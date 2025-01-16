import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import os
from matplotlib.patches import Patch

target_county_parameter = ''

# Define colors for neighborhoods
COLOR_ABOVE_AVERAGE = '#5b0000'
COLOR_ZERO_DAY_COUNT = '#fc9b9b'
COLOR_BELOW_EQUAL_AVERAGE = '#ac3434'

# Define county boundary style
COUNTY_BOUNDARY_COLOR = 'gray'
COUNTY_BOUNDARY_LINEWIDTH = 2.5
COUNTY_BOUNDARY_ALPHA = 0.45

# Heat variable
heat_variable = 'categorical_average'

def generate_maps(joined_geojson_path, pop_data_path, county_geojson_path, roads_geojson_path, output_dir, target_county=None, basemap_source=ctx.providers.CartoDB.Positron, label_layer=ctx.providers.CartoDB.PositronOnlyLabels, zoom=10, dpi=300):
    try:
        print(f"Loading joined GeoJSON data from {joined_geojson_path}")
        joined_gdf = gpd.read_file(joined_geojson_path)
        print(f"Joined data loaded: {joined_gdf.shape[0]} records")
        print(joined_gdf.head())

        print(f"Loading population data from {pop_data_path}")
        pop_df = pd.read_csv(pop_data_path, dtype={'GEOID': str})
        print(f"Population data loaded: {pop_df.shape[0]} records")
        print(pop_df.head())

        print("Loading county boundaries from {county_geojson_path}")
        counties_gdf = gpd.read_file(county_geojson_path)
        print(f"County boundaries loaded: {counties_gdf.shape[0]} records")
        print(counties_gdf.head())

        # Load Google Sheet data
        print("Loading Google Sheet data from CSV")
        google_sheet_url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTDl0u8xAvazJjlCn62edUDjjK1tLwyi4hXihYpYIGOxawrN3_HfzvYKJ1ARzH4AzhrHZysIpkc_1Nc/pub?output=csv'
        google_df = pd.read_csv(google_sheet_url, dtype={'County': str})
        print(f"Google Sheet data loaded: {google_df.shape[0]} records")
        print(google_df.head())

        print("Merging Google Sheet data with county GeoDataFrame")
        counties_gdf = counties_gdf.merge(google_df, how='left', left_on='name', right_on='County')
        print(f"Counties after merge: {counties_gdf.shape[0]} records")
        print(counties_gdf.head())

        print(f"Loading roads data from {roads_geojson_path}")
        roads_gdf = gpd.read_file(roads_geojson_path)
        print(f"Roads data loaded: {roads_gdf.shape[0]} records")
        print(roads_gdf.head())

        print("Ensuring the columns used for joining have the same data type and padding GEOID with leading zeros")
        joined_gdf['GEOID'] = joined_gdf['GEOID'].astype(str).str.zfill(11)
        pop_df['GEOID'] = pop_df['GEOID'].astype(str).str.zfill(11)

        print("Dropping 'county' column from population data to avoid overlap")
        if 'county' in pop_df.columns:
            pop_df = pop_df.drop(columns=['county'])
            print("Dropped 'county' column from population data.")

        print("Setting index for join")
        joined_gdf.set_index('GEOID', inplace=True)
        pop_df.set_index('GEOID', inplace=True)

        print("Performing the join with population data")
        joined_gdf = joined_gdf.join(pop_df, how='inner')
        print(f"Joined data with population: {joined_gdf.shape[0]} records")
        print(joined_gdf.head())

        print("Reprojecting to Web Mercator (EPSG:3857)")
        joined_gdf = joined_gdf.to_crs(epsg=3857)
        counties_gdf = counties_gdf.to_crs(epsg=3857)
        roads_gdf = roads_gdf.to_crs(epsg=3857)

        print("Getting unique counties")
        if target_county:
            if target_county in joined_gdf['county'].unique():
                counties = [target_county]
                print(f"Processing only target county: {target_county}")
            else:
                print(f"Target county '{target_county}' not found in data.")
                counties = []
        else:
            counties = joined_gdf['county'].dropna().unique()
            print(f"Counties to process: {counties}")

        for county in counties:
            try:
                print(f"Processing county: {county}")
                county_gdf = joined_gdf[joined_gdf['county'] == county]
                print(f"County data: {county_gdf.shape[0]} records")

                # Ensure geometries are valid and not empty
                county_gdf = county_gdf[county_gdf.is_valid & ~county_gdf.is_empty]

                if county_gdf.empty:
                    print(f"No valid geometries for {county}")
                    continue

                # Filter based on neighborhood type
                latino_gdf = county_gdf[county_gdf['neighborhood_type'].isin(['50+ Latino', '70+ Latino'])]

                # Dissolve Latino boundaries
                dissolved_latino_gdf = latino_gdf.dissolve()

                # Get the matching county shape
                county_shape = counties_gdf[counties_gdf['name'] == county]

                fig, ax = plt.subplots(1, 1, figsize=(15, 15))

                # Plot the county boundary with a gray outline and no fill
                county_shape.boundary.plot(ax=ax, linewidth=COUNTY_BOUNDARY_LINEWIDTH, edgecolor=COUNTY_BOUNDARY_COLOR, zorder=3, alpha=COUNTY_BOUNDARY_ALPHA)

                # Create legend elements
                legend_elements = []

                # Define colors for neighborhoods
                colors = {
                    'Zero Day Count': COLOR_ZERO_DAY_COUNT,
                    'Below/Equal Average': COLOR_BELOW_EQUAL_AVERAGE,
                    'Above Average': COLOR_ABOVE_AVERAGE
                }

                # Plot all areas
                for label, color in colors.items():
                    mask = county_gdf[heat_variable] == label
                    if not county_gdf[mask].empty:
                        county_gdf[mask].plot(ax=ax, color=color, edgecolor='none', linewidth=0.5, alpha=0.6)
                        legend_elements.append(Patch(facecolor=color, edgecolor='none', label=f'{label}', alpha=0.6))

                # Plot dissolved Latino areas with a darker border and light hatch marks
                for label, color in colors.items():
                    mask = dissolved_latino_gdf[heat_variable] == label
                    if not dissolved_latino_gdf[mask].empty:
                        dissolved_latino_gdf[mask].plot(ax=ax, color='none', edgecolor='black', linewidth=1.0, alpha=0.6)
                        dissolved_latino_gdf[mask].plot(ax=ax, color='none', edgecolor='black', linewidth=0.5, alpha=0.3, hatch='/', zorder=4)
                
                # Plot areas with no data in light gray
                no_data_gdf = county_gdf[county_gdf[heat_variable].isna()]
                print(f"No data records: {no_data_gdf.shape[0]}")
                no_data_gdf.plot(ax=ax, color='#d9d9d9', edgecolor='lightgray', linewidth=0.5, alpha=0.6)

                # Add legend to the plot
                if legend_elements:
                    legend_elements.append(Patch(facecolor='none', edgecolor='black', label='Latino Neighborhoods', hatch='/', alpha=0.3))
                    legend = ax.legend(handles=legend_elements, loc='upper right', title='Categorical Average')
                    legend.set_zorder(10)  # Ensure legend is on top

                ctx.add_basemap(ax, source=basemap_source, zoom=zoom)
                ctx.add_basemap(ax, source=label_layer, zoom=zoom)

                ax.set_aspect('equal')  # Set aspect ratio to be equal
                ax.set_axis_off()

                # Create output directory for combined maps
                output_subdir = os.path.join(output_dir, 'combined_maps')
                os.makedirs(output_subdir, exist_ok=True)

                output_path = os.path.join(output_subdir, f'{county}_heat_map_combined.png')
                print(f"Saving map to {output_path}")

                plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1, dpi=dpi)
                plt.close()

                print(f"Map for {county} saved to {output_path}")
            except Exception as e:
                print(f"An error occurred while processing {county}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    joined_geojson = 'output/joined_heat_data.geojson'
    population_data = 'inputs/tract_level_data.csv'
    county_geojson = 'inputs/geojson/ca_counties_simplified.geojson'
    roads_geojson = 'inputs/geojson/ca_primary_secondary_roads.geojson'
    output_directory = 'output/final_heat_maps'
    
    # Set target_county here. Leave as None or empty string to process all counties.
    target_county = target_county_parameter  # e.g., 'Los Angeles County' or 'None'

    generate_maps(
        joined_geojson_path=joined_geojson,
        pop_data_path=population_data,
        county_geojson_path=county_geojson,
        roads_geojson_path=roads_geojson,
        output_dir=output_directory,
        target_county=target_county
    )