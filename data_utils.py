import geopandas as gpd
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use the Agg backend for matplotlib
import matplotlib.pyplot as plt
plt.switch_backend('Agg')

def load_geojson(geojson_path):
    return gpd.read_file(geojson_path)

def ensure_directories(output_dir):
    map_dir = os.path.join(output_dir, 'maps')
    img_dir = os.path.join(output_dir, 'imgs')
    os.makedirs(map_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)
    return map_dir, img_dir

def fetch_population_data(csv_url, nrows=None):
    pop_data = pd.read_csv(csv_url, nrows=nrows)
    columns_to_clean = [
        'pop', 'latino', 'nlw', 'pct_latino', 'pct_nlw',
        'latino_90F', 'nl_white_90F', 'latino_heat_wave', 'nl_white_heat_wave',
        'latino_mid.cent_90F', 'nl_white_mid.cent_90F', 'avg_pct_under_18_latino',
        'avg_pct_under_18_nl_white', 'avg_pct_over_65_latino', 'avg_pct_over_65_nl_white'
    ]

    for column in columns_to_clean:
        pop_data[column] = pop_data[column].astype(str).str.replace(',', '')

    for column in columns_to_clean:
        pop_data[column] = pd.to_numeric(pop_data[column], errors='coerce')

    return pop_data

def create_county_name_mapping(pop_data):
    return {name: name.replace(' ', '_') for name in pop_data['county_name'].unique()}