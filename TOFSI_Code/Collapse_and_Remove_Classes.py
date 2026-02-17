"""
Script to cleanup JSON files, as Pollenlabeler does not allow for class removal once created.
Also collapses damaged pollen to their parent class
Collapse damaged classes to parent taxa and remove junk classes.
Labels are already capitalized as needed for TOFSI.
"""

import json
import os

# ==============================
# ROOT DIRECTORY
# ==============================
ROOT_JSON_DIR = r"YOUR_ROOT_JSON"

# ==============================
# DAMAGED → PARENT TAXA (FINAL, CAPITALIZED)
# ==============================
DAMAGED_TO_PARENT = {
    "Pcd": "Poa",
    "Pod": "Poa",
    "Cod": "Cor",
    "Uld": "Ulm",
    "Ald": "Aln",
    "Bed": "Bet",
    "Fad": "Fag",
    "Drd": "Dry",
    "Drf": "Dry",
    "Pid": "Pin",
    "Jud": "Jug",
    "Osd": "Ost",
    "Cad": "Car",
    "Fod": "For",
}

# ==============================
# JUNK / UNMODELED MORPHOTYPES (CAPITALIZED)
# ==============================
JUNK_CLASSES = {
    "Zon", "Bac", "Cys", "Bol", "Bob",
    "Kno", "Gra", "Var", "Ces", "Nie", "Ste", "Dor", "Check"
}

# ==============================
# PROCESS ALL JSON FILES
# ==============================
processed = 0
collapsed_total = 0
removed_total = 0

for root, _, files in os.walk(ROOT_JSON_DIR):
    for file in files:
        if not file.lower().endswith(".json"):
            continue

        path = os.path.join(root, file)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        new_shapes = []
        collapsed = 0
        removed = 0

        for shape in data.get("shapes", []):
            label = shape.get("label")

            # Collapse damaged → parent
            if label in DAMAGED_TO_PARENT:
                shape["label"] = DAMAGED_TO_PARENT[label]
                new_shapes.append(shape)
                collapsed += 1

            # Remove junk
            elif label in JUNK_CLASSES:
                removed += 1
                continue

            # Otherwise, leave as-is
            else:
                new_shapes.append(shape)

        data["shapes"] = new_shapes

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        processed += 1
        collapsed_total += collapsed
        removed_total += removed

        print(f"{path}: {collapsed} collapsed, {removed} removed")

print("\n=== SUMMARY ===")
print(f"JSON files processed: {processed}")
print(f"Total collapsed labels: {collapsed_total}")
print(f"Total junk removed: {removed_total}")
print("✅ Label space is now consistent.")
