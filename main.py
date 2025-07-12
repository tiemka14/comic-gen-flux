# main.py
"""Batch preprocess images script.
This script preprocesses images for LoRa training by resizing, padding, and saving them in a specified format.
It uses the PIL library for image processing and loguru for logging.
"""
from loguru import logger

from lib.preprocess_img import batch_preprocess_images
from lib.create_pod_template import create_pod_template
from lib.deploy_pod import deploy_pod
import argparse
import os
from pathlib import Path
import time
import json
import runpod

log_dir = Path("log")
log_dir.mkdir(exist_ok=True)
logger.add(log_dir / "main.log", rotation="1 MB")


def parse_args():
    parser = argparse.ArgumentParser(description="Batch preprocess images.")
    parser.add_argument(
        "--input_dir", type=str, default="raw_img", help="Directory of input images"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="preprocessed_img",
        help="Directory to save preprocessed images",
    )
    parser.add_argument(
        "--target_size",
        type=int,
        nargs=2,
        default=[768, 768],
        help="Target size (width height)",
    )
    parser.add_argument(
        "--do_preprocess",
        action="store_true",
        help="Flag to control whether preprocessing is done",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.do_preprocess:
        logger.info("Starting image preprocessing script.")
        start_time = time.time()
        if not os.path.exists(args.input_dir):
            logger.error(f"Input directory '{args.input_dir}' does not exist.")
            exit(1)
        if not os.path.exists(args.output_dir):
            logger.info(
                f"Output directory '{args.output_dir}' does not exist. Creating it."
            )
            os.makedirs(args.output_dir)
            logger.info(f"Output directory '{args.output_dir}' created.")
        if not (
            len(args.target_size) == 2
            and all(isinstance(x, int) for x in args.target_size)
        ):
            logger.error("Target size must be a list of two integers (width, height).")
            exit(1)
        logger.info(
            f"Starting batch preprocessing of images from '{args.input_dir}' to '{args.output_dir}' with target size {args.target_size}."
        )
        batch_preprocess_images(
            args.input_dir, args.output_dir, tuple(args.target_size)
        )
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Batch preprocessing completed in {elapsed_time:.2f} seconds.")
        logger.info(f"Processed images saved to '{args.output_dir}'.")

    else:
        logger.info("Preprocessing skipped because --do_preprocess was not specified.")

    # If pod_template available, use it, otherwise create a new one
    pod_template_dir = Path("templates/pod_templates")
    if not pod_template_dir.exists() or not any(pod_template_dir.iterdir()):
        logger.info("No pod templates found. Creating a new pod template.")
        tmpl = create_pod_template()
        logger.info(f"Pod template created with ID: {tmpl['id']}")
    else:
        logger.info("Pod templates found. Using existing pod template.")
        tmpl_files = list(pod_template_dir.glob("*.json"))
        tmpl = json.loads(tmpl_files[0].read_text())
    logger.info(f"Using pod template ID: {tmpl['id']}")
    pod = deploy_pod(template_id=tmpl["id"], image_name=tmpl["imageName"])
    logger.info(f"Pod deployed with ID: {pod['id']} and status: {pod['desiredStatus']}")
    runpod.terminate_pod(pod["id"])
    logger.info(f"Pod with ID: {pod['id']} terminated successfully.")
