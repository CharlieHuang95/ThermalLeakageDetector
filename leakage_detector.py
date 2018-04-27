import algorithms.door_detection.hog_door_detector.detector as door_detector
import dataset_processing.label as label
import numpy as np
import cv2
import os
import dataset_processing.parameters as parameters
from object_types import ObjectTypes


os_path = os.path.dirname(os.path.realpath(__file__))
HOG = door_detector.HOGDetector(os_path + "/algorithms/door_detection/hog_door_detector/model")
pa = parameters.Parameters()

def process(image_path,append_os = True, output_image_path = None):

    if append_os:
        image_path = os_path + image_path
    image = cv2.imread(image_path)
    # TODO: Should get prediction on whether window or door

    '''cv2.imshow('im',image).
    cv2.waitKey(0)
    cv2.destroyAllWindows()'''
    
    if output_image_path is None: #just output in same folder
        output_image_path = image_path.split('.')[0] + "_detected.jpeg"
        
    preds = HOG.detect(image)    
    
    if len(preds)==0:
        cv2.imwrite(output_image_path,image)
        return ObjectTypes.DOOR, "DOOR FRAME NOT FOUND"

    preds = preds[0]
    preds *= np.array([156/960,206/1280,156/960,206/1280])
    preds = preds.astype(int)

    leak_type = label.label(pa,image_path,preds[0],preds[2],preds[1],preds[3],outpath=output_image_path)
    # TODO: replace object type with result of detection algorithm
    return ObjectTypes.DOOR, leak_type

def process_folder(folder_path):
    folder_path = os_path + folder_path
    print(folder_path)
    directory = os.fsencode(folder_path)
    for filename in os.listdir(directory):
        #imgpath = os.path.join(directory,filename)
        filename = str(filename)
    
        process(folder_path+'/'+filename[2:-1],append_os = False,\
                    output_image_path = folder_path+'/../labeled_images/'+filename[2:-1])
        #cv2.imwrite(folder_path+'/../processed_images/'+filename[2:-1],p)

if __name__ == "__main__":
    pass
    #process("/algorithms/dataset_processing/dataset/images/raw_images/img_thermal_1520017052918.jpg")
    #process("/algorithms/dataset_processing/dataset/images/raw_images/img_thermal_1520032189407.jpg")
    process("/algorithms/dataset_processing/dataset/images/raw_images/img_thermal_1520032406198.jpg")
    process_folder("/algorithms/dataset_processing/dataset/images/raw_images")
    
