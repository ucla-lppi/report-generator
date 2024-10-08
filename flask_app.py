from flask import Flask, render_template, send_from_directory
import os
import matplotlib.pyplot as plt
import pandas as pd
from data_utils import load_geojson, ensure_directories, fetch_population_data, create_county_name_mapping
from openai_utils import generate_text

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
    original_county_name = next(key for key, value in county_name_mapping.items() if value == standardized_county_name)
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

    county_pop_data = pop_data[pop_data['county_name'] == original_county_name].iloc[0]

    # Debugging step: Print the columns of county_pop_data
    print("Available columns in county_pop_data:", county_pop_data.index.tolist())

    total_pop = round(county_pop_data['pop'] / 1_000_000, 1)
    latino_pop = round(county_pop_data['latino'] / 1_000_000, 1)
    nlw_pop = round(county_pop_data['nlw'] / 1_000_000, 1)
    pct_latino = int(county_pop_data['pct_latino'] * 100)
    pct_nlw = int(county_pop_data['pct_nlw'] * 100)
    ranking_by_latino_county = county_pop_data['ranking_by_latino_county']

    # Extract relevant columns for the prompt
    columns_to_check = [
        'latino_90F', 'nl_white_90F', 'latino_heat_wave', 'nl_white_heat_wave',
        'latino_mid.cent_90F', 'nl_white_mid.cent_90F', 'latino_end.cent_90F', 'nl_white_end.cent_90F',
        'latino_mid.cent_100F', 'nl_white_mid.cent_100F', 'latino_end.cent_100F', 'nl_white_end.cent_100F',
        'avg_pct_under_18_latino', 'avg_pct_under_18_nl_white', 'avg_pct_over_65_latino', 'avg_pct_over_65_nl_white'
    ]

    for column in columns_to_check:
        if column not in county_pop_data:
            print(f"Warning: Column '{column}' not found in county_pop_data")

    latino_90F = county_pop_data.get('latino_90F', 'N/A')
    nl_white_90F = county_pop_data.get('nl_white_90F', 'N/A')
    latino_heat_wave = county_pop_data.get('latino_heat_wave', 'N/A')
    nl_white_heat_wave = county_pop_data.get('nl_white_heat_wave', 'N/A')
    latino_mid_cent_90F = county_pop_data.get('latino_mid.cent_90F', 'N/A')
    nl_white_mid_cent_90F = county_pop_data.get('nl_white_mid.cent_90F', 'N/A')
    latino_end_cent_90F = county_pop_data.get('latino_end.cent_90F', 'N/A')
    nl_white_end_cent_90F = county_pop_data.get('nl_white_end.cent_90F', 'N/A')
    latino_mid_cent_100F = county_pop_data.get('latino_mid.cent_100F', 'N/A')
    nl_white_mid_cent_100F = county_pop_data.get('nl_white_mid.cent_100F', 'N/A')
    latino_end_cent_100F = county_pop_data.get('latino_end.cent_100F', 'N/A')
    nl_white_end_cent_100F = county_pop_data.get('nl_white_end.cent_100F', 'N/A')
    avg_pct_under_18_latino = county_pop_data.get('avg_pct_under_18_latino', 'N/A')
    avg_pct_under_18_nl_white = county_pop_data.get('avg_pct_under_18_nl_white', 'N/A')
    avg_pct_over_65_latino = county_pop_data.get('avg_pct_over_65_latino', 'N/A')
    avg_pct_over_65_nl_white = county_pop_data.get('avg_pct_over_65_nl_white', 'N/A')

    # Create a prompt for ChatGPT
    prompt = f"""
    Generate a summary for the Neighborhood-Level Analysis section for {original_county_name} County based on the following data:
    - Total Population: {total_pop} million
    - Latino Population: {latino_pop} million ({pct_latino}%)
    - Non-Latino White Population: {nlw_pop} million ({pct_nlw}%)
    - Ranking by Latino Population: {ranking_by_latino_county}
    - Average number of days with temperatures reaching 90°F (2018-2022): Latino neighborhoods: {latino_90F}, NL White neighborhoods: {nl_white_90F}
    - Average number of consecutive days with temperatures at or above 90°F in 2022: Latino neighborhoods: {latino_heat_wave}, NL White neighborhoods: {nl_white_heat_wave}
    - Projected average number of days with temperatures of 90°F or higher (2035-2064): Latino neighborhoods: {latino_mid_cent_90F}, NL White neighborhoods: {nl_white_mid_cent_90F}
    - Projected average number of days with temperatures of 90°F or higher (2070-2099): Latino neighborhoods: {latino_end_cent_90F}, NL White neighborhoods: {nl_white_end_cent_90F}
    - Projected average number of days with temperatures of 100°F or higher (2035-2064): Latino neighborhoods: {latino_mid_cent_100F}, NL White neighborhoods: {nl_white_mid_cent_100F}
    - Projected average number of days with temperatures of 100°F or higher (2070-2099): Latino neighborhoods: {latino_end_cent_100F}, NL White neighborhoods: {nl_white_end_cent_100F}
    - Percentage of residents under 18: Latino neighborhoods: {avg_pct_under_18_latino}%, NL White neighborhoods: {avg_pct_under_18_nl_white}%
    - Percentage of residents over 65: Latino neighborhoods: {avg_pct_over_65_latino}%, NL White neighborhoods: {avg_pct_over_65_nl_white}%
    """

    # Generate text using OpenAI API if enabled
    generated_text = None
    if use_openai:
        generated_text = generate_text(prompt)
        print(f"Generated text: {generated_text}")

    # Fallback text if OpenAI API fails or is not used
    if not generated_text:
        print("OpenAI API failed or not used, generating fallback text.")
        generated_text = generate_case_text(
            original_county_name, total_pop, latino_pop, pct_latino, nlw_pop, pct_nlw,
            ranking_by_latino_county, latino_90F, nl_white_90F, latino_heat_wave, nl_white_heat_wave,
            latino_mid_cent_90F, nl_white_mid_cent_90F, latino_end_cent_90F, nl_white_end_cent_90F,
            latino_mid_cent_100F, nl_white_mid_cent_100F, latino_end_cent_100F, nl_white_end_cent_100F,
            avg_pct_under_18_latino, avg_pct_under_18_nl_white, avg_pct_over_65_latino, avg_pct_over_65_nl_white
        )

    # Extract county statistics
    county_statistics = {
        'Median Age': {
            'Latino': county_pop_data['median_age_hispanic'],
            'NL White': county_pop_data['median_age_white'],
            'Total': county_pop_data['median_age_total']
        },
        'Non-U.S. Citizen Population': {
            'Latino': f"{county_pop_data['percent_hispanic_non_citizens']}%",
            'NL White': f"{county_pop_data['percent_white_non_citizens']}%",
            'Total': f"{county_pop_data['percent_total_non_citizens']}%"
        },
        'Limited English Proficiency': {
            'Latino': f"{county_pop_data['percent_hispanic_less_english']}%",
            'NL White': f"{county_pop_data['percent_white_less_english']}%",
            'Total': f"{county_pop_data['percent_total_less_english']}%"
        },
        'Median Household Income': {
            'Latino': f"${county_pop_data['median_income_hispanic']:,}",
            'NL White': f"${county_pop_data['median_income_white']:,}",
            'Total': f"${county_pop_data['median_income_total']:,}"
        },
        'Poverty Rate': {
            'Latino': f"{county_pop_data['percent_hispanic_poverty']}%",
            'NL White': f"{county_pop_data['percent_white_poverty']}%",
            'Total': f"{county_pop_data['percent_total_poverty']}%"
        },
        'No Health Insurance': {
            'Latino': f"{county_pop_data['percent_hispanic_no_insurance']}%",
            'NL White': f"{county_pop_data['percent_white_no_insurance']}%",
            'Total': f"{county_pop_data['percent_total_county_no_insurance']}%"
        },
        'Renter Occupied Households': {
            'Latino': f"{county_pop_data['percent_hispanic_renter']}%",
            'NL White': f"{county_pop_data['percent_white_renter']}%",
            'Total': f"{county_pop_data['percent_total_renter']}%"
        },
        'SNAP benefits': {
            'Latino': f"{county_pop_data['percent_hispanic_snap']}%",
            'NL White': f"{county_pop_data['percent_white_snap']}%",
            'Total': f"{county_pop_data['percent_total_snap']}%"
        },
        'Food Insecurity': {
            'Latino': f"{county_pop_data['latino_food_insecure']}%",
            'NL White': f"{county_pop_data['nl_white_food_insecure']}%",
            'Total': f"{county_pop_data['all_food_insecure']}%"
        },
        'Self-Reported Health Status (Fair or Poor)': {
            'Latino': f"{county_pop_data['latino_fair_poor']}%",
            'NL White': f"{county_pop_data['nl_white_fair_or_poor']}%",
            'Total': f"{county_pop_data['all_fair_or_poor']}%"
        }
    }

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
        generated_text=generated_text
    )
