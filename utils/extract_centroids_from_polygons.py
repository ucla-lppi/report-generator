import json
from shapely.geometry import shape
import argparse

def extract_centroid_features(geojson_file):
    with open(geojson_file, 'r') as f:
        data = json.load(f)
    
    features = []
    for feature in data.get('features', []):
        # Extract and capitalize values for COUNTY and CITY from the original properties if they exist.
        orig_properties = feature.get("properties", {})
        county = orig_properties.get("COUNTY", "Unknown").capitalize()
        city = orig_properties.get("CITY", "Unknown").capitalize()
        
        polygon = shape(feature['geometry'])
        centroid = polygon.centroid
        
        point_feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [centroid.x, centroid.y]
            },
            "properties": {
                "county": county,
                "name": city
            }
        }
        features.append(point_feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract centroids from a GeoJSON file and save the output as GeoJSON features using COUNTY and CITY values."
    )
    parser.add_argument("geojson_file", nargs="?", default="inputs/geojson/ca_incorprated_cities.geojson", help="Path to the geojson file")
    parser.add_argument("--output", "-o", default="output_centroids.geojson", help="Output file to save the centroid GeoJSON")
    args = parser.parse_args()

    centroid_collection = extract_centroid_features(args.geojson_file)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(centroid_collection, f, indent=2)
    
    print(f"Saved centroid GeoJSON to {args.output}")