import tensorflow as tf
import os
import json
import subprocess
from scipy.misc import imread, imresize
from scipy import misc

from trainer.train import build_forward
from trainer.utils.annolist import AnnotationLib as al
from trainer.utils.train_utils import add_rectangles, rescale_boxes

import cv2
import argparse


class CNNDetector(object):
    def __init__(self):
        tf.reset_default_graph()
        hypes_file = 'trainer/hypes.json'
        with open(hypes_file, 'r') as f:
            H = json.load(f)
        H["grid_width"] = int(H["image_width"] / H["region_size"])
        H["grid_height"] = int(H["image_height"] / H["region_size"])
        x_in = tf.placeholder(tf.float32, name='x_in', shape=[H['image_height'], H['image_width'], 3])
        if H['use_rezoom']:
            pred_boxes, pred_logits, pred_confidences, pred_confs_deltas, pred_boxes_deltas = build_forward(H, tf.expand_dims(x_in, 0), 'test', reuse=None)
            grid_area = H['grid_height'] * H['grid_width']
            pred_confidences = tf.reshape(tf.nn.softmax(tf.reshape(pred_confs_deltas, [grid_area * H['rnn_len'], 2])), [grid_area, H['rnn_len'], 2])
            if H['reregress']:
                pred_boxes = pred_boxes + pred_boxes_deltas
        else:
            pred_boxes, pred_logits, pred_confidences = build_forward(H, tf.expand_dims(x_in, 0), 'test', reuse=None)
    
        self.sess = tf.Session()
        saver = tf.train.Saver()
        sess.run(tf.global_variables_initializer())
        saver.restore(sess, args.weights)

    def detect(self, image):
        pred_annolist = al.AnnoList()

        true_annolist = al.parse(args.test_boxes)
        data_dir = os.path.dirname(args.test_boxes)
        image_dir = get_image_dir(args)
        subprocess.call('mkdir -p %s' % image_dir, shell=True)

        orig_img = image[:,:,:3]
        img = imresize(orig_img, (H["image_height"], H["image_width"]), interp='cubic')
        feed = {x_in: img}
        (np_pred_boxes, np_pred_confidences) = sess.run([pred_boxes, pred_confidences], feed_dict=feed)

        pred_anno = al.Annotation()
        pred_anno.imageName = "test"
        new_img, rects = add_rectangles(H, [img], np_pred_confidences, np_pred_boxes,
                                        use_stitching=True, rnn_len=H['rnn_len'], min_conf=args.min_conf, tau=args.tau, show_suppressed=args.show_suppressed)

        pred_anno.rects = rects
        pred_anno.imagePath = os.path.abspath(data_dir)
        pred_anno = rescale_boxes((H["image_height"], H["image_width"]), pred_anno, orig_img.shape[0], orig_img.shape[1])
        pred_annolist.append(pred_anno)
        for pred in pred_annolist:
            pred.printContent()
        misc.imsave("test.jpg", new_img)
    return pred_annolist

        

if __name__ == '__main__':
    pass