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
        img_str=self.post_data.get('pic',None)
        if img_str==None:
            self.send_to_client_non_encrypt(202,'failure',response='未找到图片')
            
        url ="http://127.0.0.1:8501/v1/models/xinyou:predict"

        IMAGE_SHAPE = (224, 224)
        img = Image.open(BytesIO(base64.b64decode(img_str))).resize(IMAGE_SHAPE)
        img_data = preprocess_input(np.array(img))
        data={'instances':np.expand_dims(img_data, axis=0).tolist()}
        response= requests.post(url,json=data)
        # for _ in range(100):
        #     response= requests.post(url,json=data)
        tfs_response = json.loads(response.text)

        result =np.asarray(tfs_response['predictions'])
        predicted_index = np.argmax(result[0], axis=-1)
        
        path=r'/home/yaoyu/Desktop/work-dir/labels/xinyou.txt'
        labels=np.loadtxt(path,dtype=np.str)

        print(labels[predicted_index])
        print(result[0][predicted_index])
        
        result={'code':labels[predicted_index],'confidence':result[0,predicted_index]}
        self.send_to_client_non_encrypt(200, message='success', response=result)