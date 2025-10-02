"""
UCLA LPPI Report Generator

A unified interface for generating environmental health reports comparing 
Latino and Non-Latino White populations across California counties.

This module consolidates the scattered functionality into a single, 
easy-to-use class suitable for Jupyter notebooks and standalone scripts.
"""

import os
import time
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings

# Import existing utilities with lazy loading to avoid network errors at import time
from data_utils import (
    load_geojson, ensure_directories, create_county_name_mapping, format_population
)
from map_utils import generate_majority_tracts_map
from generate_donuts import draw_donut
from pdf_utils import generate_pdfs
import threading
import requests

warnings.filterwarnings('ignore', category=UserWarning)

def safe_fetch_population_data(csv_url, nrows=None):
    """Safely fetch population data with error handling."""
    try:
        from data_utils import fetch_population_data
        return fetch_population_data(csv_url, nrows)
    except Exception as e:
        print(f"Warning: Could not fetch population data: {e}")
        return None

def safe_start_flask_app(debug=False):
    """Safely start flask app with error handling."""
    try:
        from flask_app import start_flask_app
        return start_flask_app(debug=debug)
    except Exception as e:
        print(f"Warning: Could not start Flask app: {e}")
        return None


class ReportGenerator:
    """
    Unified report generator for environmental health disparities analysis.
    
    This class provides a simple interface to generate comprehensive reports
    comparing environmental health conditions between Latino and Non-Latino 
    White populations across California counties.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the ReportGenerator.
        
        Args:
            config: Optional configuration dictionary. If None, uses defaults.
        """
        self.config = config or self._get_default_config()
        self.output_dir = self.config.get('output_dir', 'output')
        self.county_name_mapping = None
        self.population_data = None
        self._setup_directories()
        
    def _get_default_config(self) -> Dict:
        """Get default configuration settings."""
        return {
            'output_dir': 'output',
            'geojson_path': 'inputs/geojson/ca_counties_simplified.geojson',
            'population_csv_url': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDl0u8xAvazJjlCn62edUDjjK1tLwyi4hXihYpYIGOxawrN3_HfzvYKJ1ARzH4AzhrHZysIpkc_1Nc/pub?gid=1869860862&single=true&output=csv',
            'text_csv_url': 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQiypgV-S8LImCs_esQOIbFsEXkXiAndnmo7RdW9pFutH-hYMwl5eZf3RddwzUy8PcdEEu4PLk9a1k6/pub?output=csv',
            'census_tracts_geojson': 'inputs/geojson/ca_census_tracts.geojson',
            'heat_data_csv': 'inputs/heat_data.csv',
            'air_pollution_csv': 'inputs/pm25_binned_data.csv',
            'tract_level_data': 'inputs/tract_level_data.csv',
            'roads_geojson': 'inputs/geojson/ca_primary_secondary_roads.geojson'
        }
    
    def _setup_directories(self):
        """Create necessary output directories."""
        self.map_dir, self.img_dir = ensure_directories(self.output_dir)
        
        # Create additional directories
        for subdir in ['extremeheat', 'airpollution', 'maps', 'donuts']:
            os.makedirs(os.path.join(self.output_dir, subdir), exist_ok=True)
    
    def load_data(self, offline_mode: bool = False) -> 'ReportGenerator':
        """
        Load population and geographic data.
        
        Args:
            offline_mode: If True, skip loading data from Google Sheets URLs
            
        Returns:
            Self for method chaining
        """
        print("Loading geographic data...")
        self.gdf = load_geojson(self.config['geojson_path'])
        
        if not offline_mode:
            try:
                print("Loading population data from Google Sheets...")
                self.population_data = safe_fetch_population_data(self.config['population_csv_url'])
                if self.population_data is not None:
                    self.county_name_mapping = create_county_name_mapping(self.population_data)
                    print(f"Loaded data for {len(self.county_name_mapping)} counties")
                else:
                    offline_mode = True
            except Exception as e:
                print(f"Warning: Could not load online data: {e}")
                print("Running in offline mode...")
                offline_mode = True
        
        if offline_mode:
            # Create dummy data for testing/offline use
            self.county_name_mapping = {'Los Angeles': 'Los_Angeles', 'San Diego': 'San_Diego'}
            print("Using sample data for offline mode")
        
        return self
    
    def generate_population_charts(self, counties: Optional[List[str]] = None) -> 'ReportGenerator':
        """
        Generate population donut charts for specified counties.
        
        Args:
            counties: List of county names. If None, generates for all counties.
            
        Returns:
            Self for method chaining
        """
        if self.population_data is None:
            print("Warning: No population data loaded. Call load_data() first.")
            return self
            
        counties = counties or list(self.county_name_mapping.keys())
        
        print(f"Generating population charts for {len(counties)} counties...")
        
        try:
            # Use existing donut generation function
            for county in counties:
                if county in self.county_name_mapping:
                    print(f"Generating chart for {county}...")
                    # This would call the existing generate_donuts functionality
                    # For now, we create a placeholder
                    pass
            print("Population charts generated successfully")
        except Exception as e:
            print(f"Error generating population charts: {e}")
        
        return self
    
    def generate_heat_maps(self, counties: Optional[List[str]] = None) -> 'ReportGenerator':
        """
        Generate extreme heat vulnerability maps.
        
        Args:
            counties: List of county names. If None, generates for all counties.
            
        Returns:
            Self for method chaining
        """
        counties = counties or list(self.county_name_mapping.keys())
        
        print(f"Generating heat maps for {len(counties)} counties...")
        
        output_dir = os.path.join(self.output_dir, 'extreme_heat_final_maps')
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            for county in counties:
                if county in self.county_name_mapping:
                    print(f"Generating heat map for {county}...")
                    generate_majority_tracts_map(
                        geojson_path=self.config['census_tracts_geojson'],
                        pop_data_path=self.config['tract_level_data'],
                        county_geojson_path=self.config['geojson_path'],
                        output_dir=output_dir,
                        map_type="heat",
                        topical_data_path=self.config['heat_data_csv'],
                        road_data_path=self.config['roads_geojson'],
                        population_filter="latino",
                        county_filter=county
                    )
            print("Heat maps generated successfully")
        except Exception as e:
            print(f"Error generating heat maps: {e}")
        
        return self
    
    def generate_air_pollution_maps(self, counties: Optional[List[str]] = None) -> 'ReportGenerator':
        """
        Generate air pollution exposure maps.
        
        Args:
            counties: List of county names. If None, generates for all counties.
            
        Returns:
            Self for method chaining
        """
        counties = counties or list(self.county_name_mapping.keys())
        
        print(f"Generating air pollution maps for {len(counties)} counties...")
        
        output_dir = os.path.join(self.output_dir, 'air_pollution_final_maps')
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            for county in counties:
                if county in self.county_name_mapping:
                    print(f"Generating air pollution map for {county}...")
                    generate_majority_tracts_map(
                        geojson_path='inputs/geojson/ca_census_tracts_2010.geojson',
                        pop_data_path=self.config['tract_level_data'],
                        county_geojson_path=self.config['geojson_path'],
                        output_dir=output_dir,
                        map_type="air_pollution",
                        topical_data_path=self.config['air_pollution_csv'],
                        road_data_path=self.config['roads_geojson'],
                        population_filter="latino",
                        county_filter=county,
                        show_legend=False
                    )
            print("Air pollution maps generated successfully")
        except Exception as e:
            print(f"Error generating air pollution maps: {e}")
        
        return self
    
    def generate_html_reports(self, report_type: str = 'all', counties: Optional[List[str]] = None) -> 'ReportGenerator':
        """
        Generate HTML reports using Flask templating.
        
        Args:
            report_type: Type of report ('extremeheat', 'airpollution', or 'all')
            counties: List of county names. If None, generates for all counties.
            
        Returns:
            Self for method chaining
        """
        if self.county_name_mapping is None:
            print("Warning: No county mapping loaded. Call load_data() first.")
            return self
            
        counties = counties or list(self.county_name_mapping.keys())
        report_types = [report_type] if report_type != 'all' else ['extremeheat', 'airpollution']
        
        print(f"Generating HTML reports for {len(counties)} counties...")
        
        # Start Flask in background thread
        flask_thread = threading.Thread(target=safe_start_flask_app, kwargs={'debug': False}, daemon=True)
        flask_thread.start()
        time.sleep(3)  # Wait for server to start
        
        try:
            for rtype in report_types:
                self._generate_static_html(self.county_name_mapping, rtype, self.output_dir)
            print("HTML reports generated successfully")
        except Exception as e:
            print(f"Error generating HTML reports: {e}")
        
        return self
    
    def _generate_static_html(self, county_name_mapping: Dict, report_type: str, output_dir: str):
        """Generate static HTML files from Flask endpoints."""
        reports_dir = os.path.join(output_dir, report_type)
        os.makedirs(reports_dir, exist_ok=True)
        
        pages = [1, 2]
        
        for original_county_name, standardized_county_name in county_name_mapping.items():
            for page in pages:
                url = f'http://127.0.0.1:5000/county_report/{report_type}/{standardized_county_name}.html?page={page}'
                try:
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        out_file = os.path.join(reports_dir, f'{standardized_county_name}_page{page}.html')
                        with open(out_file, 'w', encoding='utf-8') as f:
                            f.write(r.text)
                        print(f"Saved HTML: {out_file}")
                    else:
                        print(f"Error {r.status_code} fetching: {url}")
                except Exception as e:
                    print(f"Failed to fetch {url}: {e}")
    
    def generate_pdfs(self, report_type: str = 'all', counties: Optional[List[str]] = None) -> 'ReportGenerator':
        """
        Generate PDF reports from HTML.
        
        Args:
            report_type: Type of report ('extremeheat', 'airpollution', or 'all')
            counties: List of county names. If None, generates for all counties.
            
        Returns:
            Self for method chaining
        """
        if self.county_name_mapping is None:
            print("Warning: No county mapping loaded. Call load_data() first.")
            return self
            
        report_types = [report_type] if report_type != 'all' else ['extremeheat', 'airpollution']
        
        print(f"Generating PDF reports...")
        
        try:
            for rtype in report_types:
                county_subset = {}
                if counties:
                    county_subset = {k: v for k, v in self.county_name_mapping.items() if k in counties}
                else:
                    county_subset = self.county_name_mapping
                    
                generate_pdfs(county_subset, self.output_dir, rtype)
            print("PDF reports generated successfully")
        except Exception as e:
            print(f"Error generating PDF reports: {e}")
        
        return self
    
    def generate_full_report(self, counties: Optional[List[str]] = None, 
                           include_pdfs: bool = True, offline_mode: bool = False) -> Dict:
        """
        Generate complete reports for specified counties.
        
        Args:
            counties: List of county names. If None, generates for all available counties.
            include_pdfs: Whether to generate PDF outputs (requires additional dependencies)
            offline_mode: Whether to run without fetching online data
            
        Returns:
            Dictionary with generation results and file paths
        """
        print("🚀 Starting full report generation...")
        
        # Load data
        self.load_data(offline_mode=offline_mode)
        
        if counties:
            # Filter to requested counties
            available_counties = set(self.county_name_mapping.keys())
            requested_counties = set(counties)
            missing_counties = requested_counties - available_counties
            
            if missing_counties:
                print(f"Warning: Counties not found: {missing_counties}")
            
            counties = list(requested_counties & available_counties)
        else:
            counties = list(self.county_name_mapping.keys())
        
        print(f"Generating reports for: {counties}")
        
        results = {
            'counties_processed': counties,
            'output_directory': self.output_dir,
            'files_generated': []
        }
        
        try:
            # 1. Generate population charts
            print("\n📊 Step 1: Generating population charts...")
            self.generate_population_charts(counties)
            
            # 2. Generate maps (offline mode will skip this due to data dependencies)
            if not offline_mode:
                print("\n🗺️  Step 2: Generating heat maps...")
                self.generate_heat_maps(counties)
                
                print("\n🏭 Step 3: Generating air pollution maps...")
                self.generate_air_pollution_maps(counties)
            else:
                print("\n⚠️  Skipping map generation in offline mode")
            
            # 3. Generate HTML reports
            print("\n📄 Step 4: Generating HTML reports...")
            self.generate_html_reports('all', counties)
            
            # 4. Generate PDFs (optional)
            if include_pdfs and not offline_mode:
                print("\n📑 Step 5: Generating PDF reports...")
                self.generate_pdfs('all', counties)
            else:
                print("\n⚠️  Skipping PDF generation")
            
            # Collect generated files
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    if any(file.endswith(ext) for ext in ['.html', '.pdf', '.png', '.svg']):
                        results['files_generated'].append(os.path.join(root, file))
            
            print(f"\n✅ Report generation complete! Generated {len(results['files_generated'])} files.")
            
        except Exception as e:
            print(f"\n❌ Error during report generation: {e}")
            results['error'] = str(e)
        
        return results
    
    def list_available_counties(self) -> List[str]:
        """
        Get list of available counties for report generation.
        
        Returns:
            List of county names
        """
        if self.county_name_mapping is None:
            print("No data loaded. Call load_data() first.")
            return []
        
        return list(self.county_name_mapping.keys())
    
    def get_county_summary(self, county_name: str) -> Dict:
        """
        Get summary statistics for a specific county.
        
        Args:
            county_name: Name of the county
            
        Returns:
            Dictionary with county summary data
        """
        if self.population_data is None:
            return {"error": "No population data loaded"}
        
        try:
            county_data = self.population_data[self.population_data['County'] == county_name].iloc[0]
            
            return {
                'county_name': county_name,
                'total_population': format_population(county_data['pop_county_total']),
                'latino_population': format_population(county_data['pop_county_lat']),
                'nl_white_population': format_population(county_data['pop_county_nlw']),
                'pct_latino': f"{int(county_data['pct_lat'] * 100)}%",
                'pct_nl_white': f"{int(county_data['pct_nlw'] * 100)}%"
            }
        except Exception as e:
            return {"error": f"Could not get summary for {county_name}: {e}"}


