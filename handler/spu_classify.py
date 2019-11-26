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

        data={'instances':img_list}

        s1=time.time()
        url ="http://127.0.0.1:8501/v1/models/{}:predict".format(shop_name)
        response= requests.post(url,json=data)
        print('inference time:{}'.format(time.time()-s1))
        # for _ in range(100):
        #     response= requests.post(url,json=data)
        tfs_response = json.loads(response.text)
        result =np.asarray(tfs_response['predictions'])
        predicted_index = np.argmax(result, axis=-1)
        confidence=np.max(result, axis=-1)
        
        path=r'/home/yaoyu/Desktop/work-dir/saved-model/spu-classify/labels/{}.txt'.format(shop_name)
        labels=np.loadtxt(path,dtype=np.str)

        print(predicted_index)
        print(labels[predicted_index])
        print(confidence)
        
        result={'code':labels[predicted_index].tolist(),'confidence':confidence.tolist()}
        self.send_to_client_non_encrypt(200, message='success', response=result)