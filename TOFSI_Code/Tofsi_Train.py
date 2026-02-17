"""
Training script for TOFSI training.
Slightly altered from the original given by Theuerkauf et al. (2023)
Change classes of interest based on you labeled classes.
Assumes tiff and json filesare in order, e.g. stack_001 relates to json_001
"""
import torch
import warnings
import sys
import glob
import os

warnings.simplefilter('ignore')

# Check whether CUDA is available
print("CUDA available:", torch.cuda.is_available())

# Paths
model_path = r"BASE MODEL"
tiff_path_pattern = r"PATH TO TIFF FILES"
json_path_pattern = r"PATH TO JSON FILES"
save_model_path = r"TRAINED MODEL OUTPUT"

# ===============================
# Define classes (MATCH JSON!)
# ===============================
classes_of_interest = [
    "Cor", "Aln", "Ile", "Rob", "Spo", "Pin", "Phi", "Poa", "Che",
    "Bet", "Dry", "Ole", "Pub", "Car", "Lyc", "Pic", "Pih", "For",
    "Ulm", "Spr", "Ost", "Pch", "Ace", "Rod", "Fra", "Lig", "Fag",
    "Sph", "Jug", "Glo", "Spa", "Cyp", "Hip", "Sal", "Cer", "Vit",
    "Din", "Vul", "Crc", "Tub", "Aqu", "The", "Men", "Eri", "Frx",
    "Art", "Tas", "Oen", "Gal", "Api", "Rum", "Til", "Pot", "Hyp",
    "Bra", "Cas", "Ran", "Ros", "Lan", "Asp", "Tri", "Tha", "Jac",
    "Cir", "Abi", "Abh"
] # Master Class list. Change to your own class list

classes_nonpollen = ["Nonpollen"] # Your 'debris' class
classes_lowconf = ["Ind"] # Your low confidence pollen class

# --- Pre-check dataset ---
tiff_files = sorted(glob.glob(tiff_path_pattern))
json_files = sorted(glob.glob(json_path_pattern))

print(f"Found {len(tiff_files)} TIFF images")
print(f"Found {len(json_files)} JSON files")

# Check matching JSONs
tiff_basenames = {os.path.splitext(os.path.basename(f))[0] for f in tiff_files}
json_basenames = {os.path.splitext(os.path.basename(f))[0] for f in json_files}

matching = tiff_basenames & json_basenames
missing_json = tiff_basenames - json_basenames
missing_tiff = json_basenames - tiff_basenames

print(f"Matching TIFF/JSON pairs: {len(matching)}")

if missing_json:
    print(f"Warning: {len(missing_json)} TIFF(s) have no corresponding JSON:")
    print(missing_json)

if missing_tiff:
    print(f"Warning: {len(missing_tiff)} JSON(s) have no corresponding TIFF:")
    print(missing_tiff)

if len(matching) == 0:
    print("No matching TIFF/JSON pairs found. Exiting.")
    sys.exit(1)

# Load existing model
model = torch.package.PackageImporter(model_path).load_pickle('model', 'model.pkl')
model = model.to('cpu')  # force CPU

print('Model loaded on CPU')

# ===============================
# Train the detector
# ===============================
ok = model.start_training_detector(
    imagefiles_train=[f for f in tiff_files if os.path.splitext(os.path.basename(f))[0] in matching],
    targetfiles_train=[f for f in json_files if os.path.splitext(os.path.basename(f))[0] in matching],
    classes_nonpollen=classes_nonpollen,
    epochs=10,
    lr=0.01,
    num_workers=0,
)

if not ok:
    print('Some error happened during detector training')
    sys.exit(1)

print('Detector training finished successfully')

# ===============================
# Train the classifier
# ===============================
ok = model.start_training_classifier(
    imagefiles_train=[f for f in tiff_files if os.path.splitext(os.path.basename(f))[0] in matching],
    targetfiles_train=[f for f in json_files if os.path.splitext(os.path.basename(f))[0] in matching],
    classes_of_interest=classes_of_interest,
    classes_nonpollen=classes_nonpollen,
    classes_lowconf=classes_lowconf,
    epochs=10,
    lr=0.01,
    num_workers=0,
)

if not ok:
    print('Some error happened during classifier training')
    sys.exit(1)

print('Classifier training finished successfully')

# Save the trained model
model.save(save_model_path)
print('Model saved to:', save_model_path)
