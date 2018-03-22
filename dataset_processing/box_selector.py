import cv2
import numpy as np


class BoundingBox(object):
    def __init__(self, object_type, x, y, x2, y2):
        self.type = object_type
        self.x = x
        self.y = y
        self.x2 = x2
        self.y2 = y2

    def __str__(self):
        return "[type={}, ({}, {}, {}, {})]".format(self.type,
                                                    self.x, self.y,
                                                    self.x2, self.y2)

    def __repr__(self):
        return self.__str__()


class BoxSelector(object):
    def __init__(self, image, window_name, color=(0, 0, 255)):
        # Store image and an original copy
        self.image = image
        self.orig = image.copy()

        # Capture start and end point co-ordinates
        self.start = None
        self.end = None

        # Flag to indicate tracking
        self.track = False
        self.color = color
        self.window_name = window_name

    def get_bounding_box(self):
        if self.start and self.end:
            pts = np.array([self.start, self.end])
            s = np.sum(pts, axis=1)
            (x, y) = pts[np.argmin(s)]
            (xb, yb) = pts[np.argmax(s)]
            return BoundingBox("door", x, y, xb, yb)
        return None

    def get_bounding_boxes(self):
        bounding_boxes = []
        # Hook callback to the named window
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        while True:
            key = cv2.waitKey(0)
            if key == ord('\n') or key == ord('\r'):
                return bounding_boxes
            elif key == ord('1'):
                bounding_boxes.append(self.get_bounding_box())
            else:
                return key

    def mouse_callback(self, event, x, y, flags, params):
        # Start tracking if left-button-clicked down
        if event == cv2.EVENT_LBUTTONDOWN:
            self.start = (x, y)
            self.track = True

        # Capture/end tracking while mouse-move or left-button-click released
        elif self.track and (event == cv2.EVENT_MOUSEMOVE or event == cv2.EVENT_LBUTTONUP):
            self.end = (x, y)
            if not self.start == self.end:
                self.image = self.orig.copy()
                # Draw rectangle on the image
                cv2.rectangle(self.image, self.start, self.end, self.color, 2)
                if event == cv2.EVENT_LBUTTONUP:
                    self.track = False

            # In case of clicked accidentally, reset tracking
            else:
                self.image = self.orig.copy()
                self.start = None
                self.track = False
            cv2.imshow(self.window_name, self.image)

