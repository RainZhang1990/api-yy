import logging
import math
import time
import copy
import sa
import sys

import matplotlib.pyplot as plt
import numpy as np
import numpy.random as nr
from impala.dbapi import connect
from multiprocessing import Process, Pool
import multiprocessing as mp

import utilities.collection as uc


class ClusterNode(object):
    def __init__(self, vec: set, left=None, right=None, distance=-1, id=None, count=1, order_list=[]):
        """
        :param vec: 保存两个数据聚类后形成新的订单
        :param left: 左节点
        :param right:  右节点
        :param distance: 两个订单的距离
        :param id: 用来标记哪些节点是计算过的
        :param count: 这个节点的叶子节点个数
        """
        self.vec = vec
        self.left = left
        self.right = right
        self.distance = distance
        self.id = id
        self.count = count
        self.order_list = order_list


class Hierarchical(object):
    def __init__(self, commodity_dist={}, order_dict={}, min_batch=18, max_batch=20):
        if min_batch <= 0:
            raise Exception('Batch amount should be a positive integer!')
        if min_batch > max_batch:
            raise Exception('Max_batch should be greater than min_batch!')

        self.commodity_dist = commodity_dist
        self.order_dict = order_dict
        self.origin_order_dict = copy.deepcopy(order_dict)
        self.main_node = None
        self.min_batch = min_batch
        self.max_batch = max_batch
        self.batch_order = []
        self.batch_route = []
        self.batch_distance = []

    def cluster_distance(self, order_dict1, order_dict2):
        result = {}
        for key1, val1 in order_dict1.items():
            for key2, val2 in order_dict2.items():
                if key1 < key2:
                    dist = self.order_distance(set(val1), set(val2))
                    uc.update_dict2(result, key1, key2, dist)
        return result

    def init_cluster_distance_async(self):
        cluster_dist = {}
        cores = mp.cpu_count()
        process_pool = Pool(cores)
        process_list = []
        core_amount = math.ceil(len(self.order_dict)/cores)
        order_list = list(self.order_dict.items())
        for i in range(cores):
            core_list = order_list[core_amount*i:core_amount*(i+1)]
            dist = process_pool.apply_async(
                self.cluster_distance, args=(dict(core_list), self.order_dict,))
            process_list.append(dist)
        process_pool.close()
        process_pool.join()
        for v in process_list:
            cluster_dist.update(v.get())

        return cluster_dist

    def solve(self):
        while len(self.order_dict) > self.max_batch:
            self.fit()
            self.pick_batch_order(self.main_node)
        self.batch_order.append(self.order_dict)

    def delete(self, batch):
        for v in batch:
            del self.order_dict[v]

    def fit(self):
        logging.info("step1:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        cluster_dist = self.init_cluster_distance_async()
        logging.info("step2:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

        cluster_node_dict = {key: ClusterNode(vec=set(val), id=key, order_list=[key])
                             for key, val in self.order_dict.items()}
        currentclustid = -1
        while len(cluster_node_dict) > 1:
            min_dist = math.inf
            key1, key2 = None, None
            for k, v in cluster_dist.items():
                for k1, v1 in v.items():
                    if v1 < min_dist:
                        min_dist = v1
                        key1, key2 = k, k1

            # 合并两个聚类
            node1, node2 = cluster_node_dict[key1], cluster_node_dict[key2]
            new_node = ClusterNode(vec=node1.vec | node2.vec,
                                   left=node1,
                                   right=node2,
                                   distance=min_dist,
                                   id=currentclustid,
                                   count=node1.count + node2.count,
                                   order_list=node1.order_list+node2.order_list)

            del cluster_node_dict[key1], cluster_node_dict[key2]
            self.new_cluster_distance(cluster_dist, key1, key2)

            for v in cluster_node_dict.values():
                dist = self.order_distance(v.vec, new_node.vec)
                uc.update_dict2(cluster_dist, v.id, new_node.id, dist)

            cluster_node_dict[currentclustid] = new_node
            currentclustid -= 1
        self.main_node = cluster_node_dict[currentclustid+1]

        logging.info("step3:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    def new_cluster_distance(self, cluster_distance, key1, key2):
        del cluster_distance[key1]
        if key2 in cluster_distance:
            del cluster_distance[key2]
        for_del = []
        for k, v in cluster_distance.items():
            if key1 in v:
                del v[key1]
            if key2 in v:
                del v[key2]
            if len(v) == 0:
                for_del.append(k)
        for k in for_del:
            del cluster_distance[k]

    def order_distance(self, order0: set, order1: set) -> float:
        all_dist = {}
        for i in order0:
            for j in order1:
                uc.update_dict2(all_dist, i, j, self.comm_distance(i, j))
        main_comm0, main_comm1 = set(), set()
        main_dist = self.main_distance(
            all_dist, main_comm0, main_comm1, min(len(order0), len(order1)))

        all_comm = set(order0) | set(order1)
        main_comm = main_comm0 | main_comm1
        residue_comm = all_comm - main_comm
        residue_dist = {}
        for v in residue_comm:
            for v1 in main_comm:
                uc.update_dict2(residue_dist, v, v1, self.comm_distance(v, v1))
        resi_dist = self.residue_distance(residue_dist)
        return main_dist + resi_dist

    def main_distance(self, all_dist: list, set0: set, set1: set, min_len: int):
        if len(set0) == min_len or len(set1) == min_len:
            return 0
        n = math.inf
        key0 = None
        key1 = None
        for k, v in all_dist.items():
            for k1, v1 in v.items():
                if v1 < n:
                    key0 = k
                    key1 = k1
                    n = v1
        set0.add(key0)
        set1.add(key1)
        return n + self.main_distance(uc.del_all_dict_value2(all_dist, key0, key1), set0, set1, min_len)

    def residue_distance(self, residue_dist: dict):
        if len(residue_dist) == 0:
            return 0

        n = math.inf
        comm = None
        for k, v in residue_dist.items():
            for v1 in v.values():
                if v1 < n:
                    n = v1
                    comm = k
        return n + self.residue_distance(self.new_residue_list(residue_dist, comm))

    def new_residue_list(self, residue_dist: dict, comm: str):
        del residue_dist[comm]
        for k in list(residue_dist.keys()).copy():
            uc.update_dict2(residue_dist, k, comm, self.comm_distance(k, comm))
        return residue_dist

    def comm_distance(self, comm1, comm2):
        if comm1 == comm2:
            return 0
        d = uc.get_dict_value2(self.commodity_dist, comm1, comm2, math.inf)
        if d == math.inf:
            raise Exception('库位间距不存在：{}-{}'.format(comm1, comm2))
        return d

    def merge_order(self, order_list0: list, order_list1: list, target_amount: int):
        if len(order_list0) == target_amount or len(order_list1) == 0:
            return order_list0

        n = math.inf
        order = None
        for v in order_list0:
            for v1 in order_list1:
                dist = self.order_distance(
                    self.order_dict[v], self.order_dict[v1])
                if dist < n:
                    n = dist
                    order = v1
        order_list0.append(order)
        order_list1.remove(order)

        return self.merge_order(order_list0, order_list1, target_amount)

    def pick_batch_order(self, cluster_node):
        if cluster_node.count < self.min_batch:
            return
        left_child = cluster_node.left
        right_child = cluster_node.right
        left_count = left_child.count
        right_count = right_child.count
        if left_count > self.max_batch:
            self.pick_batch_order(left_child)
        if right_count > self.max_batch:
            self.pick_batch_order(right_child)

        if left_count <= self.max_batch and left_count >= self.min_batch:
            self.batch_order.append(left_child.order_list)
            self.delete(left_child.order_list)
        if right_count <= self.max_batch and right_count >= self.min_batch:
            self.batch_order.append(right_child.order_list)
            self.delete(right_child.order_list)

        if left_count < self.min_batch and right_count < self.min_batch:
            batch = self.merge_order(
                left_child.order_list[:], right_child.order_list[:], self.max_batch)
            self.batch_order.append(batch)
            self.delete(batch)

    def get_route(self):
        sa1 = sa.SA(self.commodity_dist)
        bins_list = []
        for v in self.batch_order:
            bins = set()
            for v1 in v:
                bins = bins | self.origin_order_dict[v1]
            bins_list.append(bins)

        process_list = []
        cores = mp.cpu_count()
        process_pool = Pool(cores)
        for v in bins_list:
            process_list.append(process_pool.apply_async(
                sa1.get_route, args=(list(v),)))
        process_pool.close()
        process_pool.join()

        for proc in process_list:
            res = proc.get()
            self.batch_distance.append(res[1])
            self.batch_route.append(res[2])


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    host='47.110.133.110'
    port=3389
    date='2019-05-08'

    argvs=sys.argv
    if len(argvs)>1:
        host='10.0.130.7'
        port=4000
        date=argvs[1]

    conn = connect(host, port)
    cur = conn.cursor()

    sqlCommDist = '''SELECT * FROM tmp.pick_model_estimate_3 WHERE version=5'''
    cur.execute(sqlCommDist)
    CommDist = cur.fetchall()
    comm_dist = {}
    for cd in CommDist:
        uc.update_dict2(comm_dist, cd[0], cd[1], cd[4])
        uc.update_dict2(comm_dist, cd[1], cd[0], cd[4])

    sqlBatchOrder = '''SELECT distinct period FROM tmp.pick_order_model_input_2 a 
    	where EXISTS ( SELECT 1 FROM tmp.pick_model_location_3 b WHERE a.pos_abbr = b.loc) ORDER BY period'''
    cur.execute(sqlBatchOrder)
    batchOrder = cur.fetchall()

    for v in batchOrder:
        period=v[0]
        sqlOrderDetail = '''SELECT * FROM tmp.pick_order_model_input_2 a  WHERE period = {}
    	    AND EXISTS ( SELECT 1 FROM tmp.pick_model_location_3 b WHERE a.pos_abbr = b.loc) limit 500'''.format(period)
        cur.execute(sqlOrderDetail)
        orderDetail = cur.fetchall()
        conn.close()

        order_list = {}
        for od in orderDetail:
            if not od[2] in order_list:
                order_list[od[2]] = set()
            order_list[od[2]].add(od[6])
        
        start = time.time()
        hr = Hierarchical(comm_dist, order_list, 14, 16)
        hr.solve()
        hr.get_route()
        end = time.time()
        
        sql0="INSERT OVERWRITE tmp.pick_order_model_output_by_pos PARTITION(data_dt = CAST('2019-05-15' AS VARCHAR(10)),period = {}) VALUES".format(period)
        sql1=''
        for i,v in enumerate(hr.batch_route):
            for j,v1 in enumerate(v):
                sql1+="({},{},'{}',{},'{}',{}),".format(i,j,v1,uc.get_dict_value2(comm_dist,v[j],v[j-1],0)  if not j==0 else 0,'',int(end-start))
        sql1=sql1[:len(sql1)-1]

        conn = connect(host, port)
        cur = conn.cursor()
        cur.execute(sql0+sql1)

        logging.info('period:{}'.format(period))
        logging.info('total_order:{}'.format(sum([len(i) for i in  hr.batch_order])))
        logging.info('total_dist:{} {}'.format(sum(hr.batch_distance),hr.batch_distance))

    