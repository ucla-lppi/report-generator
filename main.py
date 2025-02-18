import os
import argparse
import time
import threading
from threading import Timer
from data_utils import create_county_name_mapping, fetch_population_data, load_geojson, ensure_directories
from pdf_utils import generate_pdfs
from flask_app import start_flask_app
import pandas as pd
import requests

# Shared setup: load geojson, population data, create mapping, ensure directories, etc.
output_dir = 'output'
map_dir, img_dir = ensure_directories(output_dir)
geojson_path = 'inputs/geojson/ca_counties_simplified.geojson'
gdf = load_geojson(geojson_path)
csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDl0u8xAvazJjlCn62edUDjjK1tLwyi4hXihYpYIGOxawrN3_HfzvYKJ1ARzH4AzhrHZysIpkc_1Nc/pub?gid=1869860862&single=true&output=csv'
csv_url_for_text = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQiypgV-S8LImCs_esQOIbFsEXkXiAndnmo7RdW9pFutH-hYMwl5eZf3RddwzUy8PcdEEu4PLk9a1k6/pub?output=csv'
pop_data = fetch_population_data(csv_url)
text_data = pd.read_csv(csv_url_for_text)
county_name_mapping = create_county_name_mapping(pop_data)
report_type = 'extremeheat'

def generate_static_html(county_name_mapping, report_type, output_dir, build_for_gh=False):
	reports_dir = os.path.join(output_dir, "heatreports")
	local_reports_dir = os.path.join("temp", "heatreports")
	os.makedirs(reports_dir, exist_ok=True)
	os.makedirs(local_reports_dir, exist_ok=True)

	pages = [1, 2]

	for original_county_name, standardized_county_name in county_name_mapping.items():
		for page in pages:
			url = f'http://127.0.0.1:5000/county_report/{report_type}/{standardized_county_name}.html?page={page}'
			try:
				r = requests.get(url, timeout=5)
				if r.status_code == 200:
					# For GitHub Pages, replace static asset URLs with '/report-generator/static/'
					if build_for_gh:
						updated_html = r.text.replace('href="/static/', 'href="/report-generator/static/')
						updated_html = updated_html.replace('src="/report-generator/static/', 'src="/report-generator/static/')
					else:
						# Local build: keep the original or modify to relative paths as needed.
						updated_html = r.text.replace('href="/static/', 'href="/static/')
						updated_html = updated_html.replace('src="/report-generator/static/', 'src="/report-generator/static/')
					# Write Github (or primary) output
					out_file = os.path.join(reports_dir, f'{standardized_county_name}_page{page}.html')
					with open(out_file, 'w', encoding='utf-8') as f:
						f.write(updated_html)
					print(f"Saved static HTML for {'GitHub Pages' if build_for_gh else 'local'}: {out_file}")

					# Always generate the local version (for preview/testing)
					local_out_file = os.path.join(local_reports_dir, f'{standardized_county_name}_page{page}.html')
					with open(local_out_file, 'w', encoding='utf-8') as f:
						local_html = r.text.replace('href="/static/', 'href="../static/')
						local_html = local_html.replace('src="/report-generator/static/', 'src="../static/')
						f.write(local_html)
					print(f"Saved static HTML for local export: {local_out_file}")
				else:
					print(f"Error {r.status_code} fetching: {url}")
			except Exception as e:
				print(f"Failed to fetch {url}: {e}")

	# For a local build only, generate PDFs/images.
	if not build_for_gh:
		generate_pdfs(county_name_mapping, output_dir)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Run the Flask app to serve pages, build static HTML or generate PDFs.'
	)
	parser.add_argument('--debug', action='store_true', help='Run Flask in debug mode')
	parser.add_argument('mode', nargs='?', default='serve', choices=['serve', 'build', 'build-gh', 'write-pdfs'],
						help="Choose: 'serve' to run the server, 'build' to build with local URLs (with PDFs), 'build-gh' for GitHub Pages, or 'write-pdfs' to generate PDFs only")
	args = parser.parse_args()

	if args.mode in ['build', 'build-gh']:
		# Start Flask in a background thread so that the app can serve pages for static generation.
		flask_thread = threading.Thread(target=start_flask_app, kwargs={'debug': args.debug}, daemon=True)
		flask_thread.start()
		# Wait a short time to ensure the server is up.
		time.sleep(3)
		build_for_gh = (args.mode == 'build-gh')
		generate_static_html(county_name_mapping, report_type, output_dir, build_for_gh=build_for_gh)
		print("Static HTML build complete.")
	elif args.mode == 'write-pdfs':
		generate_pdfs(county_name_mapping, output_dir)
		print("PDF generation complete.")
	else:
		start_flask_app(debug=args.debug)