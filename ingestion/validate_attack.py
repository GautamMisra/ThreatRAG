import json


ATTACK_FILE = "data/raw/attack/enterprise-attack.json"


with open(ATTACK_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


print("JSON loaded successfully!")

objects = data["objects"]

print("Total STIX objects:", len(objects))


techniques = [
    obj
    for obj in objects
    if obj.get("type") == "attack-pattern"
]

print("Total attack-pattern objects:", len(techniques))


technique = techniques[0]


# -----------------------------
# Extract ATT&CK technique ID
# -----------------------------

attack_id = None

for ref in technique.get("external_references", []):
    if ref.get("source_name") == "mitre-attack":
        attack_id = ref.get("external_id")
        break


# -----------------------------
# Extract basic information
# -----------------------------

name = technique.get("name")
description = technique.get("description")


# -----------------------------
# Extract tactics
# -----------------------------

tactics = []

for phase in technique.get("kill_chain_phases", []):
    if phase.get("kill_chain_name") == "mitre-attack":
        tactics.append(phase.get("phase_name"))


# -----------------------------
# Display result
# -----------------------------

print("\n========== ATT&CK TECHNIQUE ==========")

print("ID:", attack_id)
print("Name:", name)

print("\nDescription:")
print(description)

print("\nTactics:")
for tactic in tactics:
    print("-", tactic)

print("=======================================")