# test_flask_app.py
# pytest-compatible tests

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
        sample_county_original = 'Alameda'  # Specify a known county from your CSV
        sample_county_standardized = self.county_name_mapping.get(sample_county_original)
        
        self.assertIsNotNone(sample_county_standardized, f"Standardized name for {sample_county_original} not found.")

        # Test the route
        response = self.app.get(f'/county_report/{sample_county_standardized}.html')
        self.assertEqual(response.status_code, 200)

        # Check for a unique string from the Alameda report, e.g., the county name
        self.assertIn(b'Alameda County', response.data)

        # Additional assertions can be added here
        # For example, verify specific data points
        # self.assertIn(b'32 yrs', response.data)  # Example for Median Age Latino