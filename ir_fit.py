import numpy as np
import os
import PIL.Image as image
import pickle
import logging
import time
from io import BytesIO
import hnswlib
from sklearn.decomposition import IncrementalPCA
from multiprocessing import Process, Pool, Queue
import multiprocessing as mp
import oss2
from core import redis, oss
from core import config
from core.config import Config
from libs.tf import *
import asyncio


def load_image(img_paths, batch, queue1, oss_bucket, category, co_id):
    logging.getLogger().setLevel(logging.INFO)
    try:
        t = time.time()
        for i, path in enumerate(img_paths):
            img_stream = BytesIO(oss_bucket.get_object(path).read())
            img = image.open(img_stream)
            if (i-len(img_paths) % batch) % batch == 0:
                logging.info('{}_{}: images  batch {} sended {:.2f}s'
                             .format(category, co_id, i // batch, time.time()-t))
                t = time.time()
            queue1.put(img)
        queue1.put(0)
        logging.info('{}_{}: load_image finished '.format(category, co_id))
    except Exception as e:
        logging.critical(
            '{}_{}: fit error(load_image), {}'.format(category, co_id, e))
        queue1.put(e)


def feature_extract(batch, data_length, tf_serving_ip, tf_serving_port, queue1, queue2, category, co_id):
    logging.getLogger().setLevel(logging.INFO)
    try:
        flag, no = True, 0
        while flag:
            no += 1
            imgs = []
            # 预加载部分数据 避免partial_fit报错
            if no == 1:
                for _ in range(data_length % batch):
                    img = queue1.get()
                    status_check(img)
                    imgs.append(img)
            for _ in range(batch):
                img = queue1.get()
                status_check(img)
                if not type(img) == int:
                    imgs.append(img)
                else:
                    flag = False
                    break
            if len(imgs) == 0:
                break
            t = time.time()
            logging.info('{}_{}: feature extracting batch {} '
                         .format(category, co_id, no))
            features = get_resnet101_feature_grpc('{}:{}'.format(
                tf_serving_ip, tf_serving_port), imgs, 10000)
            # features = get_resnet101_feature_local(imgs)
            logging.info('{}_{}: feature extracting batch {} finished {:.2f}s '
                         .format(category, co_id, no, time.time()-t))
            queue2.put(features)
        queue2.put(0)
        logging.info(
            '{}_{}: feature_extract finished '.format(category, co_id))
    except Exception as e:
        logging.critical(
            '{}_{}: fit error(feature_extract), {}'.format(category, co_id, e))
        queue2.put(e)


def pca_hnsw(pca_n, data_length, queue2, category, co_id):
    try:
        hnsw, pca, n, no, feature_list = None, None, None, 0, []
        while True:
            no += 1
            features = queue2.get()
            status_check(features)
            if not type(features) == int:
                if pca == None:
                    n = min(len(features), pca_n)
                    pca = IncrementalPCA(n_components=n)
                    hnsw = hnswlib.Index(space='cosine', dim=n)
                    hnsw.init_index(max_elements=data_length,
                                    ef_construction=100, M=64)
                feature_list.append(features)
                t = time.time()
                logging.info('{}_{}: pca partial fiting batch {} '
                             .format(category, co_id, no))
                pca.partial_fit(features)
                logging.info('{}_{}: pca partial fiting batch {} finished {:.2f}s '
                             .format(category, co_id, no, time.time()-t))
            else:
                break
        t = time.time()
        for f in feature_list:
            hnsw.add_items(pca.transform(f))
        logging.info('{}_{}: pca hnsw time {:.2f}s '
                     .format(category, co_id, time.time()-t))
        return pca, hnsw
    except Exception as e:
        logging.critical(
            '{}_{}: fit error(pca_hnsw), {}'.format(category, co_id, e))
        raise e


def status_check(obj):
    if isinstance(obj, Exception):
        raise obj


def fit(save_dir, category, co_id, pca_n, batch, iid, labels, oss_bucket, tf_serving_ip, tf_serving_port):
    queue1 = Queue(batch)
    queue2 = Queue(batch)

    t1 = time.time()
    data_length = len(iid)
    p1 = Process(target=load_image, args=(
        iid, batch, queue1, oss_bucket, category, co_id))
    p2 = Process(target=feature_extract, args=(
        batch, data_length, tf_serving_ip, tf_serving_port, queue1, queue2, category, co_id))
    p1.start()
    p2.start()
    pca, hnsw = pca_hnsw(pca_n, data_length, queue2, category, co_id)
    p1.join()
    p2.join()

    logging.info('{}_{}: writing...'.format(category, co_id))
    version = '1'
    base_path = os.path.join(save_dir, category, co_id, version)
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    path = os.path.join(base_path, 'iid.bin')
    pickle.dump((iid, labels), open(path, 'wb'))
    path = os.path.join(base_path, 'pca.bin')
    pickle.dump(pca, open(path, 'wb'))
    path = os.path.join(base_path, 'hnsw.bin')
    hnsw.save_index(path)
    path = os.path.join(base_path, 'label.bin')
    pickle.dump(sorted(set(labels)), open(path, 'wb'))

    logging.info('{}_{}: irfit total cost {:.2f}s'
                 .format(category, co_id, time.time()-t1))


def oss_init(oss_bucket, category, co_id):
    it = oss2.ObjectIterator(
        oss_bucket, prefix='{}/{}/src/'.format(category, co_id))
    labels, iid = [], []
    for obj in it:
        key = obj.key
        if not key.endswith('/'):
            labels.append(key.split('/')[-2])
            iid.append(key)

    return labels, iid


def fit_queue(category):
    logging.getLogger().setLevel(logging.INFO)
    config.init()
    redis.init()
    oss.init()

    batch = Config().image_retrieval.get('batch')
    pca_n = Config().image_retrieval.get('pca_n_components')
    save_dir = Config().image_retrieval.get('feature_path')
    retry_interval = Config().image_retrieval.get('retry_interval')
    time_format = Config().time_format
    tf_serving_ip = Config().tf_serving_ip
    tf_serving_port = Config().tf_serving_port
    oss_bucket = oss.oss_bucket

    while True:
        co_id=''
        try:
            switch = redis.redis_get('ir', 'fit_switch') # 训练开关
            if switch == 0:
                time.sleep(retry_interval)
                continue
            co_id = redis.redis_rpop('ir', category)
            if co_id == None:
                time.sleep(retry_interval)
                continue
            redis.redis_hset(category, co_id, 'status', 'fitting')
            redis.redis_hset(category, co_id, 'stime',
                             time.strftime(time_format, time.localtime()))
            labels, iid, = oss_init(oss_bucket, category, co_id) # 获取全部图像信息
            if len(iid) == 0:
                raise Exception('oss image empty')
            fit(save_dir, category, co_id, pca_n, batch, iid, labels,
                oss_bucket, tf_serving_ip, tf_serving_port)
            redis.redis_hset(category, co_id, 'status', 'finished')
            redis.redis_hset(category, co_id, 'total', len(set(labels)))
            redis.redis_hset(category, co_id, 'etime',
                             time.strftime(time_format, time.localtime()))
            redis.publish('{}_{}'.format(category, co_id))
        except Exception as e:
            logging.critical(
                '{}_{}: fit error, {}'.format(category, co_id, e))
            try:
                redis.redis_hset(category, co_id, 'status', 'failed')
                redis.redis_hset(category, co_id, 'etime',
                                time.strftime(time_format, time.localtime()))
            except Exception as e1:
                logging.critical(
                    '{}_{}: fit status recover error, {}'.format(category, co_id, e1))
            time.sleep(retry_interval)
            


def main(fit_workers, keep_alive=False):
    for _ in range(fit_workers):
        Process(target=fit_queue, args=('sr',)).start()
        # Process(target=fit_queue, args=('ic',)).start()
    while keep_alive:  
        time.sleep(10**10)


if __name__ == "__main__":
    config.init()
    workers = Config().image_retrieval.get('fit_workers')
    main(workers, True)

