import geopandas as gpd

# Load the GeoJSON files
land_boundary = gpd.read_file('../inputs/geojson/california_land_boundary.geojson')
counties = gpd.read_file('../inputs/geojson/california_counties.geojson')

# Ensure the CRS (Coordinate Reference System) is the same
land_boundary = land_boundary.to_crs(counties.crs)

# Clip the counties to the land boundary
clipped_counties = gpd.clip(counties, land_boundary)

# Save the clipped counties to a new GeoJSON file
clipped_counties.to_file('../inputs/geojson/clipped_california_counties.geojson', driver='GeoJSON')