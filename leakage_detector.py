import door_detection.hog_door_detector.detector as door_detector
import dataset_processing.label as label
import numpy as np
import cv2
import dataset_processing.parameters as parameters

HOG = door_detector.HOGDetector(os.path.dirname(os.path.realpath(_file_)) + "/door_detection/hog_door_detector/model")
pa = parameters.Parameters()

def process(image_path):
    image = cv2.imread(image_path)
    preds = HOG.detect(image)
    output_image_path = image_path.split('.')[0] + "_detected.jpeg"
    if len(preds)>0:
        preds = preds[0]
        preds *= np.array([156/960,206/1280,156/960,206/1280])
        preds = preds.astype(int)

        label.label(pa,image_path,preds[0],preds[2],preds[1],preds[3],im_name=output_image_path)
    return output_image_path

if __name__ == "__main__":
    process("dataset/images/raw_images/img_thermal_1519937382264.jpg")
