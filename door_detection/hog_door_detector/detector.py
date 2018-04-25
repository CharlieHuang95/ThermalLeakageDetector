import dlib
import cv2
import os
import numpy as np

class HOGDetector(object):
    def __init__(self, model_path="model"):
        # Load the trained detector (for testing)
        self._detector = dlib.simple_object_detector(model_path)

    def detect(self, image, annotate=False, show=False):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rectangles = self._detector(image)
        bounding_boxes = []
        for rect in rectangles:
            x, y, x2, y2 = rect.left(), rect.top(), rect.right(), rect.bottom()
            bounding_boxes.append([x, y, x2, y2])
            if annotate:
                cv2.rectangle(image, (x, y), (x2, y2), (0, 0, 255), 2)
                cv2.rectangle(image, (x, y), (x2, y2), (0, 0, 255), 2)
            if show:
                cv2.namedWindow("detected")
                cv2.imshow("detected", image)
                cv2.waitKey(0)
        return bounding_boxes


def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(50)#max(0, (1.0 - sigma) * v))
    upper = int(120)#min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged

if __name__ == "__main__":
    # Do a quick demo.

    detector = HOGDetector()
    for f in os.listdir("../../dataset/images/processed_images/"):
        image = cv2.imread(os.path.join("../../dataset/images/processed_images", f))
        bb = detector.detect(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if bb:
            for b in bb:
                width = b[2] - b[0]
                height = b[3] - b[1]
                w_delta = int(width / 4)
                h_delta = int(height / 4)
                bb_l = [max(0, b[0] - w_delta), max(0, b[1] - h_delta),
                        min(156, b[2] + w_delta), max(208, b[3] + h_delta)]
                subregion = image[bb_l[1]:bb_l[3], bb_l[0]:bb_l[2]]
                edge = auto_canny(subregion)
                minLineLength = int(len(subregion) / 4)
                maxLineGap = int(len(subregion) / 10)
                kernel = np.ones((3, 3), np.uint8)
                print(subregion.shape)
                edge = cv2.dilate(edge, kernel, iterations=1)
                lines = cv2.HoughLinesP(edge, 4, np.pi / 180, 20, minLineLength, maxLineGap)

                if lines is not None:
                    for line in lines:
                        print(line)
                        x1, y1, x2, y2 = line[0]
                        cv2.line(subregion, (x1, y1), (x2, y2), (0, 255, 0), 2)

                #cv2.rectangle(image, (b[0], b[1]), (b[2], b[3]), (0, 0, 255), 2)
                cv2.imwrite(os.path.join("../../dataset/images/door_detection/", f.split(".")[0] + "_sub.jpg"),
                            subregion)
                cv2.imwrite(os.path.join("../../dataset/images/door_detection/", f.split(".")[0] + "_edge.jpg"),
                            edge)

        cv2.imwrite(os.path.join("../../dataset/images/door_detection/", f), image)
        #cv2.imwrite(os.path.join("../../dataset/images/door_detection/", f.split(".")[0] + "_edge.jpg"), edge)
    test_image = cv2.imread("../../dataset/images/processed_images/img_thermal_1519937382264.jpg")
    print(detector.detect(test_image, annotate=True, show=True))
