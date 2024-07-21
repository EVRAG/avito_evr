import time
import sys
import os
import time
from argparse import ArgumentParser
import sys
from pdf2image import convert_from_path
 
def My_python_method(kwargs):
 
    disp_str = 'key: {} | value: {} | type: {}'
    for each_key, each_value in kwargs.items():
        formatted_str = disp_str.format(each_key, each_value, type(each_value))
        print(formatted_str)
 
    # keep the shell open so we can debug
    time.sleep(int(kwargs.get('delay')))

def pdf_to_jpg(kwargs):
    output_dir = 'downloaded_files_backup'

    pdf_path = kwargs.get('-i')
    output_prefix = kwargs.get('-2')
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert PDF to a list of images
    images = convert_from_path(pdf_path)
    
    # Save images with the given prefix in the specified directory
    for i, image in enumerate(images):
        image_name = os.path.join(output_dir, f"{output_prefix}_{i+1}.jpg")
        image.save(image_name, 'JPEG')
        print(f"Saved {image_name}")
 
# execution order matters -this puppy has to be at the bottom as our functions are defined above
if __name__ == '__main__':
    parser = ArgumentParser(description='A simple argument input example')
    parser.add_argument("-i", "--input", dest="in", help="an input string", required=True)
    parser.add_argument("-i2", "--input2", dest="in2", help="another input", required=True)    
     
    args = parser.parse_args()
    My_python_method(vars(args))
    pass
 
# example
# python .\cmd_line_python_args.py -i="a string" -i2="another string" -d=15
