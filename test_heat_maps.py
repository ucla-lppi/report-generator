# python -m unittest test_heat_maps.py
import unittest
import os
from map_utils import generate_majority_tracts_map
test_county = ""
class TestHeatMaps(unittest.TestCase):

    def setUp(self):
        self.geojson_path = 'inputs/geojson/ca_census_tracts.geojson'
        self.ca_counties_path = 'inputs/geojson/ca_counties_simplified.geojson'
        self.pop_data_path = 'inputs/tract_level_data.csv'
        self.heat_data_path = 'inputs/heat_data.csv'
        self.output_dir = 'output/final_heat_maps'
        self.roads_path = 'inputs/geojson/ca_primary_secondary_roads.geojson'
        self.ca_counties = self.get_all_counties()
        os.makedirs(self.output_dir, exist_ok=True)
    def get_all_counties(self):
        import json
        with open(self.ca_counties_path, 'r') as f:
            data = json.load(f)
            return [feature['properties']['name'] for feature in data['features']]

    def test_generate_latino_heat_map(self):
        counties = [test_county] if test_county else self.ca_counties
        for county in counties:
            with self.subTest(county=county):
                generate_majority_tracts_map(
                    geojson_path=self.geojson_path,
                    pop_data_path=self.pop_data_path,
                    county_geojson_path=self.ca_counties_path,
                    output_dir=self.output_dir,
                    map_type="heat",
                    heat_data_path=self.heat_data_path,
                    road_data_path=self.roads_path,
                    population_filter="latino",
                    county_filter=county
                )
                expected_output_file = os.path.join(self.output_dir, "combined_maps", county + "_heat_map_combined.png")
                print(f"Expected output file: {expected_output_file}")
                print(f"Contents of output directory: {os.listdir(os.path.join(self.output_dir, 'latino'))}")
                self.assertTrue(os.path.exists(expected_output_file))
    # def test_generate_white_heat_map(self):
    #     generate_majority_tracts_map(
    #         geojson_path='inputs/geojson/ca_census_tracts.geojson',
    #         pop_data_path='inputs/tract_level_data.csv',
    #         county_geojson_path='inputs/geojson/ca_counties_simplified.geojson',
    #         output_dir='output/final_heat_maps',
    #         map_type="heat",
    #         heat_data_path='inputs/heat_data.csv',
    #         road_data_path='inputs/geojson/ca_primary_secondary_roads.geojson',
    #         county_filter='Los Angeles'  # Specify the county here
    #     )
    #     expected_output_file = os.path.join(self.output_dir, 'white', 'Alameda_heat_map.png')
        # print(f"Expected output file: {expected_output_file}")
        # print(f"Contents of output directory: {os.listdir(os.path.join(self.output_dir, 'white'))}")
        # self.assertTrue(os.path.exists(expected_output_file))

if __name__ == '__main__':
    unittest.main()