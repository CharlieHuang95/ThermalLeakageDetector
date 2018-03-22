import numpy as np
import cv2
import argparse
from imutils.paths import list_images
import os
import pickle

from box_selector import BoxSelector, BoundingBox

class AnnotationHelper(object):
    """ This class is used to load and save annotations.
    This maintain a dictionary of {filename: bounding_boxes}
    """

    def __init__(self, file_name=None):
        self.annotations = {}
        if file_name is not None:
            self.load_annotations(file_name)

    def load_annotations(self, file_name):
        # Check that the file exists
        if not os.path.isfile(file_name):
            print("Error: Please provide a valid path to an annotations file.")
            return
        f = open(file_name, "rb")
        if self.annotations is not None or len(self.annotations) != 0:
            print("Warning: Overwriting current object's annotations data.")
        self.annotations = pickle.load(f)
        f.close()

    def save_annotations(self, file_name):
        if os.path.isfile(file_name):
            print("Warning: About to overwrite saved annotation data.")
        f = open(file_name, "wb")

        # Use protocol=2 for backwards compatibility with python2.7
        pickle.dump(self.annotations, f, 2)
        f.close()

    def print(self):
        if self.annotations is not None:
            print(self.annotations)

    def add_annotation(self, image_name, bounding_box):
        self.annotations[image_name] = bounding_box

    def __contains__(self, item):
        return item in self.annotations


def create_annotations(args):
    print("Press: 'q' to quit, 'n' to skip, '1-9' to label it of that class, '<Enter>' to move on.")
    annotation_helper = AnnotationHelper(args["annotations"])
    annotation_helper.print()
    # Loop through each image and collect annotations
    for image_path in list_images(args["dataset"]):
        image_name = image_path.split("/")[-1].split("\\")[-1]
        if image_name in annotation_helper and not args["redo"]:
            continue
        # Load image and create a BoxSelector instance
        image = cv2.imread(image_path)
        bs = BoxSelector(image, "Image")
        cv2.imshow("Image", image)
        bounding_boxes = bs.get_bounding_boxes()
        if bounding_boxes == ord('q'):
            break
        elif bounding_boxes == ord('n') or type(bounding_boxes) != list:
            continue
        annotation_helper.add_annotation(image_name, bounding_boxes)
    annotation_helper.save_annotations(args["annotations"])


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--dataset",
                    default="../dataset/images/processed_images/",
                    help="path to images dataset")
parser.add_argument("-a", "--annotations",
                    default="annotations",
                    help="path to save annotations")
parser.add_argument("-r", "--redo",
                    action="store_true",
                    help="redo ones that already have bounding box information")
args = vars(parser.parse_args())
create_annotations(args)


