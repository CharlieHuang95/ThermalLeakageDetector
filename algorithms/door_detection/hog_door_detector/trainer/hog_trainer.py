import argparse
import dlib
import cv2
import numpy as np
import os
import sys
sys.path.append("../../../dataset_processing/")
from gather_annotations import AnnotationHelper


class HOGTrainer(object):
    def __init__(self, options=None):
        # Create detector options
        self.options = options
        if self.options is None:
            self.options = dlib.simple_object_detector_training_options()

    def fit(self, image_path, annotations, visualize=True, savePath=None):
        print("About to start training/fitting")
        images, annotations = prepare_images(image_path, annotations)
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
        self.evaluate(images, annotations)

    def evaluate(self, images, annotations):
        detector = dlib.simple_object_detector("door_hog_model")
        total = 0
        successful = 0
        difference_array = []
        for x in range(len(images)):
            image = images[x]
            annotation = annotations[x]
            gt = np.array([annotation[0].left(),
                           annotation[0].right(),
                           annotation[0].top(),
                           annotation[0].bottom()])
            boxes = detector(image)
            if len(boxes) > 1:
                continue
            total += 1
            if not boxes:
                # Failed to detect anything
                continue
            successful += 1
            for box in boxes:
                width = annotation[0].right() - annotation[0].left()
                height = annotation[0].bottom() - annotation[0].top()
                pred = np.array([float(box.left()),
                                 float(box.right()),
                                 float(box.top()),
                                 float(box.bottom())])
                diff = pred - gt
                diff[0] /= float(width)
                diff[1] /= float(width)
                diff[2] /= float(height)
                diff[3] /= float(height)
                difference_array.append(diff)
                pred = list(map(int, pred))
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                cv2.rectangle(image, (pred[0], pred[2]), (pred[1], pred[3]), (255, 0, 0))
                cv2.rectangle(image, (gt[0], gt[2]), (gt[1], gt[3]), (0, 255, 0))

                cv2.imwrite("eval/" + str(total) + ".jpg", image)
        difference_array = np.array(difference_array)

        print(np.mean(difference_array, axis=0))
        print("Total:", total)
        print("Successful:", successful)
        print("Success Rate:", float(successful) / total)


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
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
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
    hog_options = dlib.simple_object_detector_training_options()
    # The 'C' hyperparameter affects the SVM margins.
    # Larger values of C leads to small margins, and more false negatives
    # Smaller values of C leads to larger margins, and more false positives
    hog_options.C = 20
    trainer = HOGTrainer(hog_options)
    trainer.fit(args["images"], args["annotations"], visualize=True, savePath=args["output"])
