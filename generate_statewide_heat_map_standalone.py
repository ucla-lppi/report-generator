"""
Generate a one-time statewide extreme heat map for California (standalone, does not use map_utils.py).
"""

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import os
from matplotlib.patches import Patch
import matplotlib.colors as mcolors

# Adjustable bottom padding for map output
BOTTOM_PAD_INCHES = 0.5  # Increase this value for more whitespace at the bottom

# File paths
geojson_path = 'inputs/geojson/ca_heat_county_bins.geojson'
county_geojson_path = 'inputs/geojson/ca_counties_simplified.geojson'
roads_path = 'inputs/geojson/ca_primary_secondary_roads.geojson'
output_dir = 'output/extreme_heat_final_maps'
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, 'california_extreme_heat.png')


# Load county-level heat data
print(f"Loading county-level heat bins from {geojson_path}")
gdf = gpd.read_file(geojson_path)
gdf = gdf.to_crs(epsg=3857)

# Plot
fig, ax = plt.subplots(1, 1, figsize=(12, 18), dpi=150)



# Plot counties by heat category
# color_mapping = {
# 	"0 Days Above 90°F": "#d3ebe0",
# 	"Below/Equal State Avg": "#55947A",
# 	"Above State Avg": "#10462e",
# }
color_mapping = {
	"0 Days Above 90°F": "#e7f4ee",
	"Below/Equal State Avg": "#a2c4b6",
	"Above State Avg": "#7c998c",
}
legend_mapping = {
	"0 Days Above 90°F": "Zero Days",
	"Below/Equal State Avg": "Below/Equal State Avg",
	"Above State Avg": "Above State Avg",
}

def blend_with_white(hex_color, alpha):
	rgb = mcolors.to_rgb(hex_color)
	blended = tuple([alpha * c + (1 - alpha) * 1.0 for c in rgb])
	return blended


for label, color in color_mapping.items():
	mask = gdf['categorical_avg_90F'] == label
	if not gdf[mask].empty:
		blended = blend_with_white(color, 0.8)
		gdf[mask].plot(ax=ax, color=color, edgecolor=color, linewidth=0.5, zorder=3)


# Dissolve Latino neighborhoods by county and plot with dense hatch
if 'Neighborhood_type_for_map' in gdf.columns:
	latino_mask = gdf['Neighborhood_type_for_map'] == 'Latino Neighborhood'
	if not gdf[latino_mask].empty:
		latino_dissolved = gdf[latino_mask].dissolve(by='County')
		latino_dissolved.plot(ax=ax, facecolor='none', edgecolor='#f2c530', linewidth=1.2, alpha=1.0, zorder=4, hatch='////')



## Expand y-axis extent downward by 10% before adding basemap
ymin, ymax = ax.get_ylim()
expand = (ymax - ymin) * 0.10
ax.set_ylim(ymin - expand, ymax)
# Add basemap after extent adjustment
ctx.add_basemap(ax, source=ctx.providers.CartoDB.PositronNoLabels, zoom=6)

# Only show hardcoded major cities, subtle labels, avoid overlap
MAJOR_CITIES = [
	"Los Angeles", "San Diego", "San Jose", "San Francisco", "Santa Barbara",
	"Fresno", "Sacramento", "Bakersfield", "Salinas","Eureka","Chico","Redding","Riverside","Coachella","Napa","South Lake Tahoe","Colusa","El Centro"
]

major_cities_title = [name.title() for name in MAJOR_CITIES]
import matplotlib.patheffects as PathEffects
try:
	cities_gdf = gpd.read_file('inputs/geojson/ca_incorprated_cities.geojson')
	cities_gdf = cities_gdf.to_crs(epsg=3857)
	# Filter to only major cities
	cities_gdf = cities_gdf[cities_gdf['name'].apply(lambda n: n in MAJOR_CITIES)]
	# Sort by MAJOR_CITIES order
	cities_gdf['sort_order'] = cities_gdf['name'].apply(lambda n: MAJOR_CITIES.index(n) if n in MAJOR_CITIES else 999)
	cities_sorted = cities_gdf.sort_values('sort_order').iterrows()
	for idx, row in cities_sorted:
		x, y = row.geometry.centroid.x, row.geometry.centroid.y
		city_name = row.get('name', 'Unknown').title()
		text = ax.text(
			x, y, city_name,
			fontsize=12,
			fontweight='normal',
			ha='center',
			va='center',
			alpha=1.0,
			color='black',
			zorder=11
		)
		text.set_path_effects([
			PathEffects.withStroke(linewidth=2, foreground='#FFFFFF', alpha=1.0),
			PathEffects.Normal()
		])
except Exception as e:
	print(f"City label plotting failed: {e}")



# Plot county boundaries (medium gray, moderate thickness) on top
gdf.dissolve(by='County').boundary.plot(ax=ax, linewidth=1, edgecolor="#5D605F73", alpha=0.45, zorder=10)

# Legend
legend_elements = [
	Patch(facecolor=color, edgecolor='none', label=legend_mapping[label], alpha=0.7)
	for label, color in color_mapping.items()
]
if 'Neighborhood_type_for_map' in gdf.columns:
	legend_elements.append(Patch(facecolor='none', edgecolor='black', label='Latino Neighborhood', hatch='////'))
# ax.legend(handles=legend_elements, loc='upper right', title='Number Extreme Heat Days', frameon=True)

ax.set_axis_off()
plt.tight_layout()
plt.savefig(output_file, bbox_inches='tight', pad_inches=0.1, dpi=150)
plt.close()
print(f"Statewide extreme heat map saved to {output_file}")
