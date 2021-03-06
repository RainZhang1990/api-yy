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
from core import my_redis, oss


class IndexHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('image_retrieval.html')


class ImageRetrivalHandler(APIHandler):

    @authenticated_async
    async def post(self):
        imgs = self.post_data.get('pic', None)
        co_id = self.post_data.get('co_id', None)
        category = self.post_data.get('category', 'sr')
        try:
            libs.validator.required(imgs, 'imgs')
            libs.validator.length(imgs, 'imgs')
            libs.validator.required(co_id, 'co_id')
            libs.validator.choices(category, ['sr', 'ic'], 'category')
        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return
        logging.info('{}_{}: ImageRetrival'.format(category, co_id))

        s1 = time.time()
        img_list = []
        for img_str in imgs:
            img = Image.open(BytesIO(base64.b64decode(img_str)))
            img_list.append(img)

        features = get_resnet101_feature_grpc('{}:{}'.format(
            Config().tf_serving_ip, Config().tf_serving_port), img_list)

        iid = FeatureManager().get_iid(category, co_id)
        pca = FeatureManager().get_pca(category, co_id)
        hnsw = FeatureManager().get_hnsw(category, co_id)
        if not iid or not pca or not hnswlib:
            self.send_to_client_non_encrypt(
                404, message='failure', response='使用前请先提交训练')
            return
        img_ids, labels = FeatureManager().get_iid(category, co_id)

        s2 = time.time()
        img_features = pca.transform(features)
        logging.info('{}_{}: pca transform time:{:.4f}s'.format(
            category, co_id, time.time()-s2))

        s3 = time.time()
        query_k = min(Config().image_retrieval.get('query_k'),
                      len(labels)) if category == 'sr' else 1
        indexs, distances = hnsw.knn_query(img_features, k=query_k)
        logging.info('{}_{}: hnswlib query time:{:.4f}s'.format(
            category, co_id, time.time()-s3))

        code, img_url, similarity, oss_key = [], [], [], []
        for i, arr in enumerate(indexs):
            tmp_code, tmp_url, tmp_similarity, tmp_key = [], [], [], []
            for j, index in enumerate(arr):
                if not labels[index] in tmp_code:
                    tmp_code.append(labels[index])
                    url = oss.oss_bucket.sign_url('GET', img_ids[index], 3600)
                    tmp_url.append(url)
                    tmp_key.append(img_ids[index])
                    tmp_similarity.append('{:.2%}'.format(1-distances[i][j]/2))
            code.append(tmp_code)
            img_url.append(tmp_url)
            similarity.append(tmp_similarity)
            oss_key.append(tmp_key)
        logging.info('{}_{}: {}'.format(category, co_id, code))
        result = {'code': code, 'similarity': similarity,
                  'oss_key': oss_key, 'url': img_url}
        self.send_to_client_non_encrypt(
            200, message='success', response=result)


class IrFitHandler(APIHandler):

    @authenticated_async
    async def post(self):
        co_id = self.post_data.get('co_id', None)
        category = self.post_data.get('category', None)
        try:
            libs.validator.required(co_id, 'co_id')
            libs.validator.choices(category, ['sr', 'ic'], 'category')
        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return
        logging.info('{}_{}: IrFit'.format(category, co_id))

        interval = Config().image_retrieval.get('fit_interval')
        time_format = Config().time_format
        fit_status = my_redis.redis_hgetall(category, co_id)
        if len(fit_status) > 0:
            fstatus = fit_status.get('status')
            if fstatus in ['queuing', 'fitting']:
                self.send_to_client_non_encrypt(
                    202, 'success', response='请求已接受,请勿重复提交')
                return
            etime = time.strptime(fit_status.get('etime'), time_format)
            if fstatus == 'finished' and time.time() - time.mktime(etime) < interval:
                self.send_to_client_non_encrypt(
                    403, 'failure', response='请求过于频繁,请稍后再试')
                return

        co_info = my_redis.redis_lpush('ir', category, co_id)
        my_redis.redis_hset(category, co_id, 'status', 'queuing')
        self.send_to_client_non_encrypt(202, 'success', response='请求已接受')


class IrLabelHandler(APIHandler):

    @authenticated_async
    async def post(self):
        co_id = self.post_data.get('co_id', None)
        category = self.post_data.get('category', None)
        try:
            libs.validator.required(co_id, 'co_id')
            libs.validator.choices(category, ['sr', 'ic'], 'category')
        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return
        logging.info('{}_{}: Get IrFitLabel'.format(category, co_id))

        result = {'label': FeatureManager().get_label(category, co_id)}
        self.send_to_client_non_encrypt(200, 'success', response=result)


class IrFitStatusHandler(APIHandler):

    @authenticated_async
    async def post(self):
        co_id = self.post_data.get('co_id', None)
        category = self.post_data.get('category', None)
        try:
            libs.validator.required(co_id, 'co_id')
            libs.validator.choices(category, ['sr', 'ic'], 'category')
        except libs.validator.ValidationError as e:
            self.send_to_client_non_encrypt(400, message=e.__str__())
            return
        logging.info('{}_{}: Get IrFitStatus'.format(category, co_id))

        result = my_redis.redis_hgetall(category, co_id)
        self.send_to_client_non_encrypt(200, 'success', response=result)
