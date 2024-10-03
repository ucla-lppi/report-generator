import geopandas as gpd
import pandas as pd
import numpy as np
import os

# Load GeoJSON data
geojson_path = 'inputs/geojson/ca_census_tracts.geojson'
gdf = gpd.read_file(geojson_path)

# Print the columns to inspect the available fields
print(gdf.columns)

# Define urban counties
urban_counties = ['San Francisco County', 'Los Angeles County', 'Santa Clara County']

# Generate random population data with varying ranges
np.random.seed(42)  # For reproducibility

# Function to generate random populations based on county type
def generate_population(county_name):
    if county_name in urban_counties:
        total_population = np.random.randint(5000, 50000)
        latino_population = np.random.randint(1000, 20000)
        white_population = np.random.randint(1000, 20000)
    else:
        total_population = np.random.randint(500, 10000)
        latino_population = np.random.randint(100, 5000)
        white_population = np.random.randint(100, 5000)
    total_population = max(total_population, latino_population + white_population)
    return total_population, latino_population, white_population

# Apply the function to each row
populations = gdf['NAMELSADCO'].apply(generate_population)
gdf['total_population'], gdf['latino_population'], gdf['white_population'] = zip(*populations)

# Determine majority Hispanic tracts
gdf['majority_hispanic'] = gdf['latino_population'] > gdf['white_population']

# Extract relevant properties
gdf['tract_id'] = gdf['GEOID']
gdf['county_name'] = gdf['NAMELSADCO']

# Select relevant columns
pop_data = gdf[['tract_id', 'county_name', 'total_population', 'latino_population', 'white_population', 'majority_hispanic']]

# Ensure output directory exists
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# Save to CSV
csv_path = os.path.join(output_dir, 'random_population_data.csv')
pop_data.to_csv(csv_path, index=False)

print(f"Random population data saved to {csv_path}")