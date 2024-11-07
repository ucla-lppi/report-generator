# python generate_all_maps.py
import os
from map_utils import generate_majority_tracts_map

def clear_output_directory(output_dir):
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

def main():
    geojson_path = 'inputs/geojson/ca_census_tracts.geojson'
    ca_counties_path = 'inputs/geojson/clipped_california_counties.geojson'
    ca_roads_path = 'inputs/geojson/ca_primary_secondary_roads.geojson'
    pop_data_path = 'inputs/tract_level_data.csv'
    output_dir = 'output/all_maps'

    os.makedirs(output_dir, exist_ok=True)
    clear_output_directory(output_dir)

    generate_majority_tracts_map(geojson_path, pop_data_path, ca_counties_path, ca_roads_path, output_dir)

if __name__ == '__main__':
    main()