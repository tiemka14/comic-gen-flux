# lib/preprocess_img.py
"""
This script provides functions to preprocess images for LoRa training. It includes:

- preprocess_image: Loads an image, converts it to RGB, resizes while maintaining aspect ratio, pads to a specified size (centered), and saves as PNG.
- batch_preprocess_images: Applies preprocessing to all images in a directory, displaying a progress bar.

Intended for preparing datasets for machine learning workflows, ensuring consistent image size and format.
"""

import os
from PIL import Image
from rich.progress import Progress


def preprocess_image(input_path, output_path, size=(512, 512)):
    """
    Preprocesses an image for LoRa training:
    - Loads the image
    - Converts to RGB
    - Resizes while maintaining aspect ratio
    - Pads to the specified size (centered)
    - Saves as PNG

    Args:
        input_path (str): Path to the input image.
        output_path (str): Path to save the processed image.
        size (tuple): Desired output size (width, height).
    """
    img = Image.open(input_path).convert("RGB")
    img.thumbnail(size, Image.LANCZOS)

    # Create a new image with the desired size and paste the resized image centered
    new_img = Image.new("RGB", size, (255, 255, 255))
    left = (size[0] - img.width) // 2
    top = (size[1] - img.height) // 2
    new_img.paste(img, (left, top))
    new_img.save(output_path, format="PNG")


def batch_preprocess_images(input_dir, output_dir, size=(512, 512)):
    """
    Batch preprocess all images in a directory with a progress bar.

    Args:
        input_dir (str): Directory with input images.
        output_dir (str): Directory to save processed images.
        size (tuple): Desired output size.
    """
    os.makedirs(output_dir, exist_ok=True)
    image_files = [
        fname
        for fname in os.listdir(input_dir)
        if fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]
    with Progress() as progress:
        task = progress.add_task("Processing images...", total=len(image_files))
        for fname in image_files:
            in_path = os.path.join(input_dir, fname)
            out_path = os.path.join(output_dir, os.path.splitext(fname)[0] + ".png")
            preprocess_image(in_path, out_path, size)
            progress.update(task, advance=1)


# Example usage:
# batch_preprocess_images('raw_images', 'processed_images', size=(512, 512))
