import json
import random
import os
import sys

# ✅ check argument
if len(sys.argv) != 2:
    print("Usage: python3 preprocess.py <input_json>")
    sys.exit(1)

INPUT_FILE = sys.argv[1]

#
PAIRS_PER_WINNER = 20

# extract filename (no directories)
base_name = os.path.basename(INPUT_FILE)

# remove .json and add suffix
output_name = base_name.replace(".json", "_pairs.json")

OUTPUT_DIR = "preprocessed_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTPUT_FILE = os.path.join(OUTPUT_DIR, output_name)

# load data
with open(INPUT_FILE) as f:
    data = json.load(f)

projects = list(data.values())

# ✅ remove errors
clean_projects = [p for p in projects if p.get("results") != "Error"]

print(f"Total projects: {len(projects)}")
print(f"After removing errors: {len(clean_projects)}")

# separate winners and losers
winners = [
    p for p in clean_projects
    if isinstance(p["results"], list) and any(r["winner"] for r in p["results"])
]

losers = [p for p in clean_projects if p not in winners]

print(f"Winners: {len(winners)}")
print(f"Losers: {len(losers)}")

# build pairs
pairs = []

for w in winners:
    sampled = random.sample(losers, min(PAIRS_PER_WINNER, len(losers)))
    for l in sampled:
        if random.random() < 0.5:
            pairs.append({
                "project_a": w,
                "project_b": l,
                "label": "A"
            })
        else:
            pairs.append({
                "project_a": l,
                "project_b": w,
                "label": "B"
            })

print(f"Generated {len(pairs)} pairs")

# save
with open(OUTPUT_FILE, "w") as f:
    json.dump(pairs, f, indent=2)

print(f"Saved to {OUTPUT_FILE}")
