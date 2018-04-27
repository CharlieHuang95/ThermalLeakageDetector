import leakage_detector

file_path = "/home/pi/Desktop/rpi_seekcamera_driver/data/test.png"
leakage = leakage_detector.process(file_path, append_os=False)