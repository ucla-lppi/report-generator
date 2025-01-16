# python main.py 
import os
import argparse
from threading import Timer
from data_utils import create_county_name_mapping, fetch_population_data, load_geojson, ensure_directories
from pdf_utils import generate_pdfs
from flask_app import start_flask_app
import pandas as pd

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Argument parser for command-line arguments
parser = argparse.ArgumentParser(description='Start the Flask app with optional debug mode and OpenAI usage.')
parser.add_argument('--debug', action='store_true', help='Run the Flask app in debug mode')
parser.add_argument('--use-openai', action='store_true', help='Enable the use of OpenAI API')
args = parser.parse_args()

# Ensure the directories exist
output_dir = 'output'
map_dir, img_dir = ensure_directories(output_dir)

# Load GeoJSON data
geojson_path = 'inputs/geojson/ca_counties_simplified.geojson'
gdf = load_geojson(geojson_path)

# Fetch population data (all rows)
csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDl0u8xAvazJjlCn62edUDjjK1tLwyi4hXihYpYIGOxawrN3_HfzvYKJ1ARzH4AzhrHZysIpkc_1Nc/pub?gid=1869860862&single=true&output=csv'
csv_url_for_text ='https://docs.google.com/spreadsheets/d/e/2PACX-1vQiypgV-S8LImCs_esQOIbFsEXkXiAndnmo7RdW9pFutH-hYMwl5eZf3RddwzUy8PcdEEu4PLk9a1k6/pub?output=csv'
pop_data = fetch_population_data(csv_url)
text_data = pd.read_csv(csv_url_for_text)

# Create a mapping of standardized county names to original names
county_name_mapping = create_county_name_mapping(pop_data)

if __name__ == '__main__':
    if args.use_openai:
        Timer(1, generate_pdfs, args=(county_name_mapping, output_dir, True)).start()
    else:
        Timer(1, generate_pdfs, args=(county_name_mapping, output_dir, False)).start()
    start_flask_app(debug=args.debug)