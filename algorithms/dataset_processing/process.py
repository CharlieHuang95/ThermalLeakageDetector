import argparse
import cv2
import numpy as np
import os
import parameters
import helpers
from PIL import Image
from matplotlib import pyplot as plt

# Import modules in the local directory
from crop import crop_scale, crop_seek_logo, crop_location
from resize import resize, is_landscape

def string_to_int(string):
    for idx in range(len(string)):
        if string[idx] not in "-0123456789":
            return int(string[:idx])
    return int(string)

def main(args):
    pa = parameters.Parameters()
    # Double check that the directory exists
    directory = args["input_path"]
    if not os.path.isdir(directory):
        print("Please specify a valid path to your data set")
        return

    # Iterate through all files in the specified directory
    files_to_process = [f for f in os.listdir(directory)]
    for file_name in files_to_process:
        full_path = os.path.join(directory, file_name)
        image = cv2.imread(full_path, 0)
        print("Processing", file_name)
        #image = helpers.bilateral_filter(image,9,150,150)
        image_dict = {}
        if args["convert_to_temp"]:
            image_dict["low"],image_dict["high"] = helpers.read_scale(image,pa)
        if args["filter_scale"]:
            # TODO(charlie): implement
            pass
        else:
            image = crop_scale(image)

        if args["filter_seek_logo"]:
            # TODO(charlie): implement
            pass
        else:
            image = crop_seek_logo(image)

        if args["filter_location"]:
            # TODO(charlie): implement
            pass
        else:
            image = crop_location(image)

        image = resize(image)
        if args["convert_to_temp"]:
            abs_image = helpers.grayscale_to_temp(image,image_dict["low"],image_dict["high"])
            np.save(os.path.join(args["output_path"], file_name.split(".")[0]), abs_image)
        else:
            cv2.imwrite(os.path.join(args["output_path"], file_name), image)


parser = argparse.ArgumentParser()
parser.add_argument("--input_path", type=str,
                    default="../dataset/images/raw_images")
parser.add_argument("--output_path", type=str,
                    default="../dataset/images/processed_images")
parser.add_argument("--filter_scale",
                    help="Default is crop. Otherwise use advanced techniques \
                    to process the left side which has scaling information",
                    action="store_true")
parser.add_argument("--filter_seek_logo",
                    help="Default is crop. Otherwise use advanced techniques \
                    to process the seek logo on the bottom right side",
                    action="store_true")
parser.add_argument("--filter_location",
                    help="Default is crop. Otherwise use advanced techniques \
                    to process the top right side which has GPS data",
                    action="store_true")
parser.add_argument("--convert_to_temp",
                    help="Store a numpy array of floats with the values as \
                    degrees celcius",
                    action="store_true")

args = vars(parser.parse_args())
main(args)
