# test_pdf_utils.py
# python -m unittest test_pdf_utils.py
import unittest
import os
from pdf_utils import generate_pdfs
from data_utils import create_county_name_mapping, fetch_population_data

class PDFGenerationTestCase(unittest.TestCase):
    def setUp(self):
        # Fetch population data and create county name mapping
        csv_url = 'https://docs.google.com/spreadsheets/d/.../pub?output=csv'
        self.pop_data = fetch_population_data(csv_url)
        self.county_name_mapping = create_county_name_mapping(self.pop_data)

        # Limit to a few counties for testing
        self.county_name_mapping = dict(list(self.county_name_mapping.items())[:2])

        # Create a temporary output directory for testing
        self.output_dir = 'test_output'
        os.makedirs(self.output_dir, exist_ok=True)

    # Comment out tearDown to prevent deleting the test_output directory
    # def tearDown(self):
    #     import shutil
    #     shutil.rmtree(self.output_dir)

    def test_generate_pdfs(self):
        # Ensure the output directory is empty before the test
        import shutil
        shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)

        # Call the generate_pdfs function without mocking pdfkit
        generate_pdfs(self.county_name_mapping, self.output_dir, use_openai=False)

        # Check that PDF files were created
        pdf_files = [f for f in os.listdir(self.output_dir) if f.endswith('.pdf')]
        expected_count = len(self.county_name_mapping)
        actual_count = len(pdf_files)
        self.assertEqual(actual_count, expected_count)

        # Print the names of the generated PDF files
        print("Generated PDF files:", pdf_files)

if __name__ == '__main__':
    unittest.main()