import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import os
from matplotlib.patches import Patch

# Define colors for neighborhoods
COLOR_ABOVE_AVERAGE = '#5b0000'
COLOR_ZERO_DAY_COUNT = '#fc9b9b'
COLOR_BELOW_EQUAL_AVERAGE = '#ac3434'

# Define county boundary style
COUNTY_BOUNDARY_COLOR = 'gray'
COUNTY_BOUNDARY_LINEWIDTH = 2.5
COUNTY_BOUNDARY_ALPHA = 0.45

output_geojson_path = 'output/joined_heat_data.geojson'

heat_variable = 'categorical_average'

def join_heat_data_to_census(census_geojson_path, heat_data_path, output_geojson_path):
    try:
        print(f"Loading census GeoJSON data from {census_geojson_path}")
        census_gdf = gpd.read_file(census_geojson_path)
        print(f"Census data loaded: {census_gdf.shape[0]} records")
        print(census_gdf.head())

        print(f"Loading heat data from {heat_data_path}")
        heat_df = pd.read_csv(heat_data_path, dtype={'GEOID': str})
        print(f"Heat data loaded: {heat_df.shape[0]} records")
        print(heat_df.head())

        print("Ensuring GEOID columns have the same data type and padding with leading zeros")
        census_gdf['GEOID'] = census_gdf['GEOID'].astype(str).str.zfill(11)
        heat_df['GEOID'] = heat_df['GEOID'].astype(str).str.zfill(11)

        print("Performing the join on GEOID")
        joined_gdf = census_gdf.merge(heat_df, on='GEOID', how='left')
        print(f"Joined data: {joined_gdf.shape[0]} records")
        print(joined_gdf.head())

        print(f"Saving joined data to {output_geojson_path}")
        joined_gdf.to_file(output_geojson_path, driver='GeoJSON')
        print("Join and save successful.")

    except Exception as e:
        print(f"An error occurred while joining heat data to census tracts: {e}")

