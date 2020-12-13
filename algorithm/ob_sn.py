import logging
import math
import time
import copy
import random
import pandas as pd
import multiprocessing as mp
import sys
sys.path.append(".")

from core.config import Config
from libs.utilities import planar_dict
from multiprocessing import Process, Pool

class OrderHeap():
    def __init__(self, order_set, sku_set_s, bin_set):
        self.order_set = order_set
        self.sku_set_s = sku_set_s
        self.bin_set = bin_set


class SN():
    def __init__(self, order_src, sku_bin, sku_vol_prior, second_qty, min_batch, max_bin_area, heap_qty):
        self.order_src = order_src
        self.sku_bin_src = sku_bin
        self.sku_vol_prior = sku_vol_prior
        self.second_qty = second_qty
        self.min_batch = min_batch
        self.max_bin_area = max_bin_area
        self.order_batch = []
        self.transform_order()
        self.heap_qty = heap_qty

    def transform_order(self):
        self.order_qty = len(self.order_src)
        self.order_list = []
        self.sku_list = []
        self.sku_index = dict()
        self.order_index = dict()
        self.order_encoded = dict()
        self.order_encoded_s = dict()
        self.order_encoded_n = dict()

        sku_qty_total = dict()  # 统计销量
        for order, skus in self.order_src.items():
            for sku, qty in skus.items():
                if sku in sku_qty_total:
                    sku_qty_total[sku] += qty
                else:
                    sku_qty_total[sku] = qty

        self.sku_list = sorted(sku_qty_total.keys(),
                               key=lambda sku: (sku_qty_total[sku], sku), reverse=True)  # sku销量降序 sku码参与排序固定顺序
        for i, v in enumerate(self.sku_list):
            self.sku_index[v] = i
        self.order_list = sorted(self.order_src.keys(),
                                 key=lambda order: self.get_sort_score(self.order_src[order].keys()))  # 订单排序

        self.sku_bin = {
            self.sku_index[k]: v for k, v in self.sku_bin_src.items() if k in self.sku_index}

        for i, order in enumerate(self.order_list):  # 去掉一个sku
            self.order_index[order] = i
            sku_tmp, sku_set = [], set()
            for sku, qty in self.order_src[order].items():
                sku_index = self.sku_index[sku]
                sku_tmp.append(
                    (sku_index, qty, self.sku_vol_prior.get(sku, 0)))
                sku_set.add(sku_index)

            self.order_encoded[i] = copy.deepcopy(sku_set)

            sku_sorted = sorted(
                sku_tmp, key=lambda sku: (sku[1], -sku[2], -sku[0]))
            if sku_sorted[0][1] == 1 and len(sku_sorted) > 1:
                sku_set.remove(sku_sorted[0][0])

            self.order_encoded_s[i] = sku_set
            self.order_encoded_n[i] = sku_sorted[0][0]

    def fit(self):
        t1 = time.time()
        epoch, batch_qty_old, batch_qty_new, heap_qty, order_joined, heaps = 0, \
            -1, 0, self.heap_qty, set(), []
        while batch_qty_new > batch_qty_old or epoch < 5:
            batch_qty_old = batch_qty_new
            for order in self.order_encoded.keys():
                if order in order_joined:
                    continue
                sku_set_s = self.order_encoded_s[order]
                bin_set = self.get_bin(self.order_encoded[order])
                min_index, min_val = None, math.inf
                for i, v in enumerate(heaps):  # 最小增量堆
                    new_len_s = len(sku_set_s | v.sku_set_s)
                    new_len_bin = len(bin_set | v.bin_set)
                    if new_len_s <= self.second_qty and new_len_bin <= self.max_bin_area:
                        d = (new_len_s-len(v.sku_set_s)) * 2 \
                             + new_len_bin - len(v.bin_set)
                        if d < min_val:
                            min_index, min_val = i, d
                            if d == 0:
                                break
                if min_val <= epoch:  # 加入堆
                    min_heap = heaps[min_index]
                    min_heap.sku_set_s |= sku_set_s
                    min_heap.bin_set |= bin_set
                    min_heap.order_set.add(order)
                    order_joined.add(order)
                    if len(min_heap.order_set) == self.min_batch:
                        heap_qty += 1
                        batch_qty_new += 1

                elif len(heaps) < heap_qty and len(sku_set_s) <= self.second_qty and len(bin_set) <= self.max_bin_area:  # 新建堆
                    heaps.append(OrderHeap({order}, copy.deepcopy(
                        sku_set_s), copy.deepcopy(bin_set)))
                    order_joined.add(order)
            epoch += 1

        for small_heap in heaps:  # 合并堆
            if len(small_heap.order_set) < self.min_batch:
                for order in small_heap.order_set:
                    sku_set_s = self.order_encoded_s[order]
                    bin_set = self.get_bin(self.order_encoded[order])
                    min_index, min_val = None, math.inf
                    for i, big_heap in enumerate(heaps):
                        if len(big_heap.order_set) >= self.min_batch:
                            new_len_s = len(sku_set_s | big_heap.sku_set_s)
                            new_len_bin = len(bin_set | big_heap.bin_set)
                            if new_len_s <= self.second_qty and new_len_bin <= self.max_bin_area:
                                d = (new_len_bin - len(big_heap.bin_set)) * \
                                    10 + new_len_s - len(big_heap.sku_set_s)
                                if d < min_val:
                                    min_index, min_val = i, d
                                    if d == 0:
                                        break
                    if min_index:  # 加入堆
                        heaps[min_index].order_set.add(order)
                        heaps[min_index].sku_set_s |= sku_set_s
                        heaps[min_index].bin_set |= bin_set

        batch_sn, second_sn, bin_sn = [], [], []
        for heap in heaps:  # 订单解析
            _len = len(heap.order_set)
            if _len >= self.min_batch:
                batch_sn.append({self.order_list[iorder]: self.sku_list[self.order_encoded_n[iorder]]
                                 for iorder in heap.order_set})
                second_sn.append([self.sku_list[isku]
                                  for isku in heap.sku_set_s])
                bin_sn.append(list(heap.bin_set))

        covered = sum([len(h.order_set)
                       for h in heaps if len(h.order_set) >= self.min_batch])
        logging.info('epoch:{} batch_qty:{} heap_qty:{} covered:{} order_qty:{} order_joined:{} left:{} time:{:.2f}s'.format(
            epoch, batch_qty_new, self.heap_qty, covered, self.order_qty, len(order_joined), len(order_joined)-covered, time.time()-t1))
        return batch_qty_new, self.heap_qty, covered, batch_sn, second_sn, bin_sn

    def get_bin(self, sku_set):
        return {self.sku_bin[sku] for sku in sku_set if sku in self.sku_bin}

    def get_sort_score(self, sku_list):
        return random.randint(0,len(sku_list)*100) # 按销量无用且低效 随机反而更稳定


