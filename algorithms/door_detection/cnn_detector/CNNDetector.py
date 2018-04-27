import tensorflow as tf
import os
import json
import subprocess
from scipy.misc import imread, imresize
from scipy import misc
import sys
sys.path.append("/home/Charlie/ThermalLeakageDetector/algorithms/door_detection/cnn_detector/trainer")
from train import build_forward
from utils.annolist import AnnotationLib as al
from utils.train_utils import add_rectangles, rescale_boxes

import cv2
import argparse


class CNNDetector(object):
    def __init__(self, hypes_file):
        tf.reset_default_graph()
        #hypes_file = 'trainer/hypes.json'
        print(hypes_file)
        with open(hypes_file, 'r') as f:
            self.H = json.load(f)
        self.H["grid_width"] = int(self.H["image_width"] / self.H["region_size"])
        self.H["grid_height"] = int(self.H["image_height"] / self.H["region_size"])
        self.x_in = tf.placeholder(tf.float32, name='x_in', shape=[self.H['image_height'], self.H['image_width'], 3])
        if self.H['use_rezoom']:
            self.pred_boxes, pred_logits, self.pred_confidences, pred_confs_deltas, pred_boxes_deltas = build_forward(self.H, tf.expand_dims(self.x_in, 0), 'test', reuse=None)
            grid_area = self.H['grid_height'] * self.H['grid_width']
            self.pred_confidences = tf.reshape(tf.nn.softmax(tf.reshape(pred_confs_deltas, [grid_area * self.H['rnn_len'], 2])), [grid_area, self.H['rnn_len'], 2])
            if self.H['reregress']:
                self.pred_boxes = self.pred_boxes + pred_boxes_deltas
        else:
            pred_boxes, pred_logits, pred_confidences = build_forward(self.H, tf.expand_dims(self.x_in, 0), 'test', reuse=None)
    
        self.sess = tf.Session()
        saver = tf.train.Saver()
        self.sess.run(tf.global_variables_initializer())
        saver.restore(self.sess, "/home/Charlie/ThermalLeakageDetector/algorithms/door_detection/cnn_detector/trainer/output_model/thermal_window_setup_2018_04_27_05.15/save.ckpt-3200")

    def detect(self, image):
        pred_annolist = al.AnnoList()

        #true_annolist = al.parse(args.test_boxes)
        #data_dir = os.path.dirname(args.test_boxes)
        #image_dir = get_image_dir(args)
        #subprocess.call('mkdir -p %s' % image_dir, shell=True)

        orig_img = image[:,:,:3]
        img = imresize(orig_img, (self.H["image_height"], self.H["image_width"]))
        feed = {self.x_in: img}
        (np_pred_boxes, np_pred_confidences) = self.sess.run([self.pred_boxes, self.pred_confidences], feed_dict=feed)

        pred_anno = al.Annotation()
        pred_anno.imageName = "test"
        new_img, rects = add_rectangles(self.H, [img], np_pred_confidences, np_pred_boxes,
                                        use_stitching=True, rnn_len=self.H['rnn_len'], min_conf=0.2, tau=0.25, show_suppressed=False)

        pred_anno.rects = rects
        pred_anno.imagePath = "none"#os.path.abspath(data_dir)
        pred_anno = rescale_boxes((self.H["image_height"], self.H["image_width"]), pred_anno, orig_img.shape[0], orig_img.shape[1])
        pred_annolist.append(pred_anno)
        predictions = []
        for pred in pred_annolist:
            predictions.append([pred.rects[0].x1, pred.rects[0].y1, pred.rects[0].x2, pred.rects[0].y2])
            
        misc.imsave("test.jpg", new_img)
    	return predictions

        

if __name__ == '__main__':
    pass
