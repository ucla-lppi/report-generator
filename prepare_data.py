import os
import pandas as pd
from data_utils import create_county_name_mapping, fetch_population_data, ensure_directories
from generate_donuts import draw_donut

# Ensure the directories exist
output_dir = 'output/imgs/charts/population_donut'
os.makedirs(output_dir, exist_ok=True)

# Fetch population data (all rows)
csv_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDl0u8xAvazJjlCn62edUDjjK1tLwyi4hXihYpYIGOxawrN3_HfzvYKJ1ARzH4AzhrHZysIpkc_1Nc/pub?gid=1869860862&single=true&output=csv'
pop_data = fetch_population_data(csv_url)

# Create a mapping of standardized county names to original names
county_name_mapping = create_county_name_mapping(pop_data)

# Generate donut charts for each county
for original_county_name, standardized_county_name in county_name_mapping.items():
    total_population = pop_data[pop_data['County'] == original_county_name]['pop_county_total'].values[0]
    county_data = {
        'Latino': (pop_data[pop_data['County'] == original_county_name]['pop_county_lat'].values[0] / total_population) * 100,
        'NL White': (pop_data[pop_data['County'] == original_county_name]['pop_county_nlw'].values[0] / total_population) * 100,
        'Other': (pop_data[pop_data['County'] == original_county_name]['pop_county_other'].values[0] / total_population) * 100,
        'Total': total_population
    }
    draw_donut(county_data, standardized_county_name, output_dir)

print("All donut charts generated and saved.")