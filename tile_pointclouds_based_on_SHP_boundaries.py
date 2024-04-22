# Tiles point clouds based on multipolygon boundaries.
# The tile filename is based on multypolygon "FID".
# It is possible to define the precision (scale) and the offset in LAS header for the output point clouds.
# PDAL probably needs a conda environment to install properly: "conda install -c conda-forge python-pdal".

import geopandas as gpd
import json
import os
from pdal import Pipeline
import time
import logging
import laspy
from laspy.file import File
from shapely.geometry import box

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

laz_dir = 'laz_tiles'
shp_path = 'tiled_multipolygons.shp'
tiles_gdf = gpd.read_file(shp_path)

pipelines = {}


def create_initial_pipeline_dict(polygon, output_filename):
    pipeline_json = {
        "pipeline": [
            {
                "type": "filters.crop",
                "polygon": polygon.wkt
            },
            {
                "type": "writers.las",
                "filename": output_filename,
                "scale_x": 0.001,  
                "scale_y": 0.001,  
                "scale_z": 0.001,  
                "offset_x": 400000,
                "offset_y": 4560000,  
                "offset_z": 0,  
            }
        ]
    }
    return pipeline_json


def get_las_bbox(las_path):
    las = laspy.read(las_path)
    min_pt = las.header.mins
    max_pt = las.header.maxs
    return box(min_pt[0], min_pt[1], max_pt[0], max_pt[1])


for idx, tile in tiles_gdf.iterrows():
    tile_fid = tile['FID']
    polygon = tile['geometry']
    output_filename = f"{tile_fid}.laz"
    pipelines[tile_fid] = create_initial_pipeline_dict(polygon, output_filename)


for tile_fid, pipeline_dict in pipelines.items():
    tile_polygon = tiles_gdf[tiles_gdf['FID'] == tile_fid].iloc[0]['geometry']  # Get the tile polygon based on FID
    tile_bbox = tile_polygon.envelope  # Get the bounding box of the tile
    for laz_file in os.listdir(laz_dir):
        if laz_file.endswith('.laz'):
            laz_path = os.path.join(laz_dir, laz_file)
            laz_bbox = get_las_bbox(laz_path) 
            if laz_bbox.intersects(tile_bbox):
                logging.info(f"Processing file: {laz_file} for tile number {tile_fid}")
                reader = {
                    "type": "readers.las",
                    "filename": laz_path
                }
                pipeline_dict["pipeline"].insert(0, reader)

for tile_fid, pipeline_dict in pipelines.items():
    logging.info(f"Writing tile number {tile_fid}")
    start_time = time.time()
    
    pipeline = Pipeline(json.dumps(pipeline_dict))
    pipeline.execute()
    
    end_time = time.time()
    logging.info(f"Finished writing tile {tile_fid}. Time taken: {end_time - start_time:.2f} seconds.")


logging.info("Point cloud tiling complete for all tiles.")