import math

import logging

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_case_text(
    original_county_name, total_pop, latino_pop, pct_latino, nlw_pop, pct_nlw,
    ranking_by_latino_county, latino_90F, nl_white_90F, latino_heat_wave, nl_white_heat_wave,
    latino_mid_cent_90F, nl_white_mid_cent_90F, latino_end_cent_90F, nl_white_end_cent_90F,
    latino_mid_cent_100F, nl_white_mid_cent_100F, latino_end_cent_100F, nl_white_end_cent_100F,
    avg_pct_under_18_latino, avg_pct_under_18_nl_white, avg_pct_over_65_latino, avg_pct_over_65_nl_white
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

    # Calculate percentage differences
    diff_90F = latino_90F - nl_white_90F
    diff_heat_wave = latino_heat_wave - nl_white_heat_wave
    diff_mid_cent_90F = latino_mid_cent_90F - nl_white_mid_cent_90F
    diff_end_cent_90F = latino_end_cent_90F - nl_white_end_cent_90F
    diff_mid_cent_100F = latino_mid_cent_100F - nl_white_mid_cent_100F
    diff_end_cent_100F = latino_end_cent_100F - nl_white_end_cent_100F
    diff_under_18 = avg_pct_under_18_latino - avg_pct_under_18_nl_white
    diff_over_65 = avg_pct_over_65_latino - avg_pct_over_65_nl_white

    # Helper function to format differences
    def format_difference(diff):
        return "roughly the same amount" if abs(diff) < 1 else f"{abs(diff)} days"

    # Generate the content with conditional logic
    content = f"""
    <b>Neighborhood-Level Analysis</b><br>
    Map 1. Latino and NL White Neighborhoods in {original_county_name} County<br>
    High-Temperature Days<br>
    The federal government defines extreme heat in the U.S. as a period of 2 to 3 days above 90 degrees Fahrenheit.
    <ul>
        <li>Latino neighborhoods historically experience {'more' if diff_90F > 0 else 'fewer'} days with high temperatures. For instance, the average number of days with temperatures reaching 90°F between 2018 and 2022 is {latino_90F} days in Latino neighborhoods compared to {nl_white_90F} days in NL White neighborhoods, representing a difference of {format_difference(diff_90F)}.</li>
        <li>Latino neighborhoods endure {'longer' if diff_heat_wave > 0 else 'shorter'} heat waves. In recent years, these neighborhoods experienced an average of {latino_heat_wave} consecutive days with temperatures at or above 90°F, while NL White neighborhoods experienced {nl_white_heat_wave} consecutive days, a difference of {format_difference(diff_heat_wave)}.</li>
    </ul>
    <br>
    Looking forward, Latino neighborhoods are projected to experience {'a greater' if diff_mid_cent_90F > 0 else 'a lesser'} number of days with higher temperatures. Between 2035 and 2064, Latino neighborhoods are expected to experience an average of {latino_mid_cent_90F} days with temperatures of 90°F or higher, while NL White neighborhoods are expected to experience {nl_white_mid_cent_90F} days, a difference of {format_difference(diff_mid_cent_90F)}. Between 2070 and 2099, Latino neighborhoods are expected to experience {latino_end_cent_90F} days with temperatures of 90°F or higher, while NL White neighborhoods are expected to experience {nl_white_end_cent_90F} days, a difference of {format_difference(diff_end_cent_90F)}.
    <br>
    Projected average number of days with temperatures of 100°F or higher:
    <ul>
        <li>Between 2035 and 2064: Latino neighborhoods: {latino_mid_cent_100F} days, NL White neighborhoods: {nl_white_mid_cent_100F} days, a difference of {format_difference(diff_mid_cent_100F)}.</li>
        <li>Between 2070 and 2099: Latino neighborhoods: {latino_end_cent_100F} days, NL White neighborhoods: {nl_white_end_cent_100F} days, a difference of {format_difference(diff_end_cent_100F)}.</li>
    </ul>
    Older adults and children are at higher risk for heat-related illnesses. On average, a higher percentage of residents in Latino neighborhoods are 18 and under ({avg_pct_under_18_latino}%) compared to predominantly NL White neighborhoods ({avg_pct_under_18_nl_white}%), a difference of {format_difference(diff_under_18)}%. However, predominantly NL White neighborhoods, on average, have a higher percentage of the elderly ({avg_pct_over_65_nl_white}%), with more residents being 65 and over, compared to Latino neighborhoods ({avg_pct_over_65_latino}%), a difference of {format_difference(diff_over_65)}%.
    """
    return content
@app.route('/output/<path:filename>')
def serve_output_file(filename):
    return send_from_directory('output', filename)

def start_flask_app(debug=False):
    app.run(debug=debug)