import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import os
from matplotlib.patches import Patch

def generate_majority_tracts_map(geojson_path, pop_data_path, county_geojson_path, output_dir, basemap_source=ctx.providers.CartoDB.Positron, label_layer=ctx.providers.CartoDB.PositronOnlyLabels, zoom=10, dpi=300, map_type=None, heat_data_path=None, population_filter=None):
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
            joined_gdf = joined_gdf.join(heat_df[['LONG_90_DAY']], how='inner')
        print(f"Joined data: {joined_gdf.shape[0]} records")
        print(joined_gdf.head())

        print("Reprojecting to Web Mercator (EPSG:3857)")
        joined_gdf = joined_gdf.to_crs(epsg=3857)
        counties_gdf = counties_gdf.to_crs(epsg=3857)

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

                # Get the matching county shape
                county_shape = counties_gdf[counties_gdf['name'] == county]

                fig, ax = plt.subplots(1, 1, figsize=(15, 15))

                # Plot the county boundary with a gray outline and no fill
                county_shape.boundary.plot(ax=ax, linewidth=2.5, edgecolor='gray', zorder=3, alpha=0.45)

                if map_type == "heat":
                    # Filter based on population type
                    if population_filter == "latino":
                        filtered_gdf = county_gdf[county_gdf['Neighborhood_type'] == '70+ Latino']
                    elif population_filter == "white":
                        filtered_gdf = county_gdf[county_gdf['Neighborhood_type'].isin(['70+ NL White', 'Other'])]
                    else:
                        filtered_gdf = county_gdf

                    # Define heat map colors
                    colors = {
                        (0, 2): '#fee5d9',
                        (2, 4): '#fcae91',
                        (4, 6): '#fb6a4a',
                        (6, 8): '#de2d26',
                        (8, float('inf')): '#a50f15'
                    }

                    # Create legend elements
                    legend_elements = []
                    for (min_val, max_val), color in colors.items():
                        mask = (filtered_gdf['LONG_90_DAY'] >= min_val) & (filtered_gdf['LONG_90_DAY'] < max_val)
                        if not filtered_gdf[mask].empty:
                            filtered_gdf[mask].plot(
                                ax=ax,
                                color=color,
                                edgecolor='lightgray',
                                linewidth=0.5,
                                alpha=0.6
                            )
                            label = f'{min_val}-{max_val if max_val != float("inf") else "+"} days'
                            legend_elements.append(Patch(facecolor=color, edgecolor='lightgray', label=label, alpha=0.6))

                    # Plot areas with no temperature data as transparent
                    no_data_gdf = county_gdf[~county_gdf.index.isin(filtered_gdf.index)]
                    no_data_gdf.plot(ax=ax, color='none', edgecolor='none', linewidth=0.5, alpha=0.0)

                    # title = f'Extreme Heat Days (90°F+) - {county}'
                    # ax.set_title(title)

                    # Add legend to the plot
                    if legend_elements:
                        ax.legend(handles=legend_elements, loc='upper right', title='Days with 90°F+ Temperature')

                ctx.add_basemap(ax, source=basemap_source, zoom=zoom)
                ctx.add_basemap(ax, source=label_layer, zoom=zoom)

                ax.set_aspect('equal')  # Set aspect ratio to be equal
                ax.set_axis_off()

                # Create separate output directories for Latino and NL White/Other maps
                output_subdir = os.path.join(output_dir, population_filter)
                os.makedirs(output_subdir, exist_ok=True)

                output_path = os.path.join(output_subdir, f'{county}_heat_map.png')
                print(f"Saving map to {output_path}")

                plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1, dpi=dpi)
                plt.close()

                print(f"Map for {county} saved to {output_path}")
            except Exception as e:
                print(f"An error occurred while processing {county}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")