import logging
import math
import time
import copy
import sa
import profile

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
    def __init__(self, commodity_dist={}):
        self.commodity_dist = commodity_dist
        self.nodes = None

    def cluster_distance(self, order_dict1, order_dict2):
        result = {}
        for key1, val1 in order_dict1.items():
            for key2, val2 in order_dict2.items():
                if key1 < key2:
                    dist = self.order_distance(set(val1), set(val2))
                    uc.update_dict2(result, key1, key2, dist)
        return result

    def init_cluster_distance_async(self, cluster_dist, order_dict):
        cores = mp.cpu_count()
        process_pool = Pool(cores)
        process_list=[]
        core_amount = math.ceil(len(order_dict)/cores)
        order_list = list(order_dict.items())
        for i in range(cores):
            core_list = order_list[core_amount*i:core_amount*(i+1)]
            dist = process_pool.apply_async(
                self.cluster_distance, args=(dict(core_list), order_dict,))
            process_list.append(dist)
        process_pool.close()
        process_pool.join()
        for v in process_list:
            cluster_dist.update(v.get())

    def fit(self, batch: int, order_dict: dict):
        logging.info("step1:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        if len(order_dict) < batch or batch <= 0:
            raise Exception('批次数应为小于订单数的正整数')

        cluster_dist = {}
        self.init_cluster_distance_async(cluster_dist, order_dict)
        # cluster_dist=self.cluster_distance(order_dict,order_dict)

        logging.info("step2:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

        cluster_node_dict = {key: ClusterNode(vec=set(val), id=key, order_list=[key])
                             for key, val in order_dict.items()}
        currentclustid = -1
        while max(cluster_node_dict.values(), key=lambda x: x.count).count < batch:
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
        self.nodes = cluster_node_dict
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

    def euler_distance(self, point1: list, point2: list):
        distance = 0.0
        for a, b in zip(point1, point2):
            distance += math.pow(a - b, 2)
        return math.sqrt(distance)

    def merge_order(self, order_dict: dict, order_list0: list, order_list1: list, target_amount: int):
        if len(order_list0) == target_amount or len(order_list1) == 0:
            return order_list0

        n = math.inf
        order = None
        for v in order_list0:
            for v1 in order_list1:
                dist = self.order_distance(order_dict[v], order_dict[v1])
                if dist < n:
                    n = dist
                    order = v1
        order_list0.append(order)
        order_list1.remove(order)

        return self.merge_order(order_dict, order_list0, order_list1, target_amount)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    start=time.time()
    conn = connect(host='47.110.133.110', port=3389)
    # conn = connect(host='10.0.130.7', port=4000)
    cur = conn.cursor()
    sqlOrderDetail = '''SELECT *,concat(split_part(pos,'-',1),'-',split_part(pos,'-',2)) AS pos_abbr FROM tmp.pick_order_model_inout_25 ORDER BY o_id limit 500'''
    cur.execute(sqlOrderDetail)
    orderDetail = cur.fetchall()
    # sqlCommDist = '''SELECT b.sku sku1,c.sku sku2,a.cost FROM gpdb.yq_sku_cost a JOIN gpdb.yq_sku_map b ON a.id1=b.id
    #                     JOIN gpdb.yq_sku_map c ON a.id2=c.id'''
    sqlCommDist = '''SELECT sku1,sku2,move_cost FROM tmp.pick_model_estimate_3'''
    cur.execute(sqlCommDist)
    CommDist = cur.fetchall()
    conn.close()

    order_list = {}
    for od in orderDetail:
        if not od[0] in order_list:
            order_list[od[0]] = set()
        order_list[od[0]].add(od[3])
    comm_dist = {}
    for cd in CommDist:
        uc.update_dict2(comm_dist, cd[0], cd[1], cd[2])
        uc.update_dict2(comm_dist, cd[1], cd[0], cd[2])

    origin_list = copy.deepcopy(order_list)
    n = 18
    n1 = 20
    hr = Hierarchical(comm_dist)
    sa = sa.SA(comm_dist)
    result_order = []
    # profile.run('hr.fit(n, order_list)')
    # exit(0)
    while len(order_list) >= n:
        hr.fit(n, order_list)
        max_node = max(hr.nodes.values(), key=lambda x: x.count)
        ol = []
        if max_node.count <= n1:
            ol.extend(max_node.order_list)
        elif max_node.left.count >= max_node.right.count:
            ol.extend(hr.merge_order(
                order_list, max_node.left.order_list, max_node.right.order_list, n1))
        else:
            ol.extend(hr.merge_order(
                order_list, max_node.right.order_list, max_node.left.order_list, n1))

        result_order.append(ol)
        for i in ol:
            del order_list[i]
        logging.info("{}   {}".format(len(ol), ol))

    result_order.append(order_list)

    bins_list=[]
    for v in result_order:
        bins = set()
        for v1 in v:
            bins = bins | origin_list[v1]
        bins_list.append(bins)
    
    process_list=[]
    cores = mp.cpu_count()
    process_pool = Pool(cores)
    for v in bins_list:
        process_list.append(process_pool.apply_async(sa.get_route, args=(list(v),)))
    process_pool.close()
    process_pool.join()

    dist_list=[]
    # file=open("/data/web/python/sql.txt",'w')
    file=open(r'd:\sql.txt','w')
    for i,proc in enumerate(process_list):
        res=proc.get()
        dist_list.append(res[1])
        for j,v in enumerate(res[2]):
            file.write("insert into tmp.pick_order_model_output_25 values({},{},'{}'); \r\n".format(i,j,v))
    file.close()
    logging.info('total_dist:{} {}'.format(sum(dist_list),dist_list))
    
    end =time.time()
    logging.info('total time:{}'.format(int(end-start)))