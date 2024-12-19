from flask import Flask, render_template, send_from_directory
import os
import matplotlib.pyplot as plt
import pandas as pd
from data_utils import load_geojson, ensure_directories, fetch_population_data, create_county_name_mapping
from openai_utils import generate_text
from text_generation import generate_case_text

app = Flask(__name__, 
            template_folder='template', 
            static_folder='static')

geojson_path = 'inputs/geojson/ca_counties_simplified.geojson'
gdf = load_geojson(geojson_path)

output_dir = 'output'
map_dir, img_dir = ensure_directories(output_dir)

csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDl0u8xAvazJjlCn62edUDjjK1tLwyi4hXihYpYIGOxawrN3_HfzvYKJ1ARzH4AzhrHZysIpkc_1Nc/pub?output=csv'
pop_data = fetch_population_data(csv_url)

county_name_mapping = create_county_name_mapping(pop_data)
@app.route('/county_report/<standardized_county_name>.html')
def county_report(standardized_county_name, use_openai=False):
    try:
        original_county_name = next((key for key, value in county_name_mapping.items() if value == standardized_county_name), None)
        
        if original_county_name is None:
            print(f"Error: Original county name not found for standardized county name '{standardized_county_name}'")
            return f"Error: Original county name not found for standardized county name '{standardized_county_name}'"
    
        print(f"Generating report for {original_county_name} County")
        print(f"Checking to see if gdf[name] == original_county_name")
        print(f"gdf[name] == original_county_name: {gdf['name'] == original_county_name}")
    
        county_gdf = gdf[gdf['name'] == original_county_name]
    
        # Generate the map highlighting the specific county
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))  # Adjust the size as needed
        gdf.plot(ax=ax, color='white', edgecolor='gray', linewidth=0.5)
        county_gdf.plot(ax=ax, color='#005587')  # UCLA blue
        ax.set_axis_off()  # Remove the axis
        map_img_path = os.path.join(map_dir, f'{standardized_county_name}_map.png')
        plt.savefig(map_img_path, bbox_inches='tight', pad_inches=0)
        plt.close()
    
        # Generate infographics
        # Example: Create a simple bar chart
        data = {'Category': ['A', 'B', 'C'], 'Values': [10, 20, 30]}
        df = pd.DataFrame(data)
        plt.figure(figsize=(10, 6))
        plt.bar(df['Category'], df['Values'], color='skyblue')
        plt.title(f'{original_county_name} County Data')
        plt.xlabel('Category')
        plt.ylabel('Values')
        plt_path = os.path.join(img_dir, f'{standardized_county_name}_infographic.png')
        plt.savefig(plt_path)
        plt.close()
    
        county_pop_data = pop_data[pop_data['County'] == original_county_name].iloc[0]
    
        # Debugging step: Print the columns of county_pop_data
        print("Available columns in county_pop_data:", county_pop_data.index.tolist())
    
        total_pop = round(county_pop_data['pop_county_total'] / 1_000_000, 1)
        latino_pop = round(county_pop_data['pop_county_lat'] / 1_000_000, 1)
        nlw_pop = round(county_pop_data['pop_county_nlw'] / 1_000_000, 1)
        pct_latino = int(county_pop_data['pct_lat'] * 100)
        pct_nlw = int(county_pop_data['pct_nlw'] * 100)
    
        # Check if 'ranking_by_latino_county' exists in the DataFrame
        if 'ranking_by_latino_county' in county_pop_data:
            ranking_by_latino_county = county_pop_data['ranking_by_latino_county']
        else:
            ranking_by_latino_county = 'N/A'  # Provide a default value or handle accordingly
    
        # Extract relevant columns for the prompt
        columns_to_check = [
            'mid_cent_90F_lat', 'mid_cent_90F_comp',
            'pct_tree_lat', 'pct_tree_comp',
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
    
        # Extract values for the columns
        column_values = {column: county_pop_data.get(column, 'N/A') for column in columns_to_check}
    
        # Extract county statistics
        county_statistics = {
            'Median Age': {
                'Latino': county_pop_data['med_age_lat'],
                'NL White': county_pop_data['med_age_nlw']
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
                'Latino': f"${county_pop_data['med_inc_lat']:,}",
                'NL White': f"${county_pop_data['med_inc_nlw']:,}"
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
            'Self-Reported Health Status (Fair or Poor)': {
                'Latino': f"{county_pop_data['pct_health_stat_lat']}%",
                'NL White': f"{county_pop_data['pct_health_stat_nlw']}%"
            }
        }
    
        # Define generated_text
        generated_text = "This is a placeholder for the generated text."
    
        return render_template(
            'template.html',
            county_name=original_county_name,
            map_path=f'/output/maps/{standardized_county_name}_map.png',
            plt_path=f'/output/imgs/{standardized_county_name}_infographic.png',
            total_pop=total_pop,
            latino_pop=latino_pop,
            nlw_pop=nlw_pop,
            pct_latino=pct_latino,
            pct_nlw=pct_nlw,
            ranking_by_latino_county=ranking_by_latino_county,
            county_statistics=county_statistics,
            column_values=column_values,
            generated_text=generated_text
        )
    except Exception as e:
        import traceback
        traceback.print_exc()  # Print the full traceback for debugging
        print(f"Error generating report for {standardized_county_name}: {e}")
        return f"Error generating report for {standardized_county_name}: {e}"

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
    original_county_name, total_pop, latino_pop, pct_latino, nlw_pop, pct_nlw,
    ranking_by_latino_county, latino_90F, nl_white_90F, latino_heat_wave, nl_white_heat_wave,
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
        total_pop, latino_pop, pct_latino, nlw_pop, pct_nlw, ranking_by_latino_county,
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
    ranking_by_latino_county = round(ranking_by_latino_county)
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
