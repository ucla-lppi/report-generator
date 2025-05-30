# python -m unittest test_air_pollution_maps.py
import unittest
import os
from map_utils import generate_majority_tracts_map

test_county = ""

class TestAirPollutionMaps(unittest.TestCase):

    def setUp(self):
        self.geojson_path = 'inputs/geojson/ca_census_tracts_2010.geojson'
        self.ca_counties_path = 'inputs/geojson/ca_counties_simplified.geojson'
        self.pop_data_path = 'inputs/tract_level_data.csv'
        self.topical_data_path = 'inputs/pm25_binned_data.csv'  # Renamed from heat_data_path
        self.output_dir = 'output/air_pollution_final_maps'
        self.roads_path = 'inputs/geojson/ca_primary_secondary_roads.geojson'
        self.ca_counties = self.get_all_counties()
        os.makedirs(self.output_dir, exist_ok=True)

    def get_all_counties(self):
        import json
        with open(self.ca_counties_path, 'r') as f:
            data = json.load(f)
            return [feature['properties']['name'] for feature in data['features']]

    def test_generate_latino_air_pollution_map(self):
        counties = [test_county] if test_county else self.ca_counties
        for county in counties:
            with self.subTest(county=county):
                generate_majority_tracts_map(
                    geojson_path=self.geojson_path,
                    pop_data_path=self.pop_data_path,
                    county_geojson_path=self.ca_counties_path,
                    output_dir=self.output_dir,
                    map_type="air_pollution",
                    topical_data_path=self.topical_data_path,  # Updated to generic name
                    road_data_path=self.roads_path,
                    population_filter="latino",
                    county_filter=county,
                    show_legend = False
                )
                expected_output_file = os.path.join(self.output_dir, county + "_air_pollution.png")
                print(f"Expected output file: {expected_output_file}")
                print(f"Contents of output directory: {os.listdir(self.output_dir)}")
                self.assertTrue(os.path.exists(expected_output_file))

if __name__ == '__main__':
    unittest.main()