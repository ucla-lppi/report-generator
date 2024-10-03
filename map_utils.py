import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import os

def generate_majority_tracts_map(geojson_path, pop_data_path, output_dir, basemap_source=ctx.providers.OpenStreetMap.Mapnik, zoom=10):
    try:
        print(f"Loading GeoJSON data from {geojson_path}")
        gdf = gpd.read_file(geojson_path)
        print(f"GeoJSON data loaded: {gdf.shape[0]} records")
        print(gdf.head())

        print(f"Loading population data from {pop_data_path}")
        pop_df = pd.read_csv(pop_data_path, dtype={'tract_id': str})
        print(f"Population data loaded: {pop_df.shape[0]} records")
        print(pop_df.head())

        print("Ensuring the columns used for joining have the same data type")
        gdf['GEOID'] = gdf['GEOID'].astype(str)
        pop_df['tract_id'] = pop_df['tract_id'].astype(str)

        print("Unique GEOID values in GeoDataFrame:")
        print(gdf['GEOID'].unique()[:10])  # Print first 10 unique values

        print("Unique tract_id values in population DataFrame:")
        print(pop_df['tract_id'].unique()[:10])  # Print first 10 unique values

        print("Setting index for join")
        gdf.set_index('GEOID', inplace=True)
        pop_df.set_index('tract_id', inplace=True)

        print("Performing the join")
        joined_gdf = gdf.join(pop_df, how='inner')
        print(f"Joined data: {joined_gdf.shape[0]} records")
        print(joined_gdf.head())

        print("Getting unique counties")
        counties = joined_gdf['county_name'].unique()
        print(f"Counties found: {counties}")

        for county in counties:
            try:
                print(f"Processing county: {county}")
                county_gdf = joined_gdf[joined_gdf['county_name'] == county]
                print(f"County data: {county_gdf.shape[0]} records")

                # Ensure geometries are valid
                county_gdf = county_gdf[county_gdf.is_valid]

                fig, ax = plt.subplots(1, 1, figsize=(15, 15))

                county_gdf[county_gdf['majority_hispanic']].plot(ax=ax, color='red', edgecolor='black', label='Majority Hispanic')
                county_gdf[~county_gdf['majority_hispanic']].plot(ax=ax, color='blue', edgecolor='black', label='Majority White')

                ctx.add_basemap(ax, source=basemap_source, zoom=zoom)

                legend = ax.legend(loc='upper right', title='Census Tracts')

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
        