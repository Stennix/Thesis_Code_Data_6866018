"""
Script to capitalize classes in json files, e.g. change "poa" to "Poa".
Capitalization is prefered whilst training the TOFSI model.

Script generated using AI prompts
"""

import json
import os

# ROOT directory containing all training-run subfolders
ROOT_JSON_DIR = r"E:\Sten\JSON_Output"

def capitalize_labels_in_json(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed = False

    for shape in data.get("shapes", []):
        if "label" in shape and isinstance(shape["label"], str):
            new_label = shape["label"].strip().capitalize()
            if shape["label"] != new_label:
                shape["label"] = new_label
                changed = True

    if changed:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Updated: {json_path}")

def process_all_jsons(root_dir):
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(".json"):
                json_path = os.path.join(root, file)
                capitalize_labels_in_json(json_path)

process_all_jsons(ROOT_JSON_DIR)

print("Done. All JSON labels capitalized.")
