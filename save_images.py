import sys
from pdf2image import convert_from_path
import os
import time
from argparse import ArgumentParser

def pdf_to_jpg(pdf_path, output_prefix, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert PDF to a list of images
    images = convert_from_path(pdf_path)
    
    # Save images with the given prefix in the specified directory
    for i, image in enumerate(images):
        image_name = os.path.join(output_dir, f"{output_prefix}_{i+1}.jpg")
        image.save(image_name, 'JPEG')
        print(f"Saved {image_name}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python pdf_to_jpg.py <pdf_path> <output_prefix> <output_dir>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_prefix = sys.argv[2]
    output_dir = sys.argv[3]
    
    if not os.path.exists(pdf_path):
        print(f"Error: The file {pdf_path} does not exist.")
        sys.exit(1)
    
    pdf_to_jpg(pdf_path, output_prefix, output_dir)
    print("PDF conversion to JPG completed.")