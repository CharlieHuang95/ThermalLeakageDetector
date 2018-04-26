import argparse
import dlib
import cv2
import os
import sys
sys.path.append("../../../dataset_processing/")
from gather_annotations import AnnotationHelper


class HOGTrainer(object):
    def __init__(self, options=None, loadPath=None):
        # Create detector options
        self.options = options
        if self.options is None:
            self.options = dlib.simple_object_detector_training_options()

    def fit(self, imagePaths, annotations, visualize=True, savePath=None):
        print("About to start training/fitting")
        images, annotations = prepare_images(imagePaths, annotations)
        self._detector = dlib.train_simple_object_detector(images, annotations, self.options)
        # Visualize HOG
        if visualize:
            win = dlib.image_window()
            win.set_image(self._detector)
            win.wait_until_closed()
            dlib.hit_enter_to_continue()
            cv2.waitKey(0)
            print("Ok")
        if savePath is not None:
            self._detector.save(savePath)


def prepare_images(images, annotations):
    annotations_array = []
    images_array = []
    annotation_helper = AnnotationHelper()
    annotation_helper.load_annotations(annotations)
    print(annotations)
    for name in annotation_helper.annotations:
        image_path = images + "/" + name
        if not os.path.exists(image_path):
            print("skip")
            continue
        image = cv2.imread(image_path, 0)
        #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        images_array.append(image)
        bb = annotation_helper.annotations[name][0]
        annotations_array.append([dlib.rectangle(left=int(bb.x), top=int(bb.y),
                                                 right=int(bb.x2), bottom=int(bb.y2))])
    return images_array, annotations_array


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--annotations",
                        default="../../../dataset_processing/dataset/annotations/annotations",
                        help="Path to annotations file")
    parser.add_argument("-i", "--images",
                        default="../../../dataset_processing/dataset/images/processed_images/",
                        help="Path to images")
    parser.add_argument("-o", "--output", default="door_hog_model", help="Output model")
    args = vars(parser.parse_args())
    trainer = HOGTrainer()
    trainer.fit(args["images"], args["annotations"], visualize=True, savePath=args["output"])
