# FILE: text_generation.py
import math
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
import pandas as pd
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