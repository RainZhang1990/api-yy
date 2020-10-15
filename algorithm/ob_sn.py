import logging
import math
import time
import copy
import sys
import pandas as pd
import numpy as np

class OrderHeap():
    def __init__(self, order_set, sku_set):
        self.order_set = order_set
        self.sku_set = sku_set

class planar_dict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

class Sn():
    def __init__(self, order_src: dict, second_n, min_batch, max_batch, heap_qty):
        self.order_src = order_src
        self.second_n = second_n
        self.min_batch = min_batch
        self.max_batch = max_batch
        self.heap_qty = heap_qty
        self.order_batch = []
        self.transform_order()

    def transform_order(self):
        self.order_qty = len(self.order_src)
        self.order_list = list(self.order_src.keys())
        self.sku_index = dict()
        self.order_index = dict()
        self.order_encoded = dict()

        total_sku_qty = {}  # 统计销量
        for i, order in enumerate(self.order_list):
            self.order_index[order] = i
            for sku, qty in self.order_src[order].items():
                if sku in total_sku_qty:
                    total_sku_qty[sku] += qty
                else:
                    total_sku_qty[sku] = qty
        self.sku_list = sorted(total_sku_qty.keys(),
                               key=lambda k: total_sku_qty[k], reverse=True)  # 销量降序

        self.sku_qty = len(self.sku_list)
        for i, v in enumerate(self.sku_list):
            self.sku_index[v] = i

        for order in self.order_list:  # 去掉一个sku
            sku_tmp, sku_set = [], set()
            for sku, qty in self.order_src[order].items():
                sku_index = self.sku_index[sku]
                sku_tmp.append((sku_index, qty))
                sku_set.add(sku_index)
            sku_sorted = sorted(sku_tmp, key=lambda sku: (sku[1], -sku[0]))
            if sku_sorted[0][1] == 1 and len(sku_sorted) > 1:
                sku_set.remove(sku_sorted[0][0])

            self.order_encoded[self.order_index[order]] = sku_set

    def fit(self):
        epoch, batch_qty, order_joined, heaps = 0, -1, set(), []
        while len(self.order_batch) > batch_qty:
            batch_qty = len(self.order_batch)
            epoch += 1
            for od in self.order_list:
                order = self.order_index[od]
                sku_set = self.order_encoded[order]
                if order in order_joined:
                    continue
                min_index, min_val = None, math.inf
                for i, v in enumerate(heaps):  # 最小增量堆
                    new_len = len(sku_set | v.sku_set)
                    if new_len <= self.second_n:
                        d = new_len-len(v.sku_set)
                        if d < min_val:
                            min_index, min_val = i, d
                            if d == 0:
                                break
                if min_val <= epoch:  # 加入堆
                    min_heap = heaps[min_index]
                    min_heap.sku_set = min_heap.sku_set | sku_set
                    curr_order_set = min_heap.order_set
                    curr_order_set.add(order)
                    order_joined.add(order)
                    if len(curr_order_set) == self.max_batch:
                        self.order_batch.append(min_heap)
                        del heaps[min_index]
                elif len(heaps) < self.heap_qty:  # 新建堆
                    heaps.append(OrderHeap({order}, sku_set))
                    order_joined.add(order)

            for_del = set()
            for i, v in enumerate(heaps):
                if len(v.order_set) >= self.min_batch:
                    self.order_batch.append(v)
                    for_del.add(i)
            heaps = [v for i, v in enumerate(heaps) if not i in for_del]

        second_sn = dict()
        batch_sn = []
        for v in self.order_batch:  # 订单解析
            od_set = set()
            for order in v.order_set:
                o_src = self.order_list[order]
                od_set.add(o_src)
                second_sn[o_src] = list({self.sku_list[isku]
                                    for isku in self.order_encoded[order]})
            batch_sn.append(list(od_set))

        left = sum([len(h.order_set) for h in heaps])
        covered = len(order_joined)-left
        info = 'ob_sn  epoch：{} batch_qty: {} heap_qty: {} covered: {} rate: {:.1%}total: {} order_joined: {} left:{}'.format(
            epoch, batch_qty,self.heap_qty, covered, covered/self.order_qty, self.order_qty, len(order_joined), left)
        logging.info(info)
        return batch_sn, second_sn


def sn_validate(order_src, batch_sn, second_sn, second_n, min_batch, max_batch):
    order_qty = 0
    order_set = set()
    for batch in batch_sn:
        assert len(batch) >= min_batch and len(batch) <= max_batch
        order_qty += len(batch)
        order_set |= batch
        sku_set0 = set()
        for order in batch:
            sku_set1 = set(order_src[order].keys())
            sku_set2 = second_sn[order]
            sku_set0 |= sku_set2
            assert sku_set2.issubset(sku_set1) and len(sku_set1-sku_set2) <= 1
        assert len(sku_set0) <= second_n
    assert len(order_set) == order_qty


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    # df = pd.read_excel('d:/yy.xlsx', sheet_name='Sheet1')
    df = pd.read_excel('d:/jyt2.xlsx', sheet_name='Sheet1')
    # df = pd.read_excel('d:/puxi.xlsx', sheet_name='Sheet1')

    order_src = planar_dict()
    for row in df.itertuples():
        order_src[str(row[1])][row[2]] = row[3]

    t1 = time.time()
    for i in range(50):
        sn = SN(order_src, 32, 50, 60, 10*i)
        batch_sn, second_sn = sn.fit()
        sn_validate(order_src, batch_sn, second_sn, 32, 50, 60)
    t2 = time.time()
    print('{:.2f}s'.format(t2-t1))
