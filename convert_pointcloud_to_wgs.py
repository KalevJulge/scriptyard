# Converts Point Clouds from EPSG:3301 to WGS84.
# Run in an environment where PDAL is installed, e.g. Anaconda Prompt with 'conda install -c conda-forge pdal'.
# Does not convert EH2000 heights to ellipsoid heights!!!

import os
import json
from os.path import join
import pdal

input_directory = 'laz_original'
output_directory = 'laz_wgs84'
src_epsg_code = 'EPSG:3301' 
tgt_epsg_code = 'EPSG:4326'  

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

laz_files = [f for f in os.listdir(input_directory) if f.endswith('.laz')]

for laz_file in laz_files:
    input_path = join(input_directory, laz_file)
    output_path = join(output_directory, "wgs84_" + laz_file)
    
    pipeline_json = json.dumps(
        {
            "pipeline": [
                {
                    "type": "readers.las",
                    "filename": input_path
                },
                {
                    "type": "filters.reprojection",
                    "in_srs": src_epsg_code,
                    "out_srs": tgt_epsg_code
                },
                {
                    "type": "writers.las",
                    "filename": output_path,
                    "scale_x": 1e-7,
                    "scale_y": 1e-7,
                    "scale_z": 1e-3 
                }
            ]
        }
    )

    pipeline = pdal.Pipeline(pipeline_json)

    try:
        pipeline.execute()
        print(f"Conversion successful: {laz_file}")
    except RuntimeError as e:
        print(f"An error occurred: {e}")

print("Processing complete.")
