import cv2
import os


def standardize_names(path, type):
    counter = 0
    files = [file for file in os.listdir(path)]
    for file in files:
        os.rename(path + "/" + file, path + "/" + "temp3_" + str(counter) + ".jpg")
        counter += 1
    counter = 0
    for file in files:
        os.rename(path + "/" + "temp3_" + str(counter) + ".jpg", path + "/" + "temp4_" + str(counter) + ".jpg")
        counter += 1
    counter = 0
    for file in files:
        image = cv2.imread(path + "/" + "temp4_" + str(counter) + ".jpg")
        factor = 400.0 / float(len(image))
        image = cv2.resize(image, (int(factor * len(image[0])),
                                   int(factor * len(image))))
        cv2.imwrite(path + "/" + "door_" + str(counter) + ".jpg", image)
        os.remove(path + "/" + "temp4_" + str(counter) + ".jpg")
        counter += 1


if __name__ == "__main__":
    # We want to make sure it is all standardized names
    standardize_names("doors", "door")

