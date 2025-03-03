import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import os
from matplotlib.patches import Patch
import matplotlib.patheffects as PathEffects
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Bbox

MAJOR_CITIES = [
	"Los Angeles", "San Diego", "San Jose", "San Francisco", "Santa Cruz", "Santa Barbara",
	"Fresno", "Sacramento", "Long Beach", "Oakland", "Bakersfield", "Monterey"
]

# Define colors for neighborhoods
COLOR_ABOVE_AVERAGE = '#5b0000'
COLOR_ZERO_DAY_COUNT = '#fc9b9b'
COLOR_BELOW_EQUAL_AVERAGE = '#ac3434'

# Define county boundary style
COUNTY_BOUNDARY_COLOR = 'gray'
COUNTY_BOUNDARY_LINEWIDTH = 2.5
COUNTY_BOUNDARY_ALPHA = 0.45

output_geojson_path = 'output/joined_data.geojson'

def join_heat_data_to_census(census_geojson_path, topical_data_path, temp_output_geojson_path):
    try:
        print(f"Loading census GeoJSON data from {census_geojson_path}")
        census_gdf = gpd.read_file(census_geojson_path)
        print(f"Census data loaded: {census_gdf.shape[0]} records")
        print(census_gdf.head())

        print(f"Loading heat data from {topical_data_path}")
        heat_df = pd.read_csv(topical_data_path, dtype={'GEOID': str})
        print(f"Heat data loaded: {heat_df.shape[0]} records")
        print(heat_df.head())

        print("Ensuring GEOID columns have the same data type and padding with leading zeros")
        census_gdf['GEOID'] = census_gdf['GEOID'].astype(str).str.zfill(11)
        heat_df['GEOID'] = heat_df['GEOID'].astype(str).str.zfill(11)

        print("Performing the join on GEOID")
        joined_gdf = census_gdf.merge(heat_df, on='GEOID', how='left')
        print(f"Joined data: {joined_gdf.shape[0]} records")
        print(joined_gdf.head())

        print(f"Saving joined data to {temp_output_geojson_path}")
        joined_gdf.to_file(temp_output_geojson_path, driver='GeoJSON')
        print("Join and save successful.")

    except Exception as e:
        print(f"An error occurred while joining heat data to census tracts: {e}")
	

# "Medium": "#403e83",

# "Below County Average (option b)": "#C3B6E8" alt, old #9190bf
# alt_road_gdf_color (option b) b2b5b8 old #eaeaea

map_configs = {
	"heat": {
		"value_field": "categorical_average",
		"color_mapping": {
			"Zero Day Count": COLOR_ZERO_DAY_COUNT,
			"Below/Equal Average": COLOR_BELOW_EQUAL_AVERAGE,
			"Above Average": COLOR_ABOVE_AVERAGE
		},
		"legend_mapping": {
			"Zero Day Count": "Zero Days",
			"Below/Equal Average": "Below Average",
			"Above Average": "Above Average"
		},
		"state_average_field": "avgDays_90F_state",
		"county_average_field": "avgDays_90F_county",
		"join_data_func": join_heat_data_to_census  # Using the same function for now
	},
	"air_pollution": {
		"value_field": "categorical_average",  # assuming this field exists
		"color_mapping": {
			"Below County Average": "#C3B6E8",
			"Above County Average": "#100e48"
		},
		"legend_mapping": {
			"Below County Average": "Below County Avg.",
			"Above County Average": "Above County Avg."
		},
		"state_average_field": "avgPM25_state_avg",
		"county_average_field": "avgPM25_county_avg",
		"join_data_func": join_heat_data_to_census  # or another function if needed
	}
}
def adjust_bounds_preserve_fixed_edge(bounds, desired_ratio, preserve='miny'):
	"""
	Adjust the bounds to have the exact desired_ratio (width/height) without recentering.
	Instead, preserve the specified edge ('miny' or 'minx') and extend the opposite side.
	
	For example, if preserve == 'miny', the lower bound (miny) remains unchanged and the
	upper bound is increased as needed.
	"""
	minx, miny, maxx, maxy = bounds
	width = maxx - minx
	height = maxy - miny
	current_ratio = width / height

	if current_ratio < desired_ratio:
		# Width is too narrow relative to height; need to increase width.
		new_width = desired_ratio * height
		if preserve == 'minx':
			new_maxx = minx + new_width
			return (minx, miny, new_maxx, maxy)
		elif preserve == 'maxx':
			new_minx = maxx - new_width
			return (new_minx, miny, maxx, maxy)
		else:
			# Default: preserve the left edge.
			new_maxx = minx + new_width
			return (minx, miny, new_maxx, maxy)
	elif current_ratio > desired_ratio:
		# Height is too short relative to width; increase height.
		new_height = width / desired_ratio
		if preserve == 'miny':
			new_maxy = miny + new_height
			return (minx, miny, maxx, new_maxy)
		elif preserve == 'maxy':
			new_miny = maxy - new_height
			return (minx, new_miny, maxx, maxy)
		else:
			# Default: preserve the bottom edge.
			new_maxy = miny + new_height
			return (minx, miny, maxx, new_maxy)
	else:
		# Already matches
		return bounds

