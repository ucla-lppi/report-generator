# test_flask_app.py
# python -m unittest test_flask_app.py
import unittest
from flask_app import app
from data_utils import create_county_name_mapping, fetch_population_data

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # Set up the Flask test client
        self.app = app.test_client()
        self.app.testing = True

        # Fetch population data and create county name mapping
        csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDl0u8xAvazJjlCn62edUDjjK1tLwyi4hXihYpYIGOxawrN3_HfzvYKJ1ARzH4AzhrHZysIpkc_1Nc/pub?output=csv'
        self.pop_data = fetch_population_data(csv_url)
        self.county_name_mapping = create_county_name_mapping(self.pop_data)
    
    def test_county_report_route(self):
        # Choose a sample county to test
        sample_county_original = next(iter(self.county_name_mapping.keys()))
        sample_county_standardized = self.county_name_mapping[sample_county_original]

        # Test the route
        response = self.app.get(f'/county_report/{sample_county_standardized}.html')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'County Report', response.data)  # Check if 'County Report' is in the response

        # You can add more assertions to check the content

if __name__ == '__main__':
    unittest.main()