import numpy as np
import os
import PIL.Image as image
import pickle
import logging
import time
from io import BytesIO
import hnswlib
from sklearn.decomposition import IncrementalPCA
from multiprocessing import Process, Pool
import multiprocessing as mp
import oss2
from core import redis, oss
from core import config
from core.config import Config
from libs.tf import *
import asyncio


def load_image(img_paths, batch, pipe1, oss_bucket):
    logging.getLogger().setLevel(logging.INFO)
    try:
        t = time.time()
        for i, path in enumerate(img_paths):
            img_stream = BytesIO(oss_bucket.get_object(path).read())
            img = image.open(img_stream)
            if (i-len(img_paths) % batch) % batch == 0:
                logging.info('images  batch {} sended {:.1f}s '.format(
                    i // batch, time.time()-t))
                t = time.time()
            pipe1.send(img)
        pipe1.send(0)
        logging.info('load_image finished ')
    except Exception as e:
        logging.critical(e)
        pipe1.send(e)


def feature_extract(batch, data_length, tf_serving_ip, tf_serving_port, pipe1, pipe2):
    logging.getLogger().setLevel(logging.INFO)
    try:
        flag = True
        no = 0
        while flag:
            no += 1
            imgs = []
            # 预加载部分数据 避免partial_fit报错
            if no == 1:
                for _ in range(data_length % batch):
                    img = pipe1.recv()
                    status_check(img)
                    imgs.append(img)
            for _ in range(batch):
                img = pipe1.recv()
                status_check(img)
                if not type(img) == int:
                    imgs.append(img)
                else:
                    flag = False
                    break
            if len(imgs) == 0:
                break
            t = time.time()
            logging.info('feature extracting batch {} '.format(no))
            features = get_resnet101_feature_grpc('{}:{}'.format(
                tf_serving_ip, tf_serving_port), imgs, 10000)
            # features = get_resnet101_feature_local(imgs)
            logging.info(
                'feature extracting batch {} finished {:.1f}s '.format(no, time.time()-t))
            pipe2.send(features)
        pipe2.send(0)
        logging.info('feature_extract finished ')
    except Exception as e:
        logging.critical(e)
        pipe2.send(e)


def pca_hnsw(pca_n, data_length, pipe2):
    try:
        hnsw = None
        pca = None
        n = None
        no = 0
        feature_list = []
        while True:
            no += 1
            features = pipe2.recv()
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
                logging.info('pca partial fiting batch {} '.format(no))
                pca.partial_fit(features)
                logging.info('pca partial fiting batch {} finished {:.1f}s '.format(
                    no, time.time()-t))
            else:
                break
        t = time.time()
        for f in feature_list:
            hnsw.add_items(pca.transform(f))
        logging.info('pca hnsw time {:.1f}s '.format(time.time()-t))
        return pca, hnsw
    except Exception as e:
        logging.critical(e)
        raise e


def status_check(obj):
    if isinstance(obj, Exception):
        raise obj


def fit(save_dir, category, co_id, pca_n, batch, iid, labels, oss_bucket, tf_serving_ip, tf_serving_port):
    logging.getLogger().setLevel(logging.INFO)
    pipe1_1, pipe1_2 = mp.Pipe(duplex=False)
    pipe2_1, pipe2_2 = mp.Pipe(duplex=False)
    pool = Pool(processes=3)

    t1 = time.time()
    data_length = len(iid)
    il = pool.apply_async(load_image, args=(iid, batch, pipe1_2, oss_bucket))
    fe = pool.apply_async(feature_extract, args=(
        batch, data_length, tf_serving_ip, tf_serving_port, pipe1_1, pipe2_2))
    pool.close()
    pca, hnsw = pca_hnsw(pca_n, data_length, pipe2_1)
    pool.join()

    logging.info('writing...')
    path = os.path.join(save_dir, category, 'iid', '{}.bin'.format(co_id))
    pickle.dump((iid, labels), open(path, 'wb'))
    path = os.path.join(save_dir, category,  'pca', '{}.bin'.format(co_id))
    pickle.dump(pca, open(path, 'wb'))
    path = os.path.join(save_dir, category,  'hnsw', '{}.bin'.format(co_id))
    hnsw.save_index(path)
    path = os.path.join(save_dir, category, 'label', '{}.bin'.format(co_id))
    pickle.dump(sorted(set(labels)), open(path, 'wb'))

    logging.info('irfit total cost {}s ,  co_id: {}  category: {}'.format(
        time.time()-t1, co_id, category))


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
    config.init()
    redis.init()
    oss.init()

    batch = Config().image_retrival.get('batch')
    pca_n = Config().image_retrival.get('pca_n_components')
    save_dir = Config().image_retrival.get('feature_path')
    retry_interval = Config().image_retrival.get('retry_interval')
    time_format = Config().time_format
    tf_serving_ip = Config().tf_serving_ip
    tf_serving_port = Config().tf_serving_port
    oss_bucket = oss.oss_bucket

    while True:
        try:
            switch = redis.redis_get('ir', 'fit_switch')
            co_id = redis.redis_rpop('ir', category)
            if switch == 0 or co_id == None:
                time.sleep(retry_interval)
                continue
            redis.redis_hset(category, co_id, 'status', 'fitting')
            redis.redis_hset(category, co_id, 'stime',
                             time.strftime(time_format, time.localtime()))
            labels, iid, = oss_init(oss_bucket, category, co_id)
            fit(save_dir, category, co_id, pca_n, batch, iid, labels,
                oss_bucket, tf_serving_ip, tf_serving_port)
            redis.redis_hset(category, co_id, 'status', 'finished')
            redis.redis_hset(category, co_id, 'etime',
                             time.strftime(time_format, time.localtime()))
            redis.publish('{}_{}'.format(category, co_id))
        except Exception as e:
            logging.critical(
                'fit error, category: {} co_id: {}  e: {}'.format(category, co_id, e))
            redis.redis_hset(category, co_id, 'status', 'failed')
            redis.redis_hset(category, co_id, 'etime',
                             time.strftime(time_format, time.localtime()))


def main(fit_workers, keep_alive=False):
    for _ in range(workers):
        Process(target=fit_queue, args=('sr',)).start()
        # pool.apply_async(fit_queue, ('ic',))
    while keep_alive:
        pass

if __name__ == "__main__":
    config.init()
    workers = Config().image_retrival.get('fit_workers')
    main(workers, True)
    # co_info = {'taotao': '10016905', 'leige': '10097386',
    #            'yulu': '10054631', 'aozi': '10051865'}
