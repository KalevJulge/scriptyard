# Cut out a section of equirectangular images and create a video with specific resolution and fps based on consecutive images.
# Change the processing settings as needed.
# Install OpenCV in conda environment "conda install -c conda-forge opencv"

import cv2
import os
import numpy as np
import time

input_folder = 'equirectangular'
output_folder = 'video'
resized_images_folder = os.path.join(output_folder, '1280x1024') 
fps = 6
horizontal_fov_deg = 90
vertical_fov_deg = 45
horizontal_rotation_deg = 180
input_resolution = (8192, 4096)
output_resolution = (1280, 1024)

def rotate_and_extract_fov(image, horizontal_fov_deg, vertical_fov_deg, horizontal_rotation_deg, input_resolution, output_resolution):
    output_aspect_ratio = output_resolution[0] / output_resolution[1]
    input_aspect_ratio = input_resolution[0] / input_resolution[1]
    horizontal_fov_deg_adjusted = horizontal_fov_deg * (output_aspect_ratio / input_aspect_ratio)

    rotation_shift = int((horizontal_rotation_deg / 360.0) * image.shape[1])
    rotated_image = np.roll(image, shift=rotation_shift, axis=1)

    width, height = image.shape[1], image.shape[0]
    horizontal_fov_rad = np.radians(horizontal_fov_deg_adjusted)
    vertical_fov_rad = np.radians(vertical_fov_deg)

    cutout_width = int(width * (horizontal_fov_rad / (2 * np.pi)))
    cutout_height = int(height * (vertical_fov_rad / np.pi))

    start_x = (width - cutout_width) // 2
    start_y = (height - cutout_height) // 2

    cutout = rotated_image[start_y:start_y+cutout_height, start_x:start_x+cutout_width]
    return cutout

def resize_image(image, output_resolution):
    return cv2.resize(image, output_resolution, interpolation=cv2.INTER_LINEAR)

def save_resized_image(image, name, folder):
    cv2.imwrite(os.path.join(folder, name), image)

def process_images_and_create_video(input_folder, output_folder, fps, horizontal_fov_deg, vertical_fov_deg, horizontal_rotation_deg, input_resolution, output_resolution):
    if not os.path.exists(resized_images_folder):
        os.makedirs(resized_images_folder)

    start_process_time = time.time()
    images = sorted([img for img in os.listdir(input_folder) if img.endswith(".jpg")])
    print(f"Found {len(images)} images to process.")

    video_writer = None
    video_path = os.path.join(output_folder, f"Video_{output_resolution[0]}x{output_resolution[1]}.mp4")

    processed_count = 0
    for image_name in images:
        image_path = os.path.join(input_folder, image_name)
        image = cv2.imread(image_path)
        if image is None:
            print(f"Skipping file: {image_name}")
            continue

        cutout = rotate_and_extract_fov(image, horizontal_fov_deg, vertical_fov_deg, horizontal_rotation_deg, input_resolution, output_resolution)
        resized_cutout = resize_image(cutout, output_resolution)
        save_resized_image(resized_cutout, image_name, resized_images_folder)
        processed_count += 1

        if video_writer is None:
            print("Initializing video creation...")
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(video_path, fourcc, fps, output_resolution)

        video_writer.write(resized_cutout)

    if video_writer:
        video_writer.release()
        print(f"Video saved to {video_path} with {processed_count} frames.")
    print(f"Processing completed in {time.time() - start_process_time:.2f} seconds.")

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

process_images_and_create_video(input_folder, output_folder, fps, horizontal_fov_deg, vertical_fov_deg, horizontal_rotation_deg, input_resolution, output_resolution)