def generate_majority_tracts_map(
    geojson_path,
    pop_data_path,
    county_geojson_path,
    output_dir,
    basemap_source=ctx.providers.CartoDB.Positron,
    label_layer=ctx.providers.CartoDB.PositronOnlyLabels,
    zoom=10,
    dpi=150,  # Increased dpi for better resolution
    map_type=None,
    heat_data_path=None,
    population_filter=None,
    road_data_path=None,
    county_filter=None
):
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
        join_heat_data_to_census(geojson_path, heat_data_path, output_geojson_path)
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
        if county_filter:
            counties = [county_filter]
        else:
            counties = joined_gdf['county'].dropna().unique()
        print(f"Counties to process: {counties}")

        # Calculate state average
        category_mapping = {
            'Zero Day Count': 0,
            'Below/Equal Average': 1,
            'Above Average': 2
        }
        joined_gdf['categorical_average_num'] = joined_gdf['categorical_average'].map(category_mapping)
        state_average = joined_gdf['categorical_average_num'].mean()
        print(f"State Average: {state_average:.2f}")

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
                latino_gdf = county_gdf[county_gdf['Neighborhood_type'].isin(['50+ Latino', '70+ Latino'])]

                # Dissolve Latino boundaries
                dissolved_latino_gdf = latino_gdf.dissolve()
                print(f"Dissolved Latino neighborhoods: {dissolved_latino_gdf.shape[0]} records")

                # Calculate county average
                county_average = county_gdf['categorical_average_num'].mean()
                print(f"County Average: {county_average:.2f}")

                # Get the matching county shape
                county_shape = counties_gdf[counties_gdf['name'] == county]

                # Calculate figsize based on aspect ratio similar to 590x760 (~0.776)
                aspect_ratio = 590 / 760  # ≈0.776
                desired_width_inches = 8  # Choose a larger width for better visibility
                desired_height_inches = desired_width_inches / aspect_ratio  # ≈10.3
                figsize = (desired_width_inches, desired_height_inches)

                fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)

                # Plot the county boundary with a gray outline and no fill
                county_shape.boundary.plot(
                    ax=ax,
                    linewidth=COUNTY_BOUNDARY_LINEWIDTH,
                    edgecolor=COUNTY_BOUNDARY_COLOR,
                    zorder=3,
                    alpha=COUNTY_BOUNDARY_ALPHA
                )

                # Create legend elements
                legend_elements = []

                # Define colors for neighborhoods
                colors = {
                    'Zero Day Count': COLOR_ZERO_DAY_COUNT,
                    'Below/Equal Average': COLOR_BELOW_EQUAL_AVERAGE,
                    'Above Average': COLOR_ABOVE_AVERAGE
                }
                # Define label mapping for legend
                label_mapping = {
                    'Zero Day Count': 'Zero Days',
                    'Below/Equal Average': 'Below Average',
                    'Above Average': 'Above Average'
                }

                # Plot all areas
                for label, color in colors.items():
                    mask = county_gdf[heat_variable] == label
                    if not county_gdf[mask].empty:
                        county_gdf[mask].plot(
                            ax=ax,
                            color=color,
                            edgecolor='none',
                            linewidth=0.5,
                            alpha=0.6
                        )
                        # Use mapped label for legend
                        legend_elements.append(
                            Patch(
                                facecolor=color,
                                edgecolor='none',
                                label=label_mapping.get(label, label),
                                alpha=0.6
                            )
                        )

                # Plot dissolved Latino areas with a darker border and light hatch marks
                for label, color in colors.items():
                    mask = dissolved_latino_gdf[heat_variable] == label
                    if not dissolved_latino_gdf[mask].empty:
                        dissolved_latino_gdf[mask].plot(
                            ax=ax,
                            color='none',
                            edgecolor='black',
                            linewidth=1.0,
                            alpha=0.6
                        )
                        dissolved_latino_gdf[mask].plot(
                            ax=ax,
                            color='none',
                            edgecolor='gray',
                            linewidth=0.5,
                            alpha=0.3,
                            hatch='/',
                            zorder=4
                        )

                # Plot areas with no data in light gray
                no_data_gdf = county_gdf[county_gdf[heat_variable].isna()]
                print(f"No data records: {no_data_gdf.shape[0]}")
                no_data_gdf.plot(
                    ax=ax,
                    color='#d9d9d9',
                    edgecolor='lightgray',
                    linewidth=0.5,
                    alpha=0.6
                )

                # Adjust plot limits to maintain aspect ratio
                bounds = county_gdf.total_bounds  # minx, miny, maxx, maxy
                minx, miny, maxx, maxy = bounds
                current_ratio = (maxx - minx) / (maxy - miny)
                desired_ratio = aspect_ratio  # ≈0.776

                if current_ratio > desired_ratio:
                    # Adjust y limits
                    expected_height = (maxx - minx) / desired_ratio
                    y_center = (miny + maxy) / 2
                    y_min = y_center - expected_height / 2
                    y_max = y_center + expected_height / 2
                    ax.set_ylim(y_min, y_max)
                else:
                    # Adjust x limits
                    expected_width = (maxy - miny) * desired_ratio
                    x_center = (minx + maxx) / 2
                    x_min = x_center - expected_width / 2
                    x_max = x_center + expected_width / 2
                    ax.set_xlim(x_min, x_max)

                # Add Legend
                if legend_elements:
                    legend_elements.append(
                        Patch(
                            facecolor='none',
                            edgecolor='black',
                            label='Latino Neighborhoods',
                            hatch='/',
                            alpha=0.3
                        )
                    )
                    legend_elements.append(
                        Patch(
                            facecolor='none',
                            edgecolor='none',
                            label=f'County Average: {county_average:.2f}'
                        )
                    )
                    legend_elements.append(
                        Patch(
                            facecolor='none',
                            edgecolor='none',
                            label=f'State Average: {state_average:.2f}'
                        )
                    )
                    legend = ax.legend(
                        handles=legend_elements,
                        loc='upper right',
                        title='Categorical Average',
                        frameon=True
                    )
                    legend.set_zorder(10)  # Ensure legend is on top

                # Add Basemap Layers
                ctx.add_basemap(ax, source=basemap_source, zoom=zoom)
                ctx.add_basemap(ax, source=label_layer, zoom=zoom)

                ax.set_aspect('equal')  # Keep aspect ratio
                ax.set_axis_off()

                # Create output directory for combined maps
                output_subdir = os.path.join(output_dir, 'combined_maps')
                os.makedirs(output_subdir, exist_ok=True)

                output_path = os.path.join(output_subdir, f'{county}_heat_map_combined.png')
                print(f"Saving map to {output_path}")

                plt.savefig(
                    output_path,
                    bbox_inches='tight',
                    pad_inches=0.1,
                    dpi=dpi  # Ensure dpi is consistent with figsize
                )
                plt.close()

                print(f"Map for {county} saved to {output_path}")
            except Exception as e:
                print(f"An error occurred while processing {county}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")