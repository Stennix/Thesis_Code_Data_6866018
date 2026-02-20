"""
Detection script for the TOFSI model.
Slightly altered from the original given by Theuerkauf et al. (2023)
Pollen image output is disabled but can be reactivated if necessary.
"""

###############################################################################
### inputs
###############################################################################

root_directory = r"MULTITIFF PATH"
output_directory = r"DETECTION OUTPUT"
pthModel = r"USED MODEL"

###############################################################################
### imports and setup
###############################################################################

import torch
import warnings
warnings.simplefilter('ignore')
import json
import os
import zipfile
import shutil
import tifffile as tf
from glob import glob
import sys

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

###############################################################################
### load model
###############################################################################

model = torch.package.PackageImporter(pthModel).load_pickle(
    'model', 'model.pkl', map_location=torch.device('cpu')
)

###############################################################################
### extract class list
###############################################################################

destination_path = os.path.dirname(pthModel)
file_to_extract = 'class_list.txt'
subdirectory = os.path.splitext(os.path.basename(pthModel))[0] + '/' + 'model'

with zipfile.ZipFile(pthModel, 'r') as zip_ref:
    file_list = zip_ref.namelist()
    subdirectory_exists = any(file.startswith(f"{subdirectory}/") for file in file_list)
    
    if subdirectory_exists:
        file_to_extract_path = f"{subdirectory}/{file_to_extract}"
        if file_to_extract_path in file_list:
            extracted_file_path = zip_ref.extract(file_to_extract_path)
            destination_file_path = os.path.join(destination_path, file_to_extract)
            shutil.copy(extracted_file_path, destination_file_path)
            os.remove(extracted_file_path)
        else:
            print('class file missing')
    else:
        print('class file missing')

# read classes
file_path = os.path.join(destination_path, file_to_extract)
try:
    with open(file_path, "r") as file:
        taxalist = tuple(file.read().splitlines())
except FileNotFoundError:
    print(f"The file '{file_path}' does not exist.")
except Exception as e:
    print(f"An error occurred {e}")

###############################################################################
### JSON template
###############################################################################

LABELME_SHAPE_TEMPLATE = {
    "label": "???",
    "line_color": None,
    "fill_color": None,
    "points": [[0.0, 0.0], [0.0, 0.0]],
    "confidence": "rectangle",
    "flags": {},
}

def result_to_json(result):
    shapes = []
    for box, label, confidence in zip(
        result['boxes'],
        result['labels'],
        list(result['cls_scores'].max(axis=1))
    ):
        shape = dict(LABELME_SHAPE_TEMPLATE)
        shape['label'] = label
        shape['confidence'] = float(confidence)
        shape['points'] = [box[:2].tolist(), box[2:].tolist()]
        shapes.append(shape)

    return json.dumps({
        "flags": {},
        "shapes": shapes,
        "lineColor": [0, 255, 0, 128],
        "fillColor": [255, 0, 0, 128],
        "imagePath": "",
        "imageData": None
    }, indent=2)

###############################################################################
### detection function (JSON OUTPUT ONLY)
###############################################################################

def detect(pthSample, pthJSON):
    """Run detection on all TIFFs in a folder and save JSONs only."""
    os.makedirs(pthJSON, exist_ok=True)
    img_list = glob(os.path.join(pthSample, "*.tif"))
    n = len(img_list)

    for i, img in enumerate(img_list):
        result = model.process_image(img)
        fnImg = os.path.basename(img)
        fnBase = os.path.splitext(fnImg)[0]
        fnJSON = os.path.join(pthJSON, fnBase + '.json')

        with open(fnJSON, 'w') as f:
            f.write(result_to_json(result))

        op = f"detecting progress: {round(100 * i / n, 1)}%"
        sys.stdout.write("\r" + op)
        sys.stdout.flush()

    print("\nDetection finished!")

###############################################################################
### full extraction and cropping (DISABLED – JSON ONLY)
###############################################################################

def extract_pollen_stacks(root_dir, output_dir):
    """
    Detect pollen and save JSONs only.
    Cropping and TIFF writing are intentionally disabled.
    """
    folders_to_process = []

    # check if root_dir itself contains TIFFs
    if any(f.endswith(".tif") for f in os.listdir(root_dir)):
        folders_to_process.append((root_dir, os.path.basename(root_dir)))
    else:
        # add subfolders ending with '_stacks'
        for folder_name in os.listdir(root_dir):
            folder_path = os.path.join(root_dir, folder_name)
            if os.path.isdir(folder_path):
                stacks_folder_name = f"{folder_name}_stacks"
                stacks_folder_path = os.path.join(folder_path, stacks_folder_name)
                if os.path.exists(stacks_folder_path) and os.path.isdir(stacks_folder_path):
                    folders_to_process.append((stacks_folder_path, folder_name))

    for stack_folder, folder_output_name in folders_to_process:
        output_folder_path = os.path.join(output_dir, folder_output_name)
        os.makedirs(output_folder_path, exist_ok=True)
        print(f"Detecting pollen in {stack_folder}")

        # JSON detection (ACTIVE)
        detect(stack_folder, output_folder_path)

        # =====================================================================
        # IMAGE CROPPING & TIFF SAVING – DISABLED ON PURPOSE
        #
        # Reason:
        # - Cropped TIFF stacks are irreversible
        # - JSONs preserve full reproducibility
        # - Cropping should be a downstream, optional step
        #
        # To re-enable:
        #   Remove the comment markers below ONLY if physical TIFF output
        #   is explicitly required.
        # =====================================================================

        # stack_counter = 1
        # for filename in os.listdir(stack_folder):
        #     if filename.endswith(".tif"):
        #         stack_number = os.path.splitext(filename)[0]
        #         json_filename = os.path.join(output_folder_path, f"{stack_number}.json")
        #
        #         if not os.path.exists(json_filename):
        #             continue
        #
        #         with open(json_filename, 'r') as json_file:
        #             data = json.load(json_file)
        #
        #         image_stack_path = os.path.join(stack_folder, filename)
        #         image_stack = tf.imread(image_stack_path)
        #
        #         for shape in data['shapes']:
        #             points = shape['points']
        #             x1, y1 = map(int, points[0])
        #             x2, y2 = map(int, points[1])
        #
        #             cropped_box = image_stack[:, y1:y2, x1:x2]
        #
        #             cropped_stack_name = f"pollen_{stack_counter}.tif"
        #             cropped_stack_path = os.path.join(output_folder_path, cropped_stack_name)
        #
        #             tf.imwrite(cropped_stack_path, cropped_box)
        #             stack_counter += 1

        print(f"JSON-only processing for {folder_output_name} done.\n")

###############################################################################
### main execution
###############################################################################

if __name__ == "__main__":
    os.makedirs(output_directory, exist_ok=True)
    extract_pollen_stacks(root_directory, output_directory)
    print("\nAll stacks processed successfully (JSON only).")