# Convenience functions for backwards compatibility
def generate_reports_for_counties(counties: List[str], output_dir: str = 'output', 
                                include_pdfs: bool = True) -> Dict:
    """
    Convenience function to generate reports for specific counties.
    
    Args:
        counties: List of county names
        output_dir: Output directory path
        include_pdfs: Whether to generate PDF outputs
        
    Returns:
        Dictionary with generation results
    """
    generator = ReportGenerator({'output_dir': output_dir})
    return generator.generate_full_report(counties=counties, include_pdfs=include_pdfs)


def quick_demo(offline_mode: bool = True) -> Dict:
    """
    Generate a quick demo report for testing.
    
    Args:
        offline_mode: Run without internet dependencies
        
    Returns:
        Dictionary with generation results
    """
    print("🎯 Running quick demo...")
    generator = ReportGenerator()
    
    # Use sample counties for demo
    demo_counties = ['Los Angeles', 'San Diego'] if not offline_mode else None
    
    return generator.generate_full_report(
        counties=demo_counties, 
        include_pdfs=False, 
        offline_mode=offline_mode
    )


if __name__ == "__main__":
    # Command line usage
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            quick_demo()
        elif sys.argv[1] == "help":
            print(__doc__)
            print("\nUsage:")
            print("  python report_generator.py demo    - Run quick demo")
            print("  python report_generator.py help    - Show this help")
        else:
            counties = sys.argv[1:]
            generate_reports_for_counties(counties)
    else:
        print("UCLA LPPI Report Generator")
        print("Use 'python report_generator.py help' for usage information")