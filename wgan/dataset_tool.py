"""
Data organizing function: highly influenced by following script.
https://github.com/tkarras/progressive_growing_of_gans/blob/master/dataset_tool.py
"""

import os
from glob import glob
from time import time
from PIL import Image
import numpy as np
import tensorflow as tf


def raise_error(condition, msg):
    if condition:
        raise ValueError(msg)


def shuffle_data(data, seed=0):
    np.random.seed(seed)
    np.random.shuffle(data)
    return data


def tfrecord_parser(img_shape):
    def __tfrecord_parser(example_proto):
        features = dict(image=tf.FixedLenFeature([], tf.string, default_value=""))
        parsed_features = tf.parse_single_example(example_proto, features)
        feature_image = tf.decode_raw(parsed_features["image"], tf.uint8)
        feature_image = tf.cast(feature_image, tf.float32)
        image = tf.reshape(feature_image, img_shape)
        return image
    return __tfrecord_parser


class TFRecorder:
    """ Formatting data as TFrecord """

    def __init__(self,
                 dataset_name: str,
                 path_to_dataset: str,
                 tfrecord_dir: str,
                 print_progress: bool = True,
                 progress_interval: int = 10):

        # raise_error(dataset_name not in ['celeba', 'lsun'], 'unknown data: %s' % dataset_name)
        self.dataset_name = dataset_name
        self.path_to_dataset = path_to_dataset
        self.path_to_save = '%s/%s' % (tfrecord_dir, dataset_name)

        if not os.path.exists(tfrecord_dir):
            os.makedirs(tfrecord_dir, exist_ok=True)
        self.print_progress = print_progress
        self.progress_interval = progress_interval

    def my_print(self, *args, **kwargs):
        if self.print_progress:
            print(*args, **kwargs)

    def create(self,
               resize_value: int,
               crop_value: int = None):

        image_files = glob('%s/*.png' % self.path_to_dataset)
        image_files += glob('%s/*.jpg' % self.path_to_dataset)
        image_files = sorted(image_files)

        def write(image_filenames, name, mode):
            full_size = len(image_filenames)
            self.my_print('writing %s as tfrecord (%s): size %i' % (self.dataset_name, mode, full_size))
            compress_opt = tf.io.TFRecordOptions(tf.compat.v1.io.TFRecordCompressionType.GZIP)
            with tf.io.TFRecordWriter(name, options=compress_opt) as writer:
	    print("1")
                time_stamp = time()
                time_stamp_start = time()
	    print("2")
                for n, single_image_path in enumerate(image_filenames):
	        print(f"number {n}", end="\r")
                    # open as pillow instance
                    image = Image.open(single_image_path)
                    w, h = image.size
                    if crop_value is not None:
                        # cropping
                        upper = int(np.floor(h / 2 - crop_value / 2))
                        lower = int(np.floor(h / 2 + crop_value / 2))
                        left = int(np.floor(w / 2 - crop_value / 2))
                        right = int(np.floor(w / 2 + crop_value / 2))
                        image = image.crop((left, upper, right, lower))

                    # resize
                    image = image.resize((resize_value, resize_value))
                    img = np.asarray(image)

                    if img.shape != (resize_value, resize_value, 3):
                        self.my_print('%s: %s' % (str(img.shape), single_image_path))
                        img = img[:, :, :3]
                    img = np.rint(img).clip(0, 255).astype(np.uint8)

                    if n % self.progress_interval == 0:
                        progress_perc = n / full_size * 100
                        cl_time = time() - time_stamp
                        whole_time = time() - time_stamp_start
                        time_per_sam = cl_time / self.progress_interval
                        self.my_print('%s: %d / %d (%0.1f %%), %0.4f sec/image (%0.1f sec) \r'
                                      % (mode, n, full_size, progress_perc, time_per_sam, whole_time),
                                      end='', flush=True)
                        time_stamp = time()

                    ex = tf.train.Example(
                        features=tf.train.Features(
                            feature=dict(
                                image=tf.train.Feature(bytes_list=tf.train.BytesList(value=[img.tostring()]))
                            )))
                    writer.write(ex.SerializeToString())

        # apply full data
        if crop_value is not None:
            write(image_files, '%s-c%i-r%i.tfrecord' % (self.path_to_save, crop_value, resize_value), mode='full')
        else:
            write(image_files, '%s-r%i.tfrecord' % (self.path_to_save, resize_value), mode='full')

        # if validation_split is not None:
        #     raise_error(validation_split > 1, 'validation_split has to be in [0,1]')
        #
        #     # apply train data
        #     write(image_files[int(np.rint(len(image_files) * validation_split)):],
        #           '%s-train.tfrecord' % self.path_to_save, mode='train')
        #
        #     # apply test data
        #     write(image_files[:int(np.rint(len(image_files) * validation_split))],
        #           '%s-test.tfrecord' % self.path_to_save, mode='test')

