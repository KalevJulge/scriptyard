# Interpolates and applies XYZ corrections to point cloud points based on timestamps.
# Can be used to align overlapping point clouds.
# Measure the shifts and note down the timestamps at intersections using point cloud visualization tool (e.g. CloudCompare).
# There can be more than 2 corrections. Just add more columns.

import laspy
import numpy as np
import os
from scipy.interpolate import interp1d


input_dir = 'laz_in'
output_dir = 'laz_out'
corrections = {
    'timestamps': [1706468131, 1706468603],  
    'x_shifts': [0.40, 0.38], 
    'y_shifts': [0.32, 3.17],  
    'z_shifts': [-0.75, -2.15],  
}

def interpolate_shifts(gps_times, corrections):
    timestamps = corrections['timestamps']
    x_shifts = corrections['x_shifts']
    y_shifts = corrections['y_shifts']
    z_shifts = corrections['z_shifts']
    
    interpolate_x = interp1d(timestamps, x_shifts, fill_value="extrapolate")
    interpolate_y = interp1d(timestamps, y_shifts, fill_value="extrapolate")
    interpolate_z = interp1d(timestamps, z_shifts, fill_value="extrapolate")
    
    x_corrections = interpolate_x(gps_times)
    y_corrections = interpolate_y(gps_times)
    z_corrections = interpolate_z(gps_times)
    
    return x_corrections, y_corrections, z_corrections

def apply_corrections(input_dir, output_dir, corrections):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.endswith('.las') or filename.endswith('.laz'):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename)
            
            print(f"Processing {filename}...")
            las = laspy.read(input_file)
            
            if 'gps_time' not in las.point_format.dimension_names:
                print(f"'gps_time' dimension not found in {filename}. Skipping file.")
                continue
            
            gps_times = las.gps_time
            x_corrections, y_corrections, z_corrections = interpolate_shifts(gps_times, corrections)
            
            las.x += x_corrections
            las.y += y_corrections
            las.z += z_corrections
            
            las.write(output_file)
            print(f"Modified point cloud saved to {output_file}.")


apply_corrections(input_dir, output_dir, corrections)
