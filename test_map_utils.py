import unittest
import os
import geopandas as gpd
from map_utils import generate_majority_tracts_map

class TestMapUtils(unittest.TestCase):

    def setUp(self):
        self.geojson_path = 'inputs/geojson/ca_census_tracts.geojson'
        self.ca_counties_path = 'inputs/geojson/clipped_california_counties_simplified.geojson'
        self.ca_roads_path = 'inputs/geojson/ca_primary_secondary_roads.geojson'
        self.pop_data_path = 'inputs/tract_level_data.csv'
        self.output_dir = 'output/test_maps'

        os.makedirs(self.output_dir, exist_ok=True)

    def test_generate_majority_tracts_map(self):
        generate_majority_tracts_map(
            self.geojson_path, 
            self.pop_data_path, 
            self.ca_counties_path, 
            road_data_path=self.ca_roads_path, 
            output_dir=self.output_dir
        )
        
        # Load the GeoJSON file to get the list of counties
        counties_gdf = gpd.read_file(self.ca_counties_path)
        counties = counties_gdf['name'].unique()
        
        missing_files = []
        for county in counties:
            expected_output_file = os.path.join(self.output_dir, f'{county}_majority_tracts_map.png')
            if not os.path.exists(expected_output_file):
                missing_files.append(expected_output_file)
        
        if missing_files:
            print(f"Missing output files: {missing_files}")
        
        self.assertTrue(len(missing_files) == 0, f"Some maps were not generated: {missing_files}")

if __name__ == '__main__':
    unittest.main()