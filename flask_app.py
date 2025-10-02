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

csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTyGBCxXjMIztPF1IL5JrP0nss-H4GwJwyecXDRy7Hv5oyC3s54ytPaNotzoqTMKzkPCxFqgEItfSLz/pub?gid=1869860862&single=true&output=csv'
pop_data = fetch_population_data(csv_url)

county_name_mapping = create_county_name_mapping(pop_data)

if os.getenv('GITHUB_PAGES'):
    app.config['STATIC_BASE'] = '/report-generator/static'
else:
    app.config['STATIC_BASE'] = '/static'

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
		'pct_dac_lat', 'pct_dac_comp',
		'avgPM25_state_avg', 'avgPM25_county_avg',
		'avgPM25_lat', 'avgPM25_comp',
		'dieselPM_lat', 'dieselPM_comp',
		'tox_conc_lat', 'tox_conc_comp',
		'trafficDens_lat', 'trafficDens_comp',
		'cleanupSites_lat', 'cleanupSites_comp',
		'hazFacilites_lat', 'hazFacilites_comp',
		'prox_rmp_lat', 'prox_rmp_comp',
		'pct_poverty_lat', 'pct_poverty_comp',
		'pct_walk_lat', 'pct_walk_comp',
		'pct_pub_lat', 'pct_pub_comp',
		'pct_lowBirthWght_lat', 'pct_lowBirthWght_comp',
		'pct_dac_lat', 'pct_dac_comp',
		'pct_clean_veh_lat', 'pct_clean_veh_comp',
		'pct_veh_20yrs_lat', 'pct_veh_20yrs_comp',
		'pct_asthma_lat', 'pct_asthma_comp',
		'pct_chd_lat', 'pct_chd_comp'
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
			'County': int(county_pop_data['avgDays_90F_county']),
			'Latino': int(county_pop_data['avgDays90F_lat']),
			'NL White': int(county_pop_data['avgDays90F_comp'])
		},
		'Average Longest Heat Wave': {
			'Latino': int(county_pop_data['avgLong90F_lat']),
			'NL White': int(county_pop_data['avgLong90F_comp'])
		},
		'Mid-Century Projections': {
			'Latino': int(county_pop_data['mid_cent_90F_lat']),
			'NL White': int(county_pop_data['mid_cent_90F_comp'])
		},
		'Median Age': {
			'Latino': f"{int(county_pop_data['med_age_lat'])} yrs",
			'NL White': f"{int(county_pop_data['med_age_nlw'])} yrs"
		},
		'Non-U.S. Citizen Population': {
			'Latino': f"{int(county_pop_data['pct_non_cit_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_non_cit_nlw'])}%",
		},
		'Limited English Proficiency': {
			'Latino': f"{int(county_pop_data['pct_lep_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_lep_nlw'])}%"
		},
		'Median Household Income': {
			'Latino': f"${format_as_thousands(county_pop_data['med_inc_lat'])}",
			'NL White': f"${format_as_thousands(county_pop_data['med_inc_nlw'])}"
		},
		'Percentage Asthma': {
			'Latino': f"{int(county_pop_data['pct_asthma_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_asthma_comp'])}%"
		},
		'Life Expectancy': {
			'Latino': f"{int(county_pop_data['life_exp_lat'])} yrs",
			'NL White': f"{int(county_pop_data['life_exp_nlw'])} yrs"
		},
		'Low Birth Weight Babies': {
			'Latino': f"{int(county_pop_data['pct_lowBirthWght_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_lowBirthWght_comp'])}%"
		},
		'Low Birth Weight Babies Number': {
			'Latino': county_pop_data['pct_lowBirthWght_lat'],
			'NL White': county_pop_data['pct_lowBirthWght_comp']
		},
		'Poverty Rate': {
			'Latino': f"{int(county_pop_data['pct_pov_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_pov_nlw'])}%"
		},
		'No Health Insurance': {
			'Latino': f"{int(county_pop_data['pct_no_ins_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_no_ins_nlw'])}%"
		},
		'Renter Occupied Households': {
			'Latino': f"{int(county_pop_data['pct_rent_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_rent_nlw'])}%"
		},
		'SNAP benefits': {
			'Latino': f"{int(county_pop_data['pct_snap_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_snap_nlw'])}%"
		},
		'Food Insecurity': {
			'Latino': f"{int(county_pop_data['pct_food_insecure_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_food_insecure_nlw'])}%"
		},
		'Fair/Poor Health Status': {
			'Latino': f"{int(county_pop_data['pct_health_stat_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_health_stat_nlw'])}%"
		},
		'Workers Heat Exposed': {
			'Latino': f"{int(county_pop_data['pct_broad_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_broad_comp'])}%"
		},
		'Percentage of Population Under 18': {
			'Latino': f"{int(county_pop_data['pct_under_18_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_under_18_comp'])}%"
		},
		'Percentage of Population Under 5': {
			'Latino': f"{int(county_pop_data['pct_under_5_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_under_5_comp'])}%"
		},
		'Percentage of Population Over 65': {
			'Latino': f"{int(county_pop_data['pct_over_65_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_over_65_comp'])}%"
		},
		'Percentage of Population with Diabetes': {
			'Latino': f"{int(county_pop_data['pct_diabetes_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_diabetes_comp'])}%"
		},
		'Percentage of Population with Obesity': {
			'Latino': f"{int(county_pop_data['pct_obesity_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_obesity_comp'])}%"
		},
		'Rate Heart Attacks': {
			'Latino': int(county_pop_data['rate_cvd_ed_lat']),
			'NL White': int(county_pop_data['rate_cvd_ed_comp'])
		},
		'Rate Asthma': {
			'Latino': int(county_pop_data['rate_asthma_ed_lat']),
			'NL White': int(county_pop_data['rate_asthma_ed_comp'])
		},
		'Coronary Heart Disease': {
			'Latino': f"{round(county_pop_data['pct_chd_lat'],0)}%",
			'NL White': f"{round(county_pop_data['pct_chd_comp'],0)}%"
		},
		'Heat Related Emergency Department Visits': {
			'Latino': int(county_pop_data['rate_heat_ed_lat']),
			'NL White': int(county_pop_data['rate_heat_ed_comp'])
		},
		'Percentage Disadvantaged Communities': {
			'Latino': f"{round(int(county_pop_data['pct_dac_lat']),0)}%",
			'NL White': f"{round(int(county_pop_data['pct_dac_comp']),0)}%"
		},
		'Percentage of Clunker Vehicles': {
			'Latino': f"{county_pop_data['pct_veh_20yrs_lat']}%",
			'NL White': f"{county_pop_data['pct_veh_20yrs_comp']}%"
		},
		'Impervious Surfaces': {
			'Latino': f"{int(county_pop_data['pct_imp_surf_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_imp_surf_comp'])}%"
		},
		'Tree Canopy': {
			'Latino': f"{int(county_pop_data['pct_tree_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_tree_comp'])}%"
		},
		'Old Housing': {
			'Latino': f"{int(county_pop_data['pct_old_house_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_old_house_comp'])}%"
		},
		'Disadvantaged Communities': {
			'Latino': f"{county_pop_data['pct_dac_lat']}%",
			'NL White': f"{county_pop_data['pct_dac_comp']}%"
		},
		'Low Electric Vehicle Adoption': {
			'Latino': f"{int(county_pop_data['pct_clean_veh_lat'])}%",
			'NL White': f"{int(county_pop_data['pct_clean_veh_comp'])}%"
		},
		'Traffic Density': {
			'Latino': int(county_pop_data['trafficDens_lat']),
			'NL White': int(county_pop_data['trafficDens_comp'])
		},
		'Cleanup Sites': {
			'Latino': int(county_pop_data['cleanupSites_lat']),
			'NL White': int(county_pop_data['cleanupSites_comp'])
		},
		'RMP Proximity': {
			'Latino': county_pop_data['prox_rmp_lat'],
			'NL White': county_pop_data['prox_rmp_comp']
		},
		'Hazardous Facilities': {
			'Latino': county_pop_data['hazFacilites_lat'],
			'NL White': county_pop_data['hazFacilites_comp']
		},
		'Average PM2.5': {
			'County': county_pop_data['avgPM25_county_avg'],
			'State': county_pop_data['avgPM25_state_avg'],
			'Latino': county_pop_data['avgPM25_lat'],
			'NL White': county_pop_data['avgPM25_comp']
		},
		'Diesel PM': {
			'Latino': county_pop_data['dieselPM_lat'],
			'NL White': county_pop_data['dieselPM_comp']
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

@app.context_processor
def inject_static_base():
    return dict(static_base=app.config.get('STATIC_BASE'))

@app.route('/county_report/<report_type>/<standardized_county_name>.html')
def county_report_multi(report_type, standardized_county_name):
	try:
		page = request.args.get('page', default=1, type=int)
		report_data = build_county_report_data(standardized_county_name)
		css_url = url_for('static', filename=f'{report_type}/style.css')

		# Pick a template based on the report type and page number
		template_map = {
			'extremeheat': {
				1: 'extreme-heat-page-1/index.html',
				2: 'extreme-heat-page-2/index.html'
			},
			'airpollution': {
				1: 'air-pollution-page-1/index.html',
				2: 'air-pollution-page-2/index.html'
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
from text_generation import load_text_data

# Load text data with error handling
try:
    text_data = load_text_data()
except Exception as e:
    logging.warning(f"Could not load text data in flask_app: {e}")
    text_data = None

def classify_relationship(latino_value, comparison_value):
	if latino_value > comparison_value:
		return 'Positive'
	elif latino_value < comparison_value:
		return 'Negative'
	else:
		return 'Similar'

