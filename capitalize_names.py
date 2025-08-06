import json

input_path = "inputs/geojson/ca_incorprated_cities.geojson"
output_path = "inputs/geojson/ca_incorprated_cities_capitalized.geojson"

def proper_case(name):
    # Handles "Mc", "O'", "St.", etc. if needed, but for most cities .title() is sufficient
    return name.title()

with open(input_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for feature in data.get("features", []):
    props = feature.get("properties", {})
    if "name" in props and isinstance(props["name"], str):
        props["name"] = proper_case(props["name"])

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Capitalized city names written to {output_path}")