def apply_special_adjustments(county, bounds):
	"""
	Adjust the bounds based on special adjustments for the given county.
	
	Returns a tuple of (adjusted_bounds, adjustment_applied) where adjustment_applied is True
	if any special adjustment was applied.
	
	Special adjustments can include:
	  - 'shift_y': adds extra padding at the bottom (subtracts from y_min)
	  - 'shift_x': shifts the x bounds (added to both x_min and x_max)
	  - 'zoom_factor': rescales the bounds about the center
	"""
	special_adjustments = {
		"Kings": {"shift_y": 20000, "zoom_factor": 0.7},
		"Los Angeles": {"shift_y": 40000, "zoom_factor": 0.9},
		"Merced": {"shift_y": 35000},
		"San Diego": {"shift_y": 50000},
		"Sacramento": {"shift_y": 15000, "zoom_factor": 0.8},
		"San Joaquin": {"shift_y": 35000, "zoom_factor": 0.8},
		# "San Mateo": {"shift_y": 1000, "shift_x": 2000},
		"Monterey": {"shift_y": 15000, "zoom_factor": 0.8},
		"Stanislaus": {"shift_y": 3000},
		"Ventura": {"shift_y": 5000, "zoom_factor": 0.75}
	}
	
	# Use default values if no adjustment is provided.
	defaults = {"shift_y": 0, "shift_x": 0, "zoom_factor": 1}
	adj = special_adjustments.get(county, defaults)
	adjustment_applied = (adj.get("shift_y", 0) != 0 or adj.get("shift_x", 0) != 0 or adj.get("zoom_factor", 1) != 1)
	
	minx, miny, maxx, maxy = bounds
	# Apply shift adjustments with defaults
	miny -= adj.get("shift_y", 0)
	minx += adj.get("shift_x", 0)
	maxx += adj.get("shift_x", 0)
	
	# Only apply zoom if needed
	if adj.get("zoom_factor", 1) != 1:
		factor = adj.get("zoom_factor", 1)
		x_center = (minx + maxx) / 2
		y_center = (miny + maxy) / 2
		width = (maxx - minx) / factor
		height = (maxy - miny) / factor
		minx = x_center - width / 2
		maxx = x_center + width / 2
		miny = y_center - height / 2
		maxy = y_center + height / 2
	
	return (minx, miny, maxx, maxy), adjustment_applied



