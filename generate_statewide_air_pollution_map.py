"""
Generate a one-time statewide air pollution map for California.
"""
from map_utils import generate_majority_tracts_map
import os

if __name__ == "__main__":
    geojson_path = 'inputs/geojson/ca_census_tracts_2010.geojson'
    ca_counties_path = 'inputs/geojson/ca_counties_simplified.geojson'
    pop_data_path = 'inputs/tract_level_data.csv'
    topical_data_path = 'inputs/pm25_binned_data.csv'
    output_dir = 'output/air_pollution_final_maps'
    roads_path = 'inputs/geojson/ca_primary_secondary_roads.geojson'
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, 'california_air_pollution.png')
    generate_majority_tracts_map(
        geojson_path=geojson_path,
        pop_data_path=pop_data_path,
        county_geojson_path=ca_counties_path,
        output_dir=output_dir,
        map_type="air_pollution",
        topical_data_path=topical_data_path,
        road_data_path=roads_path,
        population_filter="latino",
        county_filter='statewide',  # Statewide mode
        show_legend=True
    )
    print(f"Statewide air pollution map generated: {output_file}")
