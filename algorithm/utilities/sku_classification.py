from __future__ import absolute_import, division, print_function, unicode_literals

import matplotlib.pylab as plt
import tensorflow as tf
# tf.compat.v1.enable_eager_execution()

import tensorflow_hub as hub
from tensorflow.keras import layers

module = hub.Module("D:\chrome download\inception3")
IMAGE_SHAPE = (224, 224)

classifier = tf.keras.Sequential([
    hub.KerasLayer(module, input_shape=IMAGE_SHAPE+(3,))
])
 
import numpy as np
import PIL.Image as Image

grace_hopper = tf.keras.utils.get_file('image.jpg','https://storage.googleapis.com/download.tensorflow.org/example_images/grace_hopper.jpg')
grace_hopper = Image.open(grace_hopper).resize(IMAGE_SHAPE)
