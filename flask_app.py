from flask import Flask, render_template, send_from_directory, request, url_for

import os
import matplotlib.pyplot as plt
import pandas as pd
from data_utils import load_geojson, ensure_directories, fetch_population_data, create_county_name_mapping, format_population, format_as_thousands
# from openai_utils import generate_text
from text_generation import generate_case_text

app = Flask(__name__, template_folder='templates', static_folder='static')

geojson_path = 'inputs/geojson/ca_counties_simplified.geojson'
gdf = load_geojson(geojson_path)

output_dir = 'output'
map_dir, img_dir = ensure_directories(output_dir)

csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDl0u8xAvazJjlCn62edUDjjK1tLwyi4hXihYpYIGOxawrN3_HfzvYKJ1ARzH4AzhrHZysIpkc_1Nc/pub?output=csv'
pop_data = fetch_population_data(csv_url)

county_name_mapping = create_county_name_mapping(pop_data)

def build_county_report_data(standardized_county_name):
	original_county_name = next((key for key, value in county_name_mapping.items() if value == standardized_county_name), None)
	if not original_county_name:
		raise ValueError(f"No original county name for '{standardized_county_name}'")
	
	county_gdf = gdf[gdf['name'] == original_county_name]
	fig, ax = plt.subplots(1, 1, figsize=(6, 6))
	gdf.plot(ax=ax, color='white', edgecolor='gray', linewidth=0.5)
	county_gdf.plot(ax=ax, color='#005587')
	ax.set_axis_off()
	map_img_path = os.path.join(map_dir, f'{standardized_county_name}_map.png')
	plt.savefig(map_img_path, bbox_inches='tight', pad_inches=0)
	plt.close()

	data = {'Category': ['A', 'B', 'C'], 'Values': [10, 20, 30]}
	df = pd.DataFrame(data)
	plt.figure(figsize=(10, 6))
	plt.bar(df['Category'], df['Values'], color='skyblue')
	plt.title(f'{original_county_name} County Data')
	plt_path = os.path.join(img_dir, f'{standardized_county_name}_infographic.png')
	plt.savefig(plt_path)
	plt.close()

	county_pop_data = pop_data[pop_data['County'] == original_county_name].iloc[0]
	total_pop = format_population(county_pop_data['pop_county_total'])
	latino_pop = format_population(county_pop_data['pop_county_lat'])
	nlw_pop = format_population(county_pop_data['pop_county_nlw'])
	pop_county_other = format_population(county_pop_data['pop_county_other'])
	pct_latino = int(county_pop_data['pct_lat'] * 100)
	pct_nlw = int(county_pop_data['pct_nlw'] * 100)

	columns_to_check = [
		'mid_cent_90F_lat', 'mid_cent_90F_comp',
		'pct_tree_lat', 'pct_tree_comp',
		'avgDays_90F_county',
		'pct_imp_surf_lat', 'pct_imp_surf_comp',
		'pct_old_house_lat', 'pct_old_house_comp',
		'rate_heat_ed_lat', 'rate_heat_ed_comp',
		'rate_asthma_ed_lat', 'rate_asthma_ed_comp',
		'rate_cvd_ed_lat', 'rate_cvd_ed_comp',
		'pct_obesity_lat', 'pct_obesity_comp',
		'pct_diabetes_lat', 'pct_diabetes_comp',
		'pct_under_18_lat', 'pct_under_18_comp',
		'pct_over_65_lat', 'pct_over_65_comp',
		'pct_broad_lat', 'pct_broad_comp',
		'pct_dac_lat', 'pct_dac_comp'
	]

	for column in columns_to_check:
		if column not in county_pop_data:
			print(f"Warning: Column '{column}' not found in county_pop_data")

	column_values = {column: county_pop_data.get(column, 'N/A') for column in columns_to_check}

	county_statistics = {
		'Population': {
			'Total': total_pop,
			'Latino': latino_pop,
			'NL White': nlw_pop,
			'Other': pop_county_other
		},
		'Average Heat Days': {
			'County': int(round(county_pop_data['avgDays_90F_county'])),
			'Latino': int(round(county_pop_data['avgDays90F_lat'])),
			'NL White': int(round(county_pop_data['avgDays90F_comp']))
		},
		'Average Longest Heat Wave': {
			'Latino': int(round(county_pop_data['avgLong90F_lat'])),
			'NL White': int(round(county_pop_data['avgLong90F_comp']))
		},
		'Mid-Century Projections': {
			'Latino': int(round(county_pop_data['mid_cent_90F_lat'])),
			'NL White': int(round(county_pop_data['mid_cent_90F_comp']))
		},
		'Median Age': {
			'Latino': round(county_pop_data['med_age_lat']),
			'NL White': round(county_pop_data['med_age_nlw'])
		},
		'Non-U.S. Citizen Population': {
			'Latino': f"{county_pop_data['pct_non_cit_lat']}%",
			'NL White': f"{county_pop_data['pct_non_cit_nlw']}%"
		},
		'Limited English Proficiency': {
			'Latino': f"{county_pop_data['pct_lep_lat']}%",
			'NL White': f"{county_pop_data['pct_lep_nlw']}%"
		},
		'Median Household Income': {
			'Latino': f"${format_as_thousands(county_pop_data['med_inc_lat'])}",
			'NL White': f"${format_as_thousands(county_pop_data['med_inc_nlw'])}"
		},
		'Life Expectancy': {
			'Latino': f"{round(county_pop_data['life_exp_lat'])} yrs",
			'NL White': f"{round(county_pop_data['life_exp_nlw'])} yrs"
		},
		'Poverty Rate': {
			'Latino': f"{county_pop_data['pct_pov_lat']}%",
			'NL White': f"{county_pop_data['pct_pov_nlw']}%"
		},
		'No Health Insurance': {
			'Latino': f"{county_pop_data['pct_no_ins_lat']}%",
			'NL White': f"{county_pop_data['pct_no_ins_nlw']}%"
		},
		'Renter Occupied Households': {
			'Latino': f"{county_pop_data['pct_rent_lat']}%",
			'NL White': f"{county_pop_data['pct_rent_nlw']}%"
		},
		'SNAP benefits': {
			'Latino': f"{county_pop_data['pct_snap_lat']}%",
			'NL White': f"{county_pop_data['pct_snap_nlw']}%"
		},
		'Food Insecurity': {
			'Latino': f"{county_pop_data['pct_food_insecure_lat']}%",
			'NL White': f"{county_pop_data['pct_food_insecure_nlw']}%"
		},
		'Fair/Poor Health Status': {
			'Latino': f"{county_pop_data['pct_health_stat_lat']}%",
			'NL White': f"{county_pop_data['pct_health_stat_nlw']}%"
		},
		'Workers Heat Exposed':{
			'Latino': f"{round(county_pop_data['pct_broad_lat'])}%",
			'NL White': f"{round(county_pop_data['pct_broad_comp'])}%"
		},
		'Percentage of Population Under 18': {
			'Latino': f"{round(county_pop_data['pct_under_18_lat'])}%",
			'NL White': f"{round(county_pop_data['pct_under_18_comp'])}%"
		},
		'Percentage of Population Over 60': {
			'Latino': f"{round(county_pop_data['pct_over_65_lat'])}%",
			'NL White': f"{round(county_pop_data['pct_over_65_comp'])}%"
		},
		'Percentage of Population with Diabetes':{
			'Latino': f"{round(county_pop_data['pct_diabetes_lat'])}%",
			'NL White': f"{round(county_pop_data['pct_diabetes_comp'])}%"
		},
		'Percentage of Population with Obesity':{
			'Latino': f"{round(county_pop_data['pct_obesity_lat'])}%",
			'NL White': f"{round(county_pop_data['pct_obesity_comp'])}%"
		},
		'Rate Heart Attacks':{
			'Latino': f"{round(county_pop_data['rate_cvd_ed_lat'])}",
			'NL White': f"{round(county_pop_data['rate_cvd_ed_comp'])}"
		},
		'Rate Asthma':{
			'Latino': f"{round(county_pop_data['rate_asthma_ed_lat'])}",
			'NL White': f"{round(county_pop_data['rate_asthma_ed_comp'])}"
		},
		'Heat Related Emergency Department Visits':{
			'Latino': f"{round(county_pop_data['rate_heat_ed_lat'])}",
			'NL White': f"{round(county_pop_data['rate_heat_ed_comp'])}"
		},
		'Percentage Disadvantaged Communities':{
			'Latino': f"{round(county_pop_data['pct_dac_lat'])}%",
			'NL White': f"{round(county_pop_data['pct_dac_comp'])}%"
		},
		'Impervious Surfaces':{
			'Latino': f"{round(county_pop_data['pct_imp_surf_lat'])}%",
			'NL White': f"{round(county_pop_data['pct_imp_surf_comp'])}%"
		},
		'Tree Canopy':{
			'Latino': f"{round(county_pop_data['pct_tree_lat'])}%",
			'NL White': f"{round(county_pop_data['pct_tree_comp'])}%"
		},
		'Old Housing':{
			'Latino': f"{round(county_pop_data['pct_old_house_lat'])}%",
			'NL White': f"{round(county_pop_data['pct_old_house_comp'])}%"
		}
	}

	return {
		'original_county_name': original_county_name,
		'map_img_path': map_img_path,
		'plt_path': plt_path,
		'total_pop': total_pop,
		'latino_pop': latino_pop,
		'nlw_pop': nlw_pop,
		'pop_county_other': pop_county_other,
		'pct_latino': pct_latino,
		'pct_nlw': pct_nlw,
		'county_statistics': county_statistics,
		'column_values': column_values
	}

