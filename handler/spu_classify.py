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
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras import backend as K
import PIL.Image as Image
import base64
import html

class IndexHandler(tornado.web.RequestHandler):
    def get(self,*args,**kwargs):
        self.render('index.html') 

class SPUClassifyHandler(APIHandler):

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
        for img_str in imgs:
            img=Image.open(BytesIO(base64.b64decode(img_str))).resize(IMAGE_SHAPE)
            img_data = preprocess_input(np.array(img))
            img_list.append(img_data.tolist())

        channel=grpc.insecure_channel('{}:3389'.format(Config().tensorflow_serving_ip))
        stub=prediction_service_pb2_grpc.PredictionServiceStub(channel)
        request=predict_pb2.PredictRequest()
        request.model_spec.name=shop_name
        request.model_spec.signature_name='serving_default'
        request.inputs['mobilenetv2_1.00_224_input'].CopyFrom(tf.make_tensor_proto(img_list))
        s1=time.time()
        response=stub.Predict(request,10)
        print('inference time:{}'.format(time.time()-s1))
        result=np.asarray(response.outputs['dense'].float_val)
        result=np.reshape(result,(len(img_list),-1))

        # data={'instances':img_list}
        # s1=time.time()
        # url ="http://{}/spu_classify/v1/models/{}:predict".format(Config().tensorflow_serving_ip,shop_name)
        # response= requests.post(url,json=data)
        # print('inference time:{}'.format(time.time()-s1))
        
        # tfs_response = json.loads(response.text)
        # result =np.asarray(tfs_response['predictions'])

        predicted_index = np.argmax(result, axis=-1)
        confidence=np.max(result, axis=-1)
        
        s1=time.time()
        label_url='http://{}/labels/spu-classify/{}.txt'.format(Config().labels_ip,shop_name)
        label=requests.get(label_url)
        print('label time:{}'.format(time.time()-s1))
        labels=np.array(label.text.split(),dtype=np.str)

        print(predicted_index)
        print(labels[predicted_index])
        print(confidence)
        
        result={'code':labels[predicted_index].tolist(),'confidence':confidence.tolist()}
        self.send_to_client_non_encrypt(200, message='success', response=result)