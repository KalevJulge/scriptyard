# Applies a mask to images. 
# The mask.png file should be black and white where the black areas will be masked out and white areas will remain visible. 
# Ensure the image and the mask have the same dimensions.

import os
from PIL import Image

image_directory = 'images'
mask_file_path = 'mask.png'
output_directory = 'masked'

def apply_mask_to_images(image_dir, mask_path, output_dir):
    mask = Image.open(mask_path).convert("L")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for image_name in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_name)

        if image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            with Image.open(image_path) as image:
                if image.size != mask.size:
                    print(f"Skipping {image_name}: Image and mask sizes do not match.")
                    continue

                if image.mode != 'RGBA':
                    image = image.convert("RGBA")

                masked_image = Image.composite(image, Image.new("RGBA", image.size, (0, 0, 0, 0)), mask)

                if not image_path.lower().endswith('.png'):
                    masked_image = masked_image.convert("RGB")

                masked_image_path = os.path.join(output_dir, image_name)
                masked_image.save(masked_image_path)
                print(f"Mask applied to {image_name}, saved to {masked_image_path}")

apply_mask_to_images(image_directory, mask_file_path, output_directory)
