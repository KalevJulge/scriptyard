# Filters point clouds based on custom dimensions. In this case "Distance".

import laspy
import numpy as np
import os

input_dir = 'laz_original'
output_dir = 'laz_filtered'
dimension_name = 'Distance'  
min_value = 2.5  
max_value = 100  

def filter_laz_by_dimension(input_dir, output_dir, dimension_name, min_value, max_value):
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.las') or filename.endswith('.laz'):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename)
            
            print(f"Processing {filename}...")
            
            las = laspy.read(input_file)
            
            if dimension_name not in las.point_format.dimension_names:
                print(f"Dimension '{dimension_name}' not found in {filename}. Skipping file.")
                continue
            
            dimension_values = getattr(las, dimension_name)
            
            within_range_indices = np.where((dimension_values >= min_value) & (dimension_values <= max_value))[0]
            
            if len(within_range_indices) > 0:
                filtered_points = las[within_range_indices]
                
                filtered_points.write(output_file)
                
                print(f"Filtered point cloud saved to {output_file}.")
            else:
                print(f"No points within the specified range for {dimension_name} in {filename}. Skipping file.")


filter_laz_by_dimension(input_dir, output_dir, dimension_name, min_value, max_value)