@app.route('/county_report/<report_type>/<standardized_county_name>.html')
def county_report_multi(report_type, standardized_county_name):
	try:
		page = request.args.get('page', default=1, type=int)
		report_data = build_county_report_data(standardized_county_name)
		css_url = url_for('static', filename=f'{report_type}/style.css')

		# Pick a template based on the report type and page number
		template_map = {
			'extremeheat': {
				1: 'eh-page-1/index.html',
				2: 'eh-page-2/index.html'
			},
			'airpollution': {
				1: 'ap-page-1/index.html',
				2: 'ap-page-2/index.html'
			}
		}

		template_name = template_map.get(report_type, {}).get(page)
		if not template_name:
			return f"Error: page {page} or report type {report_type} is not recognized"

		return render_template(
			template_name,
			page=str(page),
			county_name=report_data['original_county_name'],
			map_path=f'/output/maps/{standardized_county_name}_map.png',
			plt_path=f'/output/imgs/{standardized_county_name}_infographic.png',
			total_pop=report_data['total_pop'],
			latino_pop=report_data['latino_pop'],
			pop_county_other=report_data['pop_county_other'],
			nlw_pop=report_data['nlw_pop'],
			pct_latino=report_data['pct_latino'],
			pct_nlw=report_data['pct_nlw'],
			county_statistics=report_data['county_statistics'],
			column_values=report_data['column_values'],
			css_url=css_url
		)
	except Exception as e:
		import traceback
		traceback.print_exc()  # Print the full traceback for debugging
		return f"Error generating {report_type} report for '{standardized_county_name}' on page {page}: {e}"

