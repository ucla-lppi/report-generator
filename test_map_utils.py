import unittest
import os
from map_utils import generate_majority_tracts_map

class TestMapUtils(unittest.TestCase):

    def setUp(self):
        self.geojson_path = 'inputs/geojson/ca_census_tracts.geojson'
        self.pop_data_path = 'output/random_population_data.csv'
        self.output_dir = 'output/test_maps'
        os.makedirs(self.output_dir, exist_ok=True)

    def test_generate_majority_tracts_map(self):
        generate_majority_tracts_map(self.geojson_path, self.pop_data_path, self.output_dir)
        expected_output_file = os.path.join(self.output_dir, 'Alameda_majority_tracts_map.png')
        print(f"Expected output file: {expected_output_file}")
        print(f"Contents of output directory: {os.listdir(self.output_dir)}")
        self.assertTrue(os.path.exists(expected_output_file))

if __name__ == '__main__':
    unittest.main()