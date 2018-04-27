import numpy as np
import cv2
import argparse
import os
import pickle
import json
from random import shuffle

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

    def print_annotation(self):
        if self.annotations is not None:
            print(self.annotations)

    def add_annotation(self, image_name, bounding_boxes):
        self.annotations[image_name] = bounding_boxes

    def __contains__(self, item):
        return item in self.annotations

    def save_json(self, filename, train_percent=95):
        json_images = []
        for annotation in self.annotations:
            image_name = annotation
            bbs = self.annotations[annotation]
            rects = []
            for bb in bbs:
                bbox = dict([("x1", int(bb.x)),
                             ("y1", int(bb.y)),
                             ("x2", int(bb.x2)),
                             ("y2", int(bb.y2))])
                rects.append(bbox)
            json_image = dict([("image_path", image_name),
                               ("rects", rects)])
            json_images.append(json_image)

        train_file = open("annotations/train.json", "w")
        test_file = open("annotations/test.json", "w")
        shuffle(json_images)
        sep = int((train_percent / 100.0) * len(json_images))
        train_images, test_images = json_images[:sep], json_images[sep:]
        train_file.write(json.dumps(train_images,
                                    indent=1))
        test_file.write(json.dumps(test_images,
                                   indent=1))
        train_file.close()
        test_file.close()


def create_annotations(args):
    print("Press: 'q' to quit, 'n' to skip, '1-9' to label it of that class, '<Enter>' to move on.")
    annotation_helper = AnnotationHelper(args["annotations"])
    annotation_helper.print_annotation()
    # Loop through each image and collect annotations
    for image_name in os.listdir(args["dataset"]):
        image_path = args["dataset"] + "/" + image_name
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dataset",
                        default="dataset/images/processed_images/",
                        help="path to images dataset")
    parser.add_argument("-a", "--annotations",
                        default="dataset/annotations/annotations",
                        help="path to save annotations")
    parser.add_argument("-r", "--redo",
                        action="store_true",
                        help="redo ones that already have bounding box information")
    args = vars(parser.parse_args())
    create_annotations(args)