def sn_test(order_src, sku_bin, sku_vol_prior, batch_sn, second_sn, bin_sn, second_qty, min_batch,  max_bin_area):
    # sku_vol_prior   todo
    order_qty = 0
    order_set = set()
    for i, order_batch in enumerate(batch_sn):
        assert len(order_batch) >= min_batch
        assert len(second_sn[i]) <= second_qty
        assert len(bin_sn[i]) <= max_bin_area

        order_qty += len(order_batch)
        order_set |= set(order_batch.keys())

        sku_set = set()
        for order, sku_n in order_batch.items():
            sku_set_order = set(order_src[order].keys())
            sku_set |= sku_set_order
            sku_set_s = set(second_sn[i])
            sku_set_n = sku_set_order-sku_set_s
            assert len(sku_set_n) <= 1
            assert sku_set_n.issubset({sku_n})
        bin_set = {sku_bin[sku] for sku in sku_set if sku in sku_bin}
        assert len(bin_set) <= max_bin_area
    assert len(order_set) == order_qty  # 防止订单出现在多个批次


def ob_sn(order_src, sku_bin, sku_vol_prior, second_qty, min_batch,  max_bin_area, heap_qty):
    logging.getLogger().setLevel(logging.INFO)
    sn = SN(order_src, sku_bin, sku_vol_prior, second_qty, min_batch,
            max_bin_area, heap_qty)
    return sn.fit()


def ob_sn_parallel(order_src, sku_bin, sku_vol_prior, second_qty, min_batch,  max_bin_area):
    t1 = time.time()
    heap_qty = Config().sn.get('heap_qty')
    cores = min(Config().sn.get('fit_workers'), len(heap_qty))
    process_pool = Pool(cores)
    process_list = []
    for i in range(cores):
        p = process_pool.apply_async(
            ob_sn, args=(order_src, sku_bin, sku_vol_prior, second_qty, min_batch,  max_bin_area, heap_qty[i]))
        process_list.append(p)
    process_pool.close()
    process_pool.join()
    max_batch_qty, max_heap_qty, max_covered, max_batch_sn, max_second_sn, max_bin_sn = None, None, \
        -1, None, None, None
    for v in process_list:
        batch_qty, heap_qty, covered, batch_sn, second_sn, bin_sn = v.get()
        if max_covered < covered or (max_covered == covered and batch_qty < max_batch_qty):
            max_batch_qty = batch_qty
            max_heap_qty = heap_qty
            max_covered = covered
            max_batch_sn = batch_sn
            max_second_sn = second_sn
            max_bin_sn = bin_sn

    logging.info('ob_sn_parallel time:{:.2f}s cores:{} batch_qty:{} max_heap_qty:{} max_covered:{} total:{} heap_qty:{}'.format(
        time.time()-t1, cores, max_batch_qty, max_heap_qty, max_covered, len(order_src), heap_qty))
    return max_covered, max_batch_sn, max_second_sn, max_bin_sn


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    df = pd.read_excel('d:/jyt2.xlsx', sheet_name='Sheet1')
    # df = pd.read_excel('d:/puxi.xlsx', sheet_name='Sheet1')
    order_src = planar_dict()
    for row in df.itertuples():
        order_src[str(row[1])][row[2]] = row[3]

    df = pd.read_excel('d:/jyt2.xlsx', sheet_name='Sheet7')
    sku_bin = dict()
    for row in df.itertuples():
        sku_bin[row[1]] = row[2]

    df = pd.read_excel('d:/jyt2.xlsx', sheet_name='Sheet3')
    sku_vol_prior = dict()
    for row in df.itertuples():
        sku_vol_prior[row[1]] = row[2]

    # sku_bin = dict()
    sku_vol_prior = dict()
    second_qty, min_batch, max_bin_area = 8, 50, 100

    t1 = time.time()
    covered, batch_sn, second_sn, bin_sn = ob_sn_parallel(
        order_src, sku_bin, sku_vol_prior, second_qty, min_batch, max_bin_area)
    sn_test(order_src, sku_bin, sku_vol_prior, batch_sn, second_sn,
            bin_sn, second_qty, min_batch,  max_bin_area)
    t2 = time.time()
    print('{:.2f}s'.format(t2-t1))
