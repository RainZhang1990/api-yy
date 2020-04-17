import json
import time
import datetime
import requests
import json
import numpy as np
from io import BytesIO

import libs.validator
import tornado
from handler.api import APIHandler
from core.config import Config
from .api import authenticated_async

import grpc
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc


import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.applications.resnet import preprocess_input
from tensorflow.keras import backend as K
import PIL.Image as Image
import base64
import html
import h5py
import pickle
from scipy.spatial import distance
import hnswlib
import pandas

class IndexHandler(tornado.web.RequestHandler):
    def get(self,*args,**kwargs):
        self.render('spu_retrieval.html') 

class SPURetrivalHandler(APIHandler):

    @authenticated_async
    async def post(self):
        imgs=self.post_data.get('pic',None)
        shop_name=self.post_data.get('shop_name',None)
        if imgs==None:
            self.send_to_client_non_encrypt(202,'failure',response='image files missing')
        if shop_name==None:
            self.send_to_client_non_encrypt(202,'failure',response='shop name missing')

        IMAGE_SHAPE = (224, 224)
        img_list=[]
        s1=time.time()
        for img_str in imgs:
            img=Image.open(BytesIO(base64.b64decode(img_str))).resize(IMAGE_SHAPE)
            img_data = preprocess_input(np.array(img))
            img_list.append(img_data.tolist())
        print('preprocess time:{}'.format(time.time()-s1))

        channel=grpc.insecure_channel('{}:{}'.format(Config().tf_serving_ip,Config().tf_serving_port)
            ,options=[('grpc.default_authority','spu_retrieval')])
        stub=prediction_service_pb2_grpc.PredictionServiceStub(channel)
        request=predict_pb2.PredictRequest()
        # request.authority ='tensorflow.serving.spu_retrieval'
        request.model_spec.name=shop_name
        request.model_spec.signature_name='serving_default'
        s0=time.time()
        request.inputs['input_1'].CopyFrom(tf.make_tensor_proto(img_list))
        s1=time.time()
        response=stub.Predict(request,20)
        print('data copy time:{}  inference time:{}'.format(s1-s0,time.time()-s1))
        outputs=np.asarray(response.outputs['conv5_block3_out'].float_val)
        outputs=np.reshape(outputs,(len(img_list),-1))

        s2=time.time()
        labels,pca,num_elements,dim=pickle.load(open('pca.bin','rb'))
        img_features=pca.transform(outputs)
        print('pca transform time:{}'.format(time.time()-s2))

        s3=time.time()
        p = hnswlib.Index(space='cosine', dim=dim)
        p.load_index('features.bin',max_elements=num_elements)
        indexs, distances = p.knn_query(img_features, k=20)
        print('hnswlib query time:{}'.format(time.time()-s3))

        entity=[np.array(labels)[indexs]][0]
        entity=[pandas.unique(arr).tolist()  for arr in entity]
        print(entity)
        result={'code':entity}
        self.send_to_client_non_encrypt(200, message='success', response=result)