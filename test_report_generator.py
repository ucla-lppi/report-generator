#!/usr/bin/env python3
"""
Test script for the new ReportGenerator functionality.
This test can run offline and validates the basic functionality.
"""

import unittest
import tempfile
import shutil
import os
from report_generator import ReportGenerator, quick_demo

class TestReportGenerator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'output_dir': self.temp_dir,
            'geojson_path': 'inputs/geojson/ca_counties_simplified.geojson',
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_generator_initialization(self):
        """Test that ReportGenerator can be initialized."""
        generator = ReportGenerator(config=self.config)
        self.assertIsNotNone(generator)
        self.assertEqual(generator.output_dir, self.temp_dir)
    
    def test_load_data_offline(self):
        """Test loading data in offline mode."""
        generator = ReportGenerator(config=self.config)
        result = generator.load_data(offline_mode=True)
        
        # Should return self for method chaining
        self.assertEqual(result, generator)
        
        # Should have sample county mapping
        self.assertIsNotNone(generator.county_name_mapping)
        self.assertIn('Los Angeles', generator.county_name_mapping)
    
    def test_list_available_counties(self):
        """Test listing available counties."""
        generator = ReportGenerator(config=self.config)
        generator.load_data(offline_mode=True)
        
        counties = generator.list_available_counties()
        self.assertIsInstance(counties, list)
        self.assertGreater(len(counties), 0)
    
    def test_generate_population_charts_offline(self):
        """Test population chart generation in offline mode."""
        generator = ReportGenerator(config=self.config)
        generator.load_data(offline_mode=True)
        
        # Should not crash, even without real data
        result = generator.generate_population_charts(['Los Angeles'])
        self.assertEqual(result, generator)
    
    def test_directory_creation(self):
        """Test that required directories are created."""
        generator = ReportGenerator(config=self.config)
        
        # Check that output directories exist
        self.assertTrue(os.path.exists(self.temp_dir))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'maps')))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, 'imgs')))
    
    def test_quick_demo_offline(self):
        """Test the quick demo function in offline mode."""
        result = quick_demo(offline_mode=True)
        
        self.assertIsInstance(result, dict)
        self.assertIn('counties_processed', result)
        self.assertIn('output_directory', result)
        self.assertIn('files_generated', result)
    
    def test_configuration_handling(self):
        """Test custom configuration handling."""
        custom_config = {
            'output_dir': self.temp_dir,
            'custom_setting': 'test_value'
        }
        
        generator = ReportGenerator(config=custom_config)
        self.assertEqual(generator.config['custom_setting'], 'test_value')
        self.assertEqual(generator.output_dir, self.temp_dir)
    
    def test_county_summary_without_data(self):
        """Test county summary when no data is loaded."""
        generator = ReportGenerator(config=self.config)
        
        summary = generator.get_county_summary('Los Angeles')
        self.assertIn('error', summary)
    
    def test_generate_full_report_offline(self):
        """Test full report generation in offline mode."""
        generator = ReportGenerator(config=self.config)
        
        result = generator.generate_full_report(
            counties=['Los Angeles'],
            include_pdfs=False,
            offline_mode=True
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('counties_processed', result)
        self.assertEqual(result['counties_processed'], ['Los Angeles'])
        self.assertEqual(result['output_directory'], self.temp_dir)


class TestBackwardsCompatibility(unittest.TestCase):
    """Test that existing functions still work."""
    
    def test_import_existing_modules(self):
        """Test that existing modules can still be imported."""
        try:
            import data_utils
            import map_utils
            import pdf_utils
            import generate_donuts
            self.assertTrue(True)  # If we get here, imports worked
        except ImportError as e:
            self.fail(f"Failed to import existing modules: {e}")
    
    def test_existing_function_signatures(self):
        """Test that key existing functions are available."""
        from data_utils import load_geojson, ensure_directories, format_population
        from map_utils import generate_majority_tracts_map
        from generate_donuts import draw_donut
        
        # Just check that these functions exist and are callable
        self.assertTrue(callable(load_geojson))
        self.assertTrue(callable(ensure_directories))
        self.assertTrue(callable(format_population))
        self.assertTrue(callable(generate_majority_tracts_map))
        self.assertTrue(callable(draw_donut))


if __name__ == '__main__':
    print("Running ReportGenerator tests...")
    print("Note: These tests run in offline mode and don't require network connectivity.")
    
    # Run the tests
    unittest.main(verbosity=2)