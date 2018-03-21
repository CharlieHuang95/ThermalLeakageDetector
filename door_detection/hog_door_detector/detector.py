import dlib
import cv2


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


if __name__ == "__main__":
    # Do a quick demo.
    detector = HOGDetector()
    test_image = cv2.imread("../../dataset/images/processed_images/img_thermal_1519937382264.jpg")
    print(detector.detect(test_image, annotate=True, show=True))
