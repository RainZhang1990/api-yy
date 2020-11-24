import numpy as np
import time
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications.resnet import preprocess_input
from core.config import Config
import logging

import grpc
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc

def get_resnet101_feature_grpc(url,imgs,timeout=20):
    IMAGE_SHAPE = (224, 224)
    imgs=[np.array(img.resize(IMAGE_SHAPE)) for img in imgs]
    img_data = preprocess_input(np.array(imgs))

    channel=grpc.insecure_channel(url
        ,options=[('grpc.max_receive_message_length',2000*1024*1024)]
        # ,options=[('grpc.default_authority','sku_retrieval')]
        )
    stub=prediction_service_pb2_grpc.PredictionServiceStub(channel)
    request=predict_pb2.PredictRequest()
    request.model_spec.name='resnet101'
    request.model_spec.signature_name='serving_default'
    s0=time.time()
    request.inputs['input_1'].CopyFrom(tf.make_tensor_proto(img_data))
    s1=time.time()
    response=stub.Predict(request,timeout)
    logging.info('data copy time:{:.4f}s  inference time:{:.4f}s'.format(s1-s0,time.time()-s1))
    features=np.asarray(response.outputs['conv5_block3_out'].float_val)
    features=np.reshape(features,(len(img_data),-1))
    return features

def get_resnet101_feature_local(imgs):
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        tf.config.experimental.set_memory_growth(gpus[0], True)
    feat_extractor = keras.applications.ResNet101(
        weights='imagenet', include_top=False)

    IMAGE_SHAPE = (224, 224)
    imgs=[np.array(img.resize(IMAGE_SHAPE)) for img in imgs]
    img_data = preprocess_input(np.array(imgs))

    s1=time.time()
    features = feat_extractor.predict(img_data)
    features = np.array(features).reshape(len(imgs), -1)
    logging.info('inference time:{}'.format(time.time()-s1))
    return features