def generate_majority_tracts_map(
    geojson_path,
    pop_data_path,  # Keeping the argument but not using it
    county_geojson_path,
    output_dir,
    basemap_source=ctx.providers.CartoDB.PositronNoLabels,
    label_layer=ctx.providers.CartoDB.PositronOnlyLabels,
    zoom=10,
    dpi=150,  # Increased dpi for better resolution
    map_type=None,
    topical_data_path=None,  # Renamed from heat_data_path
    population_filter=None,
    road_data_path=None,
    county_filter=None
):
    try:
        config = map_configs.get(map_type, {})
        value_field = config.get("value_field", "categorical_average")
        colors = config.get("color_mapping", {
            "Zero Day Count": COLOR_ZERO_DAY_COUNT,
            "Below/Equal Average": COLOR_BELOW_EQUAL_AVERAGE,
            "Above Average": COLOR_ABOVE_AVERAGE
        })
        legend_mapping = config.get("legend_mapping", {
            "Zero Day Count": "Zero Days",
            "Below/Equal Average": "Below Average",
            "Above Average": "Above Average"
        })
        state_avg_field = config.get("state_average_field", "avgDays_90F_state")
        county_avg_field = config.get("county_average_field", "avgDays_90F_county")
        join_func = config.get("join_data_func")

        print(f"Loading GeoJSON data from {geojson_path}")
        gdf = gpd.read_file(geojson_path)
        print(f"GeoJSON data loaded: {gdf.shape[0]} records")
        print(gdf.head())

        if map_type and topical_data_path:
            print(f"Loading {map_type} data from {topical_data_path}")
            topical_df = pd.read_csv(topical_data_path, dtype={'GEOID': str})
            print(f"{map_type.capitalize()} data loaded: {topical_df.shape[0]} records")
            print(topical_df.head())

        print(f"Loading county boundaries from {county_geojson_path}")
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

        print(f"Loading roads data from {road_data_path}")
        roads_gdf = gpd.read_file(road_data_path)
        print(f"Roads data loaded: {roads_gdf.shape[0]} records")
        print(roads_gdf.head())

        print("Ensuring the columns used for joining have the same data type and padding GEOID with leading zeros")
        gdf['GEOID'] = gdf['GEOID'].astype(str).str.zfill(11)
        if map_type and topical_data_path:
            topical_df['GEOID'] = topical_df['GEOID'].astype(str).str.zfill(11)
        
        temp_output_geojson_path = 'output/temp_joined_data.geojson'
        join_func(geojson_path, topical_data_path, temp_output_geojson_path)
        
        print("Loading joined data from temporary file")
        joined_gdf = gpd.read_file(temp_output_geojson_path)
        print(f"Joined data loaded: {joined_gdf.shape[0]} records")
        print(joined_gdf.head())

        print("Reprojecting to Web Mercator (EPSG:3857)")
        joined_gdf = joined_gdf.to_crs(epsg=3857)
        counties_gdf = counties_gdf.to_crs(epsg=3857)
        roads_gdf = roads_gdf.to_crs(epsg=3857)

        print("Getting unique counties")
        if county_filter:
            counties = [county_filter]
        else:
            counties = joined_gdf['County'].dropna().unique()
        print(f"Counties to process: {counties}")

        state_average = counties_gdf[state_avg_field].iloc[0]
        print(f"State Average from Google Sheet (rounded to 1 decimal): {state_average:.0f}")
        county_average = counties_gdf[county_avg_field].iloc[0]
        for county in counties:
            try:
                print(f"Processing county: {county}")
                if 'County' not in joined_gdf.columns:
                    print(f"Column 'County' not found in joined_gdf")
                    continue
                county_gdf = joined_gdf[joined_gdf['County'] == county]
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
                county_average = counties_gdf[counties_gdf['name'] == county][county_avg_field].values[0]
                print(f"County Average from Google Sheet: {county_average:.0f}")

                # Get the matching county shape
                county_shape = counties_gdf[counties_gdf['name'] == county]

                # Calculate figsize based on aspect ratio similar to 590x760 (~0.776)
                aspect_ratio = 387 / 507  # ≈0.776
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

                # Plot all areas
                for label, color in colors.items():
                    mask = county_gdf[value_field] == label
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
                                label=legend_mapping.get(label, label),
                                alpha=0.6
                            )
                        )

                # Plot dissolved Latino areas with a darker border and light hatch marks
                for label, color in colors.items():
                    mask = dissolved_latino_gdf[value_field] == label
                    if not dissolved_latino_gdf[mask].empty:
                        dissolved_latino_gdf[mask].plot(
                            ax=ax,
                            color='none',
                            edgecolor='#333333',
                            linewidth=1.0,
                            alpha=0.9,
                            zorder=6
                        )
                        dissolved_latino_gdf[mask].plot(
                            ax=ax,
                            color='none',
                            edgecolor='#FFB347',
                            linewidth=0.5,
                            alpha=0.6,
                            hatch='//',
                            zorder=7
                        )

                # Plot areas with no data in light gray
                no_data_gdf = county_gdf[county_gdf[value_field].isna()]
                print(f"No data records: {no_data_gdf.shape[0]}")
                no_data_gdf.plot(
                    ax=ax,
                    color='#d9d9d9',
                    edgecolor='lightgray',
                    linewidth=0.5,
                    alpha=0.6
                )

                # Plot roads with increased linewidth and a prominent color
                roads_gdf.plot(
                    ax=ax,
                    color='#b2b5b8',  # Change to a more prominent color
                    linewidth=1,  # Increase the linewidth
                    alpha=0.7,
                    zorder=2
                )

                # 1. Get the raw bounds and apply your special adjustments.
                raw_bounds = county_gdf.total_bounds  # (minx, miny, maxx, maxy)
                adjusted_bounds, adjustments_applied = apply_special_adjustments(county, raw_bounds)
                minx, miny, maxx, maxy = adjusted_bounds

                # 2. Then, enforce the desired aspect ratio.
                desired_ratio = aspect_ratio  # e.g., 387/507
                current_ratio = (maxx - minx) / (maxy - miny)

                if current_ratio > desired_ratio:
                    # The map is too wide; fix x limits and adjust y limits.
                    expected_height = (maxx - minx) / desired_ratio
                    y_center = (miny + maxy) / 2
                    new_miny = y_center - expected_height / 2
                    new_maxy = y_center + expected_height / 2
                    ax.set_xlim(minx, maxx)
                    ax.set_ylim(new_miny, new_maxy)
                else:
                    # The map is too tall; fix y limits and adjust x limits.
                    expected_width = (maxy - miny) * desired_ratio
                    x_center = (minx + maxx) / 2
                    new_minx = x_center - expected_width / 2
                    new_maxx = x_center + expected_width / 2
                    ax.set_xlim(new_minx, new_maxx)
                    ax.set_ylim(miny, maxy)

                ax.set_aspect('equal')
                ax.axis('off')
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
                            label=f'County Average: {county_average:.0f}'
                        )
                    )
                    legend_elements.append(
                        Patch(
                            facecolor='none',
                            edgecolor='none',
                            label=f'State Average: {state_average:.0f}'
                        )
                    )
                    # legend = ax.legend(
                    #     handles=legend_elements,
                    #     loc='upper right',
                    #     title='Number Extreme Heat Days',
                    #     frameon=True
                    # )
                    # legend.set_zorder(10)  # Ensure legend is on top

                # Add Basemap Layers
                ctx.add_basemap(ax, source=basemap_source, zoom=zoom)
                # ctx.add_basemap(ax, source=label_layer, zoom=zoom)

                # Load custom city labels GeoJSON
                cities_gdf = gpd.read_file('inputs/geojson/ca_incorprated_cities.geojson')
                cities_gdf = cities_gdf.to_crs(epsg=3857)
                county_shape_geom = county_shape.unary_union
                cities_in_county = cities_gdf[cities_gdf.geometry.centroid.within(county_shape_geom)]

                # Load lexend custom font with increased size
                lexend = FontProperties(fname="static/fonts/Lexend-Regular.ttf", size=12)

                # Sort the cities so major cities come first.
                cities_sorted = sorted(
                    cities_in_county.iterrows(),
                    key=lambda x: 0 if x[1].get('name', 'Unknown') in MAJOR_CITIES else 1
                )

                # ...
                placed_bboxes = []
                # Precompute title-case versions of MAJOR_CITIES for the overlap check.
                major_cities_title = [name.title() for name in MAJOR_CITIES]

                for idx, row in cities_sorted:
                    x, y = row.geometry.centroid.x, row.geometry.centroid.y
                    # Capitalize all words even after spaces.
                    city_name = row.get('name', 'Unknown').title()
                    # Determine font size based on whether the city is major or not.
                    fontsize = 10 if city_name in major_cities_title else 9
                    # Set lower zorder so labels appear under the colored layers.
                    z_order = 10
                    text = ax.text(
                        x, y, city_name,
                        fontproperties=lexend,  # Custom font
                        fontsize=fontsize,
                        fontweight='bold',
                        ha='center',
                        va='center',
                        alpha=1,  # Alpha for the text
                        color='#5C666F',  # Hex color for rgb(92,102,111,255)
                        zorder=z_order
                    )

                    # Apply two path effects: an outer white halo and an inner stroke (same color as text)
                    text.set_path_effects([
                        PathEffects.withStroke(linewidth=2, foreground='white', alpha=1),
                        PathEffects.Normal()
                    ])
                    # Get the rendered bounding box for the text and expand it (50% in all directions)
                    bbox = text.get_window_extent(renderer=fig.canvas.get_renderer())
                    padded_bbox = bbox.expanded(1.5, 1.5)

                    overlap = False
                    for other_bbox in placed_bboxes:
                        if padded_bbox.overlaps(other_bbox):
                            overlap = True
                            break

                    # If overlapping and the label is not a major city, hide it.
                    if overlap and city_name not in major_cities_title:
                        text.set_visible(False)
                    else:
                        placed_bboxes.append(padded_bbox)
                # Save the figure for the current county
                output_path = os.path.join(output_dir, f'{county}_map.png')
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
                print(f"An error occurred while processing county {county}: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")