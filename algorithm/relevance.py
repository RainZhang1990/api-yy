import logging
import math
import time
import sys
sys.path.append('.')
import pandas as pd
from itertools import combinations
from core.config import Config
from core import config

from multiprocessing import Process, Pool
import multiprocessing as mp


def relevance(order_src, dim, top):
    combo_count = dict()
    for sku_list in order_src:
        if len(sku_list) >= dim and len(sku_list) < 30:
            sku_list.sort()
            for c in combinations(sku_list, dim):
                if not c in combo_count:
                    combo_count[c] = 0
                combo_count[c] += 1
    c_list = sorted(combo_count.keys(),
                    key=lambda k: combo_count[k], reverse=True)
    return {k: combo_count[k] for k in c_list[:top*10]}


def relevance_parallel(order_src, dim, top):
    t1 = time.time()
    fit_workers = Config().relevance.get('fit_workers')
    load_workers = len(order_src)//Config().relevance.get('worker_load')+1
    total_count = {}
    if load_workers==1 or fit_workers==1:
        total_count = relevance(order_src, dim, top)
        logging.info('relevance time:{:.3f}s cores:{} orders:{}'.format(
            time.time()-t1, 1, len(order_src)))
    else:
        cores = min(mp.cpu_count(), fit_workers, load_workers)
        process_pool = Pool(cores)
        process_list = []
        core_amount = math.ceil(len(order_src)/cores)
        for i in range(cores):
            core_list = order_src[core_amount*i:core_amount*(i+1)]
            p = process_pool.apply_async(relevance, args=(core_list, dim, top,))
            process_list.append(p)
        process_pool.close()
        process_pool.join()
        for v in process_list:
            sub_count = v.get()
            for k, v in sub_count.items():
                if not k in total_count:
                    total_count[k] = 0
                total_count[k] += v
        logging.info('relevance_parallel time:{:.3f}s cores:{} orders:{}'.format(
            time.time()-t1, cores, len(order_src)))
    t_list = sorted(total_count.keys(),
                    key=lambda k: total_count[k], reverse=True)
    return [{' '.join(k): total_count[k]} for k in t_list[:top]]


def relevance_test(order_src, result):
    for r in result:
        c=None
        for k, v in r.items():
            c=[k.split(' '), v]
            break
        n = 0
        for sku_set in order_src.values():
            if set(c[0]).issubset(set(sku_set)) and len(sku_set) > 1 and len(sku_set) < 30:
                n += 1
        assert n == c[1]


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    df = pd.read_csv('d:/jjj.csv')
    order_src = dict()
    for row in df.itertuples():
        o_id = str(row[1])
        if not o_id in order_src:
            order_src[o_id] = []
        order_src[o_id].append(row[2])
        # if len(order_src)==10000:
        #     break

    t1 = time.time()
    result = relevance_parallel(list(order_src.values()), 2, 100)
    # relevance_test(order_src, result)
    t2 = time.time()
    print(result)
    print('{:.2f}s'.format(t2-t1))
