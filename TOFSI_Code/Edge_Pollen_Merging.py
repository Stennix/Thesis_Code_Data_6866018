"""
Script for removing edge pollen duplicates.
Uses both boundary box size and confidence score to determine which pollen to delete.
Assumes stacks are in order, e.g. image stack 1 relates to grid position 0,0 (row 0, column 0).
If the grid is incorrect, it will only detect vertical edge duplicates, not horizontal (if stacks are placed in order)

Generated using AI Prompts
"""

import json
import glob
import os
from collections import Counter, defaultdict

# ============================================================
# CONFIG
# ============================================================
JSON_DIR = r"YOUR_JSON_FOLDER"
OUT_DIR  = r"MERGED_JSON_OUTPUT"

N_ROWS = 49 #Rows in your microscope grid
N_COLS = 16 #Columns in your microscope grid

IMG_WIDTH  = 2736 #In pixels
IMG_HEIGHT = 1824 #In pixels

EDGE_TOL     = 25
OVERLAP_FRAC = 0.30   # conservative, science-first

os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# GRID HELPERS (column-major)
# ============================================================
def stack_to_grid(stack_id):
    idx = stack_id - 1
    return idx % N_ROWS, idx // N_ROWS  # row, col

def grid_to_stack(r, c):
    return c * N_ROWS + r + 1

def neighbors(stack_id):
    r, c = stack_to_grid(stack_id)
    return {
        "top":    grid_to_stack(r-1, c) if r > 0 else None,
        "bottom": grid_to_stack(r+1, c) if r < N_ROWS-1 else None,
        "left":   grid_to_stack(r, c-1) if c > 0 else None,
        "right":  grid_to_stack(r, c+1) if c < N_COLS-1 else None,
    }

# ============================================================
# BOX HELPERS
# ============================================================
def overlap_1d(a1, a2, b1, b2):
    return max(0, min(a2, b2) - max(a1, b1))

def overlap_fraction(b1, b2, axis):
    if axis == "x":
        overlap = overlap_1d(b1[0], b1[2], b2[0], b2[2])
        denom   = min(b1[2]-b1[0], b2[2]-b2[0])
    else:
        overlap = overlap_1d(b1[1], b1[3], b2[1], b2[3])
        denom   = min(b1[3]-b1[1], b2[3]-b2[1])
    return overlap / denom if denom > 0 else 0

def near_edge(b):
    return {
        "top":    b[1] <= EDGE_TOL,
        "bottom": b[3] >= IMG_HEIGHT - EDGE_TOL,
        "left":   b[0] <= EDGE_TOL,
        "right":  b[2] >= IMG_WIDTH - EDGE_TOL,
    }

# ============================================================
# LOAD JSONS
# ============================================================
detections = []
by_stack   = defaultdict(list)

json_files = sorted(glob.glob(os.path.join(JSON_DIR, "*.json")))
print(f"JSON files found: {len(json_files)}")

for path in json_files:
    stack_id = int(os.path.basename(path).split("_")[1].split(".")[0])
    with open(path) as f:
        data = json.load(f)

    for obj in data.get("shapes", []):
        det = {
            "stack": stack_id,
            "bbox": [
                float(obj["points"][0][0]),
                float(obj["points"][0][1]),
                float(obj["points"][1][0]),
                float(obj["points"][1][1]),
            ],
            "label": obj["label"],
            "confidence": obj.get("confidence", 0.0),
            "raw": obj
        }
        detections.append(det)
        by_stack[stack_id].append(det)

print(f"Loaded {len(detections)} raw detections")

# ============================================================
# MERGE LOGIC (FINAL, SCIENTIFIC)
# ============================================================
kept        = set(id(d) for d in detections)
removed_log = []

for det in detections:
    for side, nb in neighbors(det["stack"]).items():
        if nb is None:
            continue

        for other in by_stack.get(nb, []):

            if id(det) not in kept or id(other) not in kept:
                continue

            # NEVER merge different taxa
            if det["label"] != other["label"]:
                continue

            e1 = near_edge(det["bbox"])
            e2 = near_edge(other["bbox"])

            if side == "top"    and not (e1["top"]    and e2["bottom"]): continue
            if side == "bottom" and not (e1["bottom"] and e2["top"]):    continue
            if side == "left"   and not (e1["left"]   and e2["right"]):  continue
            if side == "right"  and not (e1["right"]  and e2["left"]):   continue

            axis = "x" if side in ("top", "bottom") else "y"
            if overlap_fraction(det["bbox"], other["bbox"], axis) < OVERLAP_FRAC:
                continue

            # same grain → keep highest confidence
            if det["confidence"] >= other["confidence"]:
                kept.discard(id(other))
                removed_log.append({
                    "removed_stack": other["stack"],
                    "kept_stack": det["stack"],
                    "label": det["label"],
                    "confidence_kept": det["confidence"]
                })
            else:
                kept.discard(id(det))
                removed_log.append({
                    "removed_stack": det["stack"],
                    "kept_stack": other["stack"],
                    "label": other["label"],
                    "confidence_kept": other["confidence"]
                })

# ============================================================
# SAVE UPDATED JSONS
# ============================================================
final_by_stack = defaultdict(list)

for det in detections:
    if id(det) in kept:
        final_by_stack[det["stack"]].append(det)

for path in json_files:
    stack_id = int(os.path.basename(path).split("_")[1].split(".")[0])
    with open(path) as f:
        data = json.load(f)

    data["shapes"] = [d["raw"] for d in final_by_stack.get(stack_id, [])]

    out = os.path.join(OUT_DIR, os.path.basename(path))
    with open(out, "w") as f:
        json.dump(data, f, indent=2)

# ============================================================
# REPORT
# ============================================================
vertical   = sum(1 for r in removed_log if r["removed_stack"] - r["kept_stack"] in [-1,1] or r["removed_stack"] == r["kept_stack"])
horizontal = len(removed_log) - vertical

affected_stacks = sorted(
    set(r["removed_stack"] for r in removed_log) |
    set(r["kept_stack"] for r in removed_log)
)

print("\nMERGE SUMMARY")
print("-" * 30)
print(f"Total merges: {len(removed_log)}")
print(f"Vertical merges   : {vertical}")
print(f"Horizontal merges : {horizontal}")
print(f"Stacks affected ({len(affected_stacks)}): {affected_stacks}")

# optional: full merge log per stack without direction
print("\nFULL MERGE LOG:")
for r in removed_log:
    print(r)
