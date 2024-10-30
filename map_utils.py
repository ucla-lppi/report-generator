import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import os
from matplotlib.patches import Patch

def generate_majority_tracts_map(geojson_path, pop_data_path, county_geojson_path, roads_path, output_dir, basemap_source=ctx.providers.CartoDB.Positron, label_layer=ctx.providers.CartoDB.PositronOnlyLabels, zoom=10, dpi=300):
    try:
        print(f"Loading GeoJSON data from {geojson_path}")
        gdf = gpd.read_file(geojson_path)
        print(f"GeoJSON data loaded: {gdf.shape[0]} records")
        print(gdf.head())

        print(f"Loading population data from {pop_data_path}")
        pop_df = pd.read_csv(pop_data_path, dtype={'GEOID': str})
        print(f"Population data loaded: {pop_df.shape[0]} records")
        print(pop_df.head())

        print(f"Loading county boundaries from {county_geojson_path}")
        counties_gdf = gpd.read_file(county_geojson_path)
        print(f"County boundaries loaded: {counties_gdf.shape[0]} records")
        print(counties_gdf.head())

        print(f"Loading roads data from {roads_path}")
        roads_gdf = gpd.read_file(roads_path)
        print(f"Roads data loaded: {roads_gdf.shape[0]} records")
        print(roads_gdf.head())

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

        print("Reprojecting to Web Mercator (EPSG:3857)")
        joined_gdf = joined_gdf.to_crs(epsg=3857)
        counties_gdf = counties_gdf.to_crs(epsg=3857)
        roads_gdf = roads_gdf.to_crs(epsg=3857)

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

                # Clip the roads to the county boundaries
                clipped_roads = gpd.overlay(roads_gdf, county_shape, how='intersection')

                fig, ax = plt.subplots(1, 1, figsize=(15, 15))

                # Plot the county boundary with a gray outline and no fill
                county_shape.boundary.plot(ax=ax, linewidth=2.5, edgecolor='gray', zorder=3, alpha=0.45)

                # Plot the clipped roads with a thicker gray line and higher transparency
                clipped_roads.plot(ax=ax, color='#e3e3e3', linewidth=1.5, alpha=1, zorder=2)

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
                human_friendly_labels = {
                    '70+ Latino': 'Over 70% Latino',
                    '50+ Latino': 'Over 50% Latino',
                    '70+ NL White': 'Over 70% Non-Latino White',
                    '50+ NL White': 'Over 50% Non-Latino White',
                    'Other': 'Other'
                }

                for neighborhood_type in neighborhood_types:
                    if not county_gdf[county_gdf['Neighborhood_type'] == neighborhood_type].empty:
                        county_gdf[county_gdf['Neighborhood_type'] == neighborhood_type].plot(
                            ax=ax, 
                            color=colors.get(neighborhood_type, 'white'), 
                            edgecolor=edgecolors.get(neighborhood_type, 'none'), 
                            linewidth=0.5, 
                            alpha=0.6,  # Set transparency
                            label=human_friendly_labels.get(neighborhood_type, neighborhood_type)
                        )

                ctx.add_basemap(ax, source=basemap_source, zoom=zoom)
                ctx.add_basemap(ax, source=label_layer, zoom=zoom)

                ax.set_aspect('equal')  # Set aspect ratio to be equal
                ax.set_axis_off()

                # Create legend dynamically and add it last
                legend_elements = [Patch(facecolor=colors[nt], edgecolor=edgecolors[nt], label=human_friendly_labels[nt], alpha=0.6) for nt in neighborhood_types]
                ax.legend(handles=legend_elements, loc='upper right', title='Census Tracts')

                os.makedirs(output_dir, exist_ok=True)

                output_path = os.path.join(output_dir, f'{county}_majority_tracts_map.png')
                print(f"Saving map to {output_path}")

                plt.savefig(output_path, bbox_inches='tight', pad_inches=0.1, dpi=dpi)
                plt.close()

                print(f"Map for {county} saved to {output_path}")
            except Exception as e:
                print(f"An error occurred while processing {county}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")