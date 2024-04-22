# Generates tiles along a polyline from the input SHP file.
# Define the "buffer_width" - the width of the tile in meters - and "distance_between_points" - the approximate length of the tile along the polyline - in code below.
# Note that if the polyline is very twisty then theresults will need to be checked manually.


import geopandas as gpd
from shapely.geometry import LineString, Point, MultiLineString, Polygon
from shapely.ops import unary_union, split
import numpy as np

line_gdf = gpd.read_file('polyline.shp')
buffer_width = 60  
distance_between_points = 600

# Function to create a perpendicular line to the line at the point
def create_perpendicular_line(line, point, length):
    # Check if line is a MultiLineString and convert to LineString if needed
    if isinstance(line, MultiLineString):
        # Convert MultiLineString to list of LineStrings
        line_strings = list(line.geoms)
        # Find the line segment within the MultiLineString that is closest to the point
        closest_segment = min(
            line_strings,
            key=lambda seg: seg.distance(point)
        )
    else:
        # If 'line' is not a MultiLineString, it assumes 'line' is already a LineString
        closest_segment = line

    # Now, line is guaranteed to be a LineString
    line_coords = closest_segment.coords

    for i in range(len(line_coords) - 1):
        segment = LineString([line_coords[i], line_coords[i+1]])
        if segment.distance(point) < 1e-8:
            # Calculate the angle of the line
            angle = np.arctan2(segment.coords[1][1] - segment.coords[0][1], 
                               segment.coords[1][0] - segment.coords[0][0])
            # Create a perpendicular angle
            perp_angle = angle + np.pi / 2
            # Define the end points of the perpendicular line
            dx = length * np.cos(perp_angle)
            dy = length * np.sin(perp_angle)
            p1 = Point(point.x - dx, point.y - dy)
            p2 = Point(point.x + dx, point.y + dy)
            return LineString([p1, p2])


# Buffer the line to create the area polygon
line = line_gdf.unary_union
buffer_polygon = line.buffer(buffer_width)

# Create points along the line at equal intervals of its total length
num_points = int(line.length / distance_between_points) + 1
points_along_line = [line.interpolate(float(n)/num_points, normalized=True) for n in range(num_points)]

# Create perpendicular cutting lines
cutting_lines = [create_perpendicular_line(line, point, buffer_width * 2) for point in points_along_line]

# Use the cutting lines to split the buffer polygon
split_polygons = [buffer_polygon]
for cutting_line in cutting_lines:
    new_split_polygons = []
    for poly in split_polygons:
        # Perform the split operation
        split_result = split(poly, cutting_line)
        # Check if the split result is not empty and is a GeometryCollection
        if split_result.is_empty:
            continue
        if "GeometryCollection" in split_result.geom_type:
            # Iterate over each geometry in the GeometryCollection
            for geom in split_result.geoms:
                if isinstance(geom, Polygon):  
                    new_split_polygons.append(geom)
        else:
            # If split_result is not a GeometryCollection (it's a single geometry), handle it directly
            if isinstance(split_result, Polygon):
                new_split_polygons.append(split_result)

    split_polygons = new_split_polygons  


# Filter out small erroneous pieces
split_polygons = [poly for poly in split_polygons if poly.area > buffer_width * distance_between_points / 2]

# Convert the polygons to a GeoDataFrame
multi_gdf = gpd.GeoDataFrame({'geometry': split_polygons}, crs=line_gdf.crs)

# Save the result to a shapefile
multi_gdf.to_file('tiled_multipolygons.shp')
