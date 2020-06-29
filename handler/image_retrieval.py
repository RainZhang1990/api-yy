import time
from io import BytesIO
import logging
import PIL.Image as Image
import base64
import hnswlib
import libs.validator
import tornado
from handler.api import APIHandler
from core.config import Config
from .api import authenticated_async
from libs.tf import *
from controller.feature import FeatureManager
from core import redis, oss


class IndexHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('image_retrieval.html')


class ImageRetrivalHandler(APIHandler):

    @authenticated_async
    async def post(self):
        imgs = self.post_data.get('pic', None)
        custom_id = self.post_data.get('custom_id', None)
        category = self.post_data.get('category', 'sr')
        try:
            libs.validator.required(imgs)
            libs.validator.required(custom_id)
            libs.validator.ir_category(category)

        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return

        logging.info('ImageRetrival  co_id: {}  category: {}'.format(
            custom_id, category))
        s1 = time.time()
        img_list = []
        for img_str in imgs:
            img = Image.open(BytesIO(base64.b64decode(img_str)))
            img_list.append(img)

        features = get_resnet101_feature_grpc('{}:{}'.format(
            Config().tf_serving_ip, Config().tf_serving_port), img_list)
        img_ids, labels = FeatureManager().get_iid(category, custom_id)
        pca = FeatureManager().get_pca(category, custom_id)
        hnsw = FeatureManager().get_hnsw(category, custom_id)

        s2 = time.time()
        img_features = pca.transform(features)
        logging.info('pca transform time:{}'.format(time.time()-s2))

        s3 = time.time()
        indexs, distances = hnsw.knn_query(img_features, k=50)
        logging.info('hnswlib query time:{}'.format(time.time()-s3))

        code, img_url, distance = [], [], []
        for i, arr in enumerate(indexs):
            tmp_code, tmp_url, tmp_distance = [], [], []
            for j, index in enumerate(arr):
                if not labels[index] in tmp_code:
                    tmp_code.append(labels[index])
                    url = 'http://{}.{}/{}'.format(
                        Config().oss.get('bucket'), Config().oss.get('endpoint'), img_ids[index])
                    tmp_url.append(url)
                    tmp_distance.append('{:.2%}'.format(1-distances[i][j]))
            code.append(tmp_code)
            img_url.append(tmp_url)
            distance.append(tmp_distance)
        logging.info(code)
        result = {'code': code, 'similarity': distance, 'url': img_url}
        self.send_to_client_non_encrypt(
            200, message='success', response=result)


class IrFitHandler(APIHandler):

    @authenticated_async
    async def post(self):
        custom_id = self.post_data.get('custom_id', None)
        category = self.post_data.get('category', None)
        try:
            libs.validator.required(custom_id)
            libs.validator.ir_category(category)

        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return

        logging.info('IrFit: {}  {}'.format(custom_id, category))
        interval = Config().image_retrival.get('fit_interval')
        time_format = Config().time_format
        fit_status = redis.redis_hgetall(category, custom_id)
        if len(fit_status) > 0:
            if fit_status.get('status') in ['queuing', 'fitting']:
                self.send_to_client_non_encrypt(
                    202, 'success', response='请求已接受,请勿重复提交')
                return
            etime = time.strptime(fit_status.get('etime'), time_format)
            if time.time() - time.mktime(etime) < interval:
                self.send_to_client_non_encrypt(
                    403, 'failure', response='请求过于频繁,请稍后再试')
                return

        co_info = redis.redis_lpush('ir', category, custom_id)
        redis.redis_hset(category, custom_id, 'status', 'queuing')
        self.send_to_client_non_encrypt(202, 'success', response='请求已接受')


class IrLabelHandler(APIHandler):

    @authenticated_async
    async def get(self):
        custom_id = self.post_data.get('custom_id', None)
        category = self.post_data.get('category', None)
        try:
            libs.validator.required(custom_id)
            libs.validator.ir_category(category)

        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return

        logging.info('Get IrFitLabel: {}  {}'.format(custom_id, category))
        result = {'label': FeatureManager().get_label(category, custom_id)}
        self.send_to_client_non_encrypt(200, 'success', response=result)


class IrFitStatusHandler(APIHandler):

    @authenticated_async
    async def get(self):
        custom_id = self.post_data.get('custom_id', None)
        category = self.post_data.get('category', None)
        try:
            libs.validator.required(custom_id)
            libs.validator.ir_category(category)

        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return

        logging.info('Get IrFitStatus: {}  {}'.format(custom_id, category))
        result = {'fit status': redis.redis_hgetall(category, custom_id)}
        self.send_to_client_non_encrypt(200, 'success', response=result)
