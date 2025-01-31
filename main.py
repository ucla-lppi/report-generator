import os
import argparse
from threading import Timer
from data_utils import create_county_name_mapping, fetch_population_data, load_geojson, ensure_directories
from pdf_utils import generate_pdfs
from flask_app import start_flask_app
import pandas as pd
import requests

# Load environment variables from .env file
# from dotenv import load_dotenv
# load_dotenv()

# Argument parser for command-line arguments
parser = argparse.ArgumentParser(description='Start the Flask app with optional debug mode and OpenAI usage.')
parser.add_argument('--debug', action='store_true', help='Run the Flask app in debug mode')
# parser.add_argument('--use-openai', action='store_true', help='Enable the use of OpenAI API')
args = parser.parse_args()

# Ensure the directories exist
output_dir = 'output'
map_dir, img_dir = ensure_directories(output_dir)

# Load GeoJSON data
geojson_path = 'inputs/geojson/ca_counties_simplified.geojson'
gdf = load_geojson(geojson_path)

# Fetch population data (all rows)
csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDl0u8xAvazJjlCn62edUDjjK1tLwyi4hXihYpYIGOxawrN3_HfzvYKJ1ARzH4AzhrHZysIpkc_1Nc/pub?gid=1869860862&single=true&output=csv'
csv_url_for_text = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQiypgV-S8LImCs_esQOIbFsEXkXiAndnmo7RdW9pFutH-hYMwl5eZf3RddwzUy8PcdEEu4PLk9a1k6/pub?output=csv'
pop_data = fetch_population_data(csv_url)
text_data = pd.read_csv(csv_url_for_text)

# Create a mapping of standardized county names to original names
county_name_mapping = create_county_name_mapping(pop_data)
def generate_static_html(county_name_mapping, report_type, output_dir):
	reports_dir = os.path.join(output_dir, "heatreports")
	os.makedirs(reports_dir, exist_ok=True)

	report_types = ['extremeheat', 'airpollution']
	pages = [1, 2]

	for original_county_name, standardized_county_name in county_name_mapping.items():
		for page in pages:
			url = f'http://127.0.0.1:5000/county_report/{report_type}/{standardized_county_name}.html?page={page}'
			try:
				r = requests.get(url, timeout=5)
				if r.status_code == 200:
					out_file = os.path.join(reports_dir, f'{standardized_county_name}_page{page}.html')
					with open(out_file, 'w', encoding='utf-8') as f:
						updated_html = r.text.replace('href="/static/', 'href="/report-generator/static/')
						updated_html = updated_html.replace('src="/static/', 'src="/report-generator/static/')
						f.write(updated_html)
					print(f"Saved static HTML: {out_file}")
				else:
					print(f"Error {r.status_code} fetching: {url}")
			except Exception as e:
				print(f"Failed to fetch {url}: {e}")
				
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Run the Flask app and optionally generate static HTML.')
	parser.add_argument('--debug', action='store_true', help='Run Flask in debug mode')
	args = parser.parse_args()

	output_dir = 'output'
	# report_types = ['extremeheat', 'airpollution']
	report_type = 'extremeheat'
	map_dir, img_dir = ensure_directories(output_dir)
	geojson_path = 'inputs/geojson/ca_counties_simplified.geojson'
	gdf = load_geojson(geojson_path)
	csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDl0u8xAvazJjlCn62edUDjjK1tLwyi4hXihYpYIGOxawrN3_HfzvYKJ1ARzH4AzhrHZysIpkc_1Nc/pub?gid=1869860862&single=true&output=csv'
	csv_url_for_text = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQiypgV-S8LImCs_esQOIbFsEXkXiAndnmo7RdW9pFutH-hYMwl5eZf3RddwzUy8PcdEEu4PLk9a1k6/pub?output=csv'
	pop_data = fetch_population_data(csv_url)
	text_data = pd.read_csv(csv_url_for_text)
	county_name_mapping = create_county_name_mapping(pop_data)

	# Wait until Flask is up, then generate static HTML
	Timer(1, generate_static_html, args=(county_name_mapping, report_type,output_dir)).start()
	start_flask_app(debug=args.debug)