@app.route('/output/<path:filename>')
def serve_output_file(filename):
	return send_from_directory('output', filename)

def start_flask_app(debug=False):
	app.run(debug=debug)

import math
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

import requests

# Fetch the new data
csv_url_for_text = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQiypgV-S8LImCs_esQOIbFsEXkXiAndnmo7RdW9pFutH-hYMwl5eZf3RddwzUy8PcdEEu4PLk9a1k6/pub?output=csv'
text_data = pd.read_csv(csv_url_for_text)

def classify_relationship(latino_value, comparison_value):
	if latino_value > comparison_value:
		return 'Positive'
	elif latino_value < comparison_value:
		return 'Negative'
	else:
		return 'Similar'

def generate_case_text(
	original_county_name, total_pop, latino_pop, pct_latino, nlw_pop, pct_nlw, latino_90F, nl_white_90F, latino_heat_wave, nl_white_heat_wave,
	latino_mid_cent_90F, nl_white_mid_cent_90F, latino_end_cent_90F, nl_white_end_cent_90F,
	latino_mid_cent_100F, nl_white_mid_cent_100F, latino_end_cent_100F, nl_white_end_cent_100F,
	avg_pct_under_18_latino, avg_pct_under_18_nl_white, avg_pct_over_65_latino, avg_pct_over_65_nl_white,
	text_data
):
	# Helper function to check for NaN values
	def is_nan(value):
		return math.isnan(value)

	# Check if any critical value is NaN
	critical_values = [
		total_pop, latino_pop, pct_latino, nlw_pop, pct_nlw,
		latino_90F, nl_white_90F, latino_heat_wave, nl_white_heat_wave,
		latino_mid_cent_90F, nl_white_mid_cent_90F, latino_end_cent_90F, nl_white_end_cent_90F,
		latino_mid_cent_100F, nl_white_mid_cent_100F, latino_end_cent_100F, nl_white_end_cent_100F,
		avg_pct_under_18_latino, avg_pct_under_18_nl_white, avg_pct_over_65_latino, avg_pct_over_65_nl_white
	]
	
	if any(is_nan(value) for value in critical_values):
		logging.warning(f"Skipping report for {original_county_name} County due to NaN values in critical data.")
		return f"<b>Neighborhood-Level Analysis</b><br>Data for {original_county_name} County is incomplete or invalid."

	# Convert all values to integers
	total_pop = round(total_pop)
	latino_pop = round(latino_pop)
	pct_latino = round(pct_latino)
	nlw_pop = round(nlw_pop)
	pct_nlw = round(pct_nlw)
	latino_90F = round(latino_90F)
	nl_white_90F = round(nl_white_90F)
	latino_heat_wave = round(latino_heat_wave)
	nl_white_heat_wave = round(nl_white_heat_wave)
	latino_mid_cent_90F = round(latino_mid_cent_90F)
	nl_white_mid_cent_90F = round(nl_white_mid_cent_90F)
	latino_end_cent_90F = round(latino_end_cent_90F)
	nl_white_end_cent_90F = round(nl_white_end_cent_90F)
	latino_mid_cent_100F = round(latino_mid_cent_100F)
	nl_white_mid_cent_100F = round(nl_white_mid_cent_100F)
	latino_end_cent_100F = round(latino_end_cent_100F)
	nl_white_end_cent_100F = round(nl_white_end_cent_100F)
	avg_pct_under_18_latino = round(avg_pct_under_18_latino)
	avg_pct_under_18_nl_white = round(avg_pct_under_18_nl_white)
	avg_pct_over_65_latino = round(avg_pct_over_65_latino)
	avg_pct_over_65_nl_white = round(avg_pct_over_65_nl_white)

	# Helper function to format differences
	def format_difference(diff):
		return "roughly the same amount" if abs(diff) < 1 else f"{abs(diff)} days"

	# Generate the content with conditional logic
	content = f"""
	<b>Neighborhood-Level Analysis</b><br>
	Map 1. Latino and NL White Neighborhoods in {original_county_name} County<br>
	"""

	# Add general information
	content += "At 90°F, the risk of heat-related illnesses and conditions increases significantly.<br>"
	content += "The Federal Emergency Management Agency defines a period of extreme heat in most of the U.S. as a period of 2 to 3 days above 90°F.<br>"

	# Add specific data points
	indicators = [
		("Historical Temperature, 90F", "avgDays90F_lat", "avgDays90F_comp", latino_90F, nl_white_90F),
		("Longest Period of Consecutive Days at or Above 90F", "avgLong90F_lat", "avgLong90F_comp", latino_heat_wave, nl_white_heat_wave),
		("Projected Number of Days Above 90°F by Mid-Century (2035–2064)", "mid_cent_90F_lat", "mid_cent_90F_comp", latino_mid_cent_90F, nl_white_mid_cent_90F),
		("Projected Number of Days Above 90°F by End-Century (2070–2099)", "end_cent_90F_lat", "end_cent_90F_comp", latino_end_cent_90F, nl_white_end_cent_90F),
		("Projected Number of Days Above 100°F by Mid-Century (2035–2064)", "mid_cent_100F_lat", "mid_cent_100F_comp", latino_mid_cent_100F, nl_white_mid_cent_100F),
		("Projected Number of Days Above 100°F by End-Century (2070–2099)", "end_cent_100F_lat", "end_cent_100F_comp", latino_end_cent_100F, nl_white_end_cent_100F),
		("Population age 18 or younger", "pct_under_18_lat", "pct_under_18_comp", avg_pct_under_18_latino, avg_pct_under_18_nl_white),
		("Population age 65 or older", "pct_over_65_lat", "pct_over_65_comp", avg_pct_over_65_latino, avg_pct_over_65_nl_white)
	]

	for indicator, latino_var, comp_var, latino_value, comp_value in indicators:
		relationship = classify_relationship(latino_value, comp_value)
		row = text_data[(text_data['Latino Variable Name'] == latino_var) & (text_data['Comparison Variable Name'] == comp_var) & (text_data['Type'] == relationship)]
		if not row.empty:
			copy_text = row.iloc[0]['Copy']
			copy_text = copy_text.replace("XX", str(latino_value)).replace("XX", str(comp_value))
			content += f"<b>{indicator}</b><br>{copy_text}<br>"

	return content