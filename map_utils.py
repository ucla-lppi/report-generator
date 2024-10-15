import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import os
from matplotlib.patches import Patch

def generate_majority_tracts_map(geojson_path, pop_data_path, output_dir, basemap_source=ctx.providers.OpenStreetMap.Mapnik, zoom=10):
    try:
        print(f"Loading GeoJSON data from {geojson_path}")
        gdf = gpd.read_file(geojson_path)
        print(f"GeoJSON data loaded: {gdf.shape[0]} records")
        print(gdf.head())

        print(f"Loading population data from {pop_data_path}")
        pop_df = pd.read_csv(pop_data_path, dtype={'GEOID': str})
        print(f"Population data loaded: {pop_df.shape[0]} records")
        print(pop_df.head())

        print("Ensuring the columns used for joining have the same data type and padding GEOID with leading zeros")
        gdf['GEOID'] = gdf['GEOID'].astype(str).str.zfill(11)
        pop_df['GEOID'] = pop_df['GEOID'].astype(str).str.zfill(11)

        print("Unique GEOID values in GeoDataFrame:")
        print(gdf['GEOID'].unique()[:10])  # Print first 10 unique values

        print("Unique GEOID values in population DataFrame:")
        print(pop_df['GEOID'].unique()[:10])  # Print first 10 unique values

        print("Setting index for join")
        gdf.set_index('GEOID', inplace=True)
        pop_df.set_index('GEOID', inplace=True)

        print("Performing the join")
        joined_gdf = gdf.join(pop_df, how='inner')
        print(f"Joined data: {joined_gdf.shape[0]} records")
        print(joined_gdf.head())

        print("Reprojecting to California Albers NAD 83")
        joined_gdf = joined_gdf.to_crs(epsg=3310)

        print("Getting unique counties")
        counties = joined_gdf['county'].dropna().unique()
        print(f"Counties found: {counties}")

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

                fig, ax = plt.subplots(1, 1, figsize=(15, 15))

                # Get unique neighborhood types
                neighborhood_types = county_gdf['Neighborhood_type'].unique()
                colors = {
                    '70+ Latino': 'lightpink',
                    '50+ Latino': 'lightpink',
                    '70+ NL White': '#2774AE',
                    '50+ NL White': '#2774AE',
                    'Other': 'white'
                }
                edgecolors = {
                    '70+ Latino': 'lightgray',
                    '50+ Latino': 'lightgray',
                    '70+ NL White': 'lightgray',
                    '50+ NL White': 'lightgray',
                    'Other': 'none'
                }

                for neighborhood_type in neighborhood_types:
                    if not county_gdf[county_gdf['Neighborhood_type'] == neighborhood_type].empty:
                        county_gdf[county_gdf['Neighborhood_type'] == neighborhood_type].plot(
                            ax=ax, 
                            color=colors.get(neighborhood_type, 'white'), 
                            edgecolor=edgecolors.get(neighborhood_type, 'none'), 
                            linewidth=0.5, 
                            label=neighborhood_type
                        )

                ctx.add_basemap(ax, source=basemap_source, zoom=zoom)

                # Create legend dynamically
                legend_elements = [Patch(facecolor=colors[nt], edgecolor=edgecolors[nt], label=nt) for nt in neighborhood_types]
                ax.legend(handles=legend_elements, loc='upper right', title='Census Tracts')

                ax.set_aspect('equal')  # Set aspect ratio to be equal
                ax.set_axis_off()

                os.makedirs(output_dir, exist_ok=True)

                output_path = os.path.join(output_dir, f'{county}_majority_tracts_map.png')
                print(f"Saving map to {output_path}")

                plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1)
                plt.close()

                print(f"Map for {county} saved to {output_path}")
            except Exception as e:
                print(f"An error occurred while processing {county}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")