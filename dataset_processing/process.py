import argparse
import cv2
import os

# Import modules in the local directory
from crop import crop_scale, crop_seek_logo, crop_location
from resize import resize


def main(args):
    # Double check that the directory exists
    directory = args["input_path"]
    if not os.path.isdir(directory):
        print("Please specify a valid path to your data set")
        return

    # Iterate through all files in the specified directory
    files_to_process = [f for f in os.listdir(directory)]
    for file_name in files_to_process:
        full_path = os.path.join(directory, file_name)
        image = cv2.imread(full_path)
        print("Processing", file_name)
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
args = vars(parser.parse_args())
main(args)

