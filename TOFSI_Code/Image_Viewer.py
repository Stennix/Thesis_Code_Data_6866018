"""
#Costum Viewer script for loading in (multi)tiff images in combination with a .json file, based on the labelme-format
#Partially generated using AI-prompts, requires alterations if your file are shaped or formatted differently.
"""

import os
import cv2
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import tifffile

# ===== CONFIG =====
tiff_folder = r"YOUR_TIFF_IMAGE_FOLDER"
json_folder = r"YOUR_JSON_FOLDER"

# ===== FILE LISTS =====
tiff_files = sorted([f for f in os.listdir(tiff_folder) if f.lower().endswith((".tif", ".tiff"))])
json_files = sorted([f for f in os.listdir(json_folder) if f.lower().endswith(".json")])
json_dict = {os.path.splitext(f)[0]: f for f in json_files}

# ===== STATE =====
index = 0
total = len(tiff_files)
fig, ax = plt.subplots(figsize=(12, 12))
im = None
rect_patches = []
text_patches = []

# ===== LOAD SINGLE IMAGE =====
def load_image(idx):
    fname = tiff_files[idx]
    base = os.path.splitext(fname)[0]
    path = os.path.join(tiff_folder, fname)
    img_stack = tifffile.imread(path)

    # Handle 4D/3D arrays
    if img_stack.ndim == 4:  # multi-page RGB
        middle_index = img_stack.shape[0] // 2
        img = img_stack[middle_index]
    elif img_stack.ndim == 3:
        if img_stack.shape[2] in [3,4]:  # single RGB
            img = img_stack
        else:  # grayscale stack
            middle_index = img_stack.shape[0] // 2
            img = img_stack[middle_index]
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    else:  # single grayscale
        img = cv2.cvtColor(img_stack, cv2.COLOR_GRAY2RGB)
    return img, base

# ===== DISPLAY =====
def show_image(idx):
    global im, rect_patches, text_patches
    img, base = load_image(idx)

    # Clear old rectangles and text
    for r in rect_patches: r.remove()
    for t in text_patches: t.remove()
    rect_patches.clear()
    text_patches.clear()

    if im is None:
        im = ax.imshow(img)
    else:
        im.set_data(img)
    ax.set_title(f"{idx+1}/{total}: {tiff_files[idx]}", fontsize=14)

    # JSON overlay
    if base in json_dict:
        path = os.path.join(json_folder, json_dict[base])
        with open(path) as f:
            data = json.load(f)
        for shape in data.get("shapes", []):
            x0, y0 = shape["points"][0]
            x1, y1 = shape["points"][1]
            rect = patches.Rectangle((x0, y0), x1-x0, y1-y0, linewidth=2, edgecolor='r', facecolor='none')
            txt = ax.text(x0, y0-5, shape["label"], color='yellow', fontsize=12, weight='bold')
            ax.add_patch(rect)
            rect_patches.append(rect)
            text_patches.append(txt)

    fig.canvas.draw_idle()

# ===== KEY HANDLER =====
def on_key(event):
    global index
    if event.key == 'right':
        if index < total - 1:
            index += 1
            show_image(index)
    elif event.key == 'left':
        if index > 0:
            index -= 1
            show_image(index)
    elif event.key == 'escape':
        plt.close('all')

fig.canvas.mpl_connect('key_press_event', on_key)

# ===== START =====
show_image(index)
print("Use Right/Left arrows to navigate, Esc to quit.")
plt.show()  # blocking call, works in terminal/Qt5 GUI
