# Applies a xyz shift to all LAS/LAZ point clouds in a directory.

import laspy
import os

# Configuration
input_dir = 'laz'  
output_dir = 'laz_shifted'  
x_shift = -0.1  
y_shift = -0.8 
z_shift = 1.7 

def apply_xyz_shift(input_dir, output_dir, x_shift, y_shift, z_shift):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.las') or filename.endswith('.laz'):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename)
            
            print(f"Processing {filename}...")
            
            las = laspy.read(input_file)
            
            # Apply shifts
            las.x += x_shift
            las.y += y_shift
            las.z += z_shift
         
            las.write(output_file)
            
            print(f"Modified point cloud saved to {output_file}.")


apply_xyz_shift(input_dir, output_dir, x_shift, y_shift, z_shift)
