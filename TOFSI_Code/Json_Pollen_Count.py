"""
Script to extract pollen counts in JSON files.
Assumes root folder with your slide subfolders containing JSON files.

Outputs:
- Global totals for all JSON files in rootfolder.
- Per subfolder totals (per slide).
- Optional pollen locator to check where the detected pollen are located.

Script generated using AI prompts.
"""

import json
import os
from collections import Counter, defaultdict
from glob import glob

############################################################
# CONFIG
############################################################

json_root_folder = r"YOUR_JSON_ROOT_Folder"

# --- OPTIONAL LOCATOR SETTINGS ---
ENABLE_LOCATOR = True
TARGET_LABELS = ["Your", "Targeted", "Pollen"] #Pollen locator

############################################################
# FIND JSON FILES
############################################################

json_files = glob(os.path.join(json_root_folder, "**", "*.json"), recursive=True)
print(f"Found {len(json_files)} JSON files")

############################################################
# COUNTERS
############################################################

# Global
global_counter = Counter()
global_total = 0

# Per slide (folder)
folder_counters = defaultdict(Counter)
folder_totals = defaultdict(int)

# Locator
label_locations = defaultdict(lambda: defaultdict(int))

############################################################
# PROCESS FILES
############################################################

for jf in json_files:

    try:
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"⚠️ Could not read {jf}: {e}")
        continue

    if "shapes" not in data:
        continue

    # Get slide (first folder inside root)
    relative_path = os.path.relpath(jf, json_root_folder)
    slide_name = relative_path.split(os.sep)[0]

    for shape in data["shapes"]:
        label = shape.get("label", "UNKNOWN")

        # --- GLOBAL ---
        global_counter[label] += 1
        global_total += 1

        # --- PER SLIDE ---
        folder_counters[slide_name][label] += 1
        folder_totals[slide_name] += 1

        # --- LOCATOR ---
        if ENABLE_LOCATOR and label in TARGET_LABELS:
            label_locations[label][jf] += 1

############################################################
# GLOBAL SUMMARY
############################################################

print("\n==============================")
print("GLOBAL TOTALS")
print("==============================")

for label, count in global_counter.most_common():
    print(f"{label:20s} {count}")

print(f"\nTotal objects (incl. Nonpollen): {global_total}")

nonpollen = global_counter.get("Nonpollen", 0)
print(f"Pollen objects only: {global_total - nonpollen}")

############################################################
# PER SLIDE TOTALS
############################################################

print("\n==============================")
print("PER SLIDE TOTALS")
print("==============================")

for slide in sorted(folder_counters.keys()):
    print(f"\nSlide: {slide}")
    print(f"Total objects: {folder_totals[slide]}")

    nonpollen = folder_counters[slide].get("Nonpollen", 0)
    print(f"Pollen only: {folder_totals[slide] - nonpollen}")

    for label, count in folder_counters[slide].most_common():
        print(f"  {label:18s} {count}")

############################################################
# LOCATOR OUTPUT
############################################################

if ENABLE_LOCATOR:
    print("\n==============================")
    print("LOCATOR RESULTS")
    print("==============================")

    for label in TARGET_LABELS:
        hits = label_locations.get(label, {})

        print(f"\nLabel: {label}")
        print(f"JSON files with ≥1 detection: {len(hits)}")

        if len(hits) == 0:
            print("  ⚠️ No detections found.")
        else:
            for file_path, count in hits.items():
                print(f"  {os.path.basename(file_path)} → {count}")

        print(f"\nLabel: {label}")
        print(f"JSON files with ≥1 detection: {len(hits)}")

        if len(hits) == 0:
            print("  ⚠️ No detections found.")
        else:
            for file_path, count in hits.items():
                print(f"  {os.path.basename(file_path)} → {count}")