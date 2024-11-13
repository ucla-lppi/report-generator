import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import os
from matplotlib.patches import Patch
import numpy as np
import jenkspy

heat_variable = 'LONG_90_DAY'
# heat_variable = 'avg_90F'

def generate_majority_tracts_map(geojson_path, pop_data_path, county_geojson_path, output_dir, basemap_source=ctx.providers.CartoDB.Positron, label_layer=ctx.providers.CartoDB.PositronOnlyLabels, zoom=10, dpi=300, map_type=None, heat_data_path=None, population_filter=None, road_data_path=None):
    try:
        print(f"Loading GeoJSON data from {geojson_path}")
        gdf = gpd.read_file(geojson_path)
        print(f"GeoJSON data loaded: {gdf.shape[0]} records")
        print(gdf.head())

        print(f"Loading population data from {pop_data_path}")
        pop_df = pd.read_csv(pop_data_path, dtype={'GEOID': str})
        print(f"Population data loaded: {pop_df.shape[0]} records")
        print(pop_df.head())

        if map_type == "heat" and heat_data_path:
            print(f"Loading heat data from {heat_data_path}")
            heat_df = pd.read_csv(heat_data_path, dtype={'GEOID': str})
            print(f"Heat data loaded: {heat_df.shape[0]} records")
            print(heat_df.head())

        print(f"Loading county boundaries from {county_geojson_path}")
        counties_gdf = gpd.read_file(county_geojson_path)
        print(f"County boundaries loaded: {counties_gdf.shape[0]} records")
        print(counties_gdf.head())

        print(f"Loading roads data from {road_data_path}")
        roads_gdf = gpd.read_file(road_data_path)
        print(f"Roads data loaded: {roads_gdf.shape[0]} records")
        print(roads_gdf.head())

        print("Ensuring the columns used for joining have the same data type and padding GEOID with leading zeros")
        gdf['GEOID'] = gdf['GEOID'].astype(str).str.zfill(11)
        pop_df['GEOID'] = pop_df['GEOID'].astype(str).str.zfill(11)
        if map_type == "heat" and heat_data_path:
            heat_df['GEOID'] = heat_df['GEOID'].astype(str).str.zfill(11)

        print("Setting index for join")
        gdf.set_index('GEOID', inplace=True)
        pop_df.set_index('GEOID', inplace=True)
        if map_type == "heat" and heat_data_path:
            heat_df.set_index('GEOID', inplace=True)

        print("Performing the join")
        joined_gdf = gdf.join(pop_df, how='inner')
        if map_type == "heat" and heat_data_path:
            joined_gdf = joined_gdf.join(heat_df[[heat_variable]], how='inner')
        print(f"Joined data: {joined_gdf.shape[0]} records")
        print(joined_gdf.head())

        print("Reprojecting to Web Mercator (EPSG:3857)")
        joined_gdf = joined_gdf.to_crs(epsg=3857)
        counties_gdf = counties_gdf.to_crs(epsg=3857)
        roads_gdf = roads_gdf.to_crs(epsg=3857)

        print("Getting unique counties")
        counties = joined_gdf['county'].dropna().unique()
        print(f"Counties found: {counties}")

        # Calculate overall county average and standard deviation
        overall_average = joined_gdf[heat_variable].mean()
        print(f"Overall average: {overall_average}")

        # Calculate breaks using jenkspy on the combined data
        breaks = jenkspy.jenks_breaks(joined_gdf[heat_variable], n_classes=2)
        breaks = [round(b) for b in breaks]  # Round the break values to the nearest integer
        print(f"Jenks breaks: {breaks}")

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

                # Filter based on population type
                latino_gdf = county_gdf[county_gdf['Neighborhood_type'] == '70+ Latino']
                white_gdf = county_gdf[county_gdf['Neighborhood_type'] == '70+ NL White']

                # Combine Latino and White neighborhoods
                combined_gdf = pd.concat([latino_gdf, white_gdf])

                if combined_gdf.empty:
                    print(f"No valid Latino or White 70+ neighborhoods for {county}")
                    continue

                # Get the matching county shape
                county_shape = counties_gdf[counties_gdf['name'] == county]

                # Clip the roads to the county boundaries
                clipped_roads = gpd.overlay(roads_gdf, county_shape, how='intersection')

                fig, ax = plt.subplots(1, 1, figsize=(15, 15))

                # Plot the county boundary with a gray outline and no fill
                county_shape.boundary.plot(ax=ax, linewidth=2.5, edgecolor='gray', zorder=3, alpha=0.45)

                if map_type == "heat":
                    # Create legend elements
                    legend_elements = []

                    # Define colors for Latino and White neighborhoods
                    latino_colors = ['#fc9272', '#fb6a4a']
                    white_colors = ['#f4e57f', '#f9c148']

                    # Plot Latino areas
                    for i, (color, label) in enumerate(zip(latino_colors, ['Below Average', 'Above Average'])):
                        if label == 'Below Average':
                            mask = latino_gdf[heat_variable] <= breaks[1]
                        else:
                            mask = latino_gdf[heat_variable] > breaks[1]

                        if not latino_gdf[mask].empty:
                            latino_gdf[mask].plot(ax=ax, color=color, edgecolor='none', linewidth=0.5, alpha=0.6)
                            legend_elements.append(Patch(facecolor=color, edgecolor='none', label=f'{label} (Latino) ({round(latino_gdf[mask][heat_variable].min())}-{round(latino_gdf[mask][heat_variable].max())} days)', alpha=0.6))

                    # Plot White areas
                    for i, (color, label) in enumerate(zip(white_colors, ['Below Average', 'Above Average'])):
                        if label == 'Below Average':
                            mask = white_gdf[heat_variable] <= breaks[1]
                        else:
                            mask = white_gdf[heat_variable] > breaks[1]

                        if not white_gdf[mask].empty:
                            white_gdf[mask].plot(ax=ax, color=color, edgecolor='none', linewidth=0.5, alpha=0.6)
                            legend_elements.append(Patch(facecolor=color, edgecolor='none', label=f'{label} (White) ({round(white_gdf[mask][heat_variable].min())}-{round(white_gdf[mask][heat_variable].max())} days)', alpha=0.6))

                    # Add overall average to the legend if it's a valid number
                    if pd.notna(overall_average):
                        legend_elements.append(Patch(facecolor='none', edgecolor='none', label=f'State Average: {round(overall_average)} days'))

                    # Plot areas with no temperature data in light gray
                    no_data_gdf = combined_gdf[combined_gdf[heat_variable].isna()]
                    print(f"No data records: {no_data_gdf.shape[0]}")
                    no_data_gdf.plot(ax=ax, color='#d9d9d9', edgecolor='lightgray', linewidth=0.5, alpha=0.6)

                    # Add legend to the plot
                    if legend_elements:
                        legend_title = ''
                        if heat_variable == 'avg_90F':
                            legend_title = 'Annual Number of Days with 90°F+'
                        if heat_variable == 'LONG_90_DAY':
                            legend_title = 'Exposure to Heatwaves over 90°F+'
                        legend = ax.legend(handles=legend_elements, loc='upper right', title=legend_title)
                        legend.set_zorder(10)  # Ensure legend is on top

                ctx.add_basemap(ax, source=basemap_source, zoom=zoom)
                ctx.add_basemap(ax, source=label_layer, zoom=zoom)

                ax.set_aspect('equal')  # Set aspect ratio to be equal
                ax.set_axis_off()

                # Create output directory for combined maps
                output_subdir = os.path.join(output_dir, 'combined_maps', f'{heat_variable}')
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