# Converts panoramas with random aspect ratio to 2:1 (pseudo) equirectangular images.

from PIL import Image
import os
import glob

source_folder = 'panorama_original'
output_folder = 'panorama_equirectangular'

def add_black_borders(input_image_path, output_image_path):
    with Image.open(input_image_path) as img:
        width, height = img.size
        new_height = width // 2 
        new_img = Image.new("RGB", (width, new_height), "black")
        new_img.paste(img, (0, (new_height - height) // 2))
        new_img.save(output_image_path)

def process_folder(source_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for file_path in glob.glob(os.path.join(source_folder, '*.jpg')):
        filename = os.path.basename(file_path)
        output_path = os.path.join(output_folder, filename)
        add_black_borders(file_path, output_path)
        print(f"Processed {filename}")

process_folder(source_folder, output_folder)
