"""
Script to extract pollen counts in JSON files.

Script generated using AI prompts.
"""

import json
import os
from collections import Counter, defaultdict
from glob import glob

############################################################
# CONFIG
############################################################

json_root_folder = r"YOUR JSON FILES"

# --- OPTIONAL LOCATOR SETTINGS ---
ENABLE_LOCATOR = True          # <- set True to activate
TARGET_LABELS = ["Your","Highlighted", "Labels"]          # Use ["Art", "Bet", "..."] to print these labels seperately

############################################################
# FIND JSON FILES
############################################################

json_files = glob(os.path.join(json_root_folder, "**", "*.json"), recursive=True)
print(f"Found {len(json_files)} JSON files")

############################################################
# COUNTERS
############################################################

label_counter = Counter()
total_objects = 0

# Only used if locator is enabled
label_locations = defaultdict(lambda: defaultdict(int))
# structure: label_locations[label][json_path] = count

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

    for shape in data["shapes"]:
        label = shape.get("label", "UNKNOWN")

        # --- ORIGINAL BEHAVIOR ---
        label_counter[label] += 1
        total_objects += 1

        # --- OPTIONAL LOCATOR ---
        if ENABLE_LOCATOR and label in TARGET_LABELS:
            label_locations[label][jf] += 1

############################################################
# GLOBAL SUMMARY (UNCHANGED)
############################################################

print("\nDetected classes and counts:")
for label, count in label_counter.most_common():
    print(f"{label:20s} {count}")

print("\n==============================")
print(f"Total objects (incl. Nonpollen): {total_objects}")

nonpollen_count = label_counter.get("Nonpollen", 0)
print(f"Pollen objects only: {total_objects - nonpollen_count}")

############################################################
# LOCATOR OUTPUT (SECONDARY)
############################################################

if ENABLE_LOCATOR:
    print("\n==============================")
    print("LOCATOR RESULTS")

    for label in TARGET_LABELS:
        hits = label_locations.get(label, {})

        print(f"\nLabel: {label}")
        print(f"JSON files with ≥1 detection: {len(hits)}")

        if len(hits) == 0:
            print("  ⚠️ No detections found.")
            continue

        for jf, count in sorted(
            hits.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            print(f"  {count:3d} → {jf}")
