import logging
import math
import time
import copy
import sa_njit
import sys
import profile
import random

from numba import njit,prange,cuda
from numba.typed import Dict
from numba import types
import numba

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
    def __init__(self, np_dist, order_dict, min_batch=18, max_batch=20,max_bin=100,max_param=10):
        if min_batch <= 0:
            raise Exception('Batch amount should be a positive integer!')
        if min_batch > max_batch:
            raise Exception('Max_batch should be greater than min_batch!')

        self.order_dict = order_dict
        self.origin_order_dict=copy.deepcopy(order_dict)
        self.np_dist = np_dist
        self.min_batch = min_batch
        self.max_batch = max_batch
        self.main_node = None
        self.batch_order = []
        self.batch_route = []
        self.batch_distance = []

        self.order_amount=len(order_dict)
        self.max_shape=max_bin*2+max_param
        self.np_order = {}
        self.np_compute=np.empty_like(np_dist,dtype=np.complex128).ravel()
        # self.np_container0=np.empty(self.max_shape,dtype=np.float_)
        self.np_container1=np.empty(max_bin+1,dtype=np.int64)
        self.np_container2=np.empty(max_bin+1,dtype=np.int64)

        logging.warning("step1:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        self.init_np_order()
        get_np_order(self.np_order.reshape(-1,self.max_shape),self.max_shape,self.np_dist,self.np_compute,self.np_container1,self.np_container2)
    
    def init_np_order(self):
        order_amount=len(self.order_dict)
        self.np_order=np.empty((order_amount,order_amount,self.max_shape),dtype=np.int64)
        for k,v in self.order_dict.items():
            for k1,v1 in self.order_dict.items():
                l=len(v)
                l1=len(v1)
                arr=self.np_order[k][k1]
                arr[0:l]=v
                arr[l:l+l1]=v1
                arr[-1]=l
                arr[-2]=l1
                arr[-3]=k+10**10
                arr[-4]=k1+10**10
                arr[-5]=10**10

    def solve(self):
        while len(self.order_dict) > self.max_batch:
            self.fit()
            self.pick_batch_order(self.main_node)
            labels(len(self.batch_order))
        self.batch_order.append(self.order_dict.keys())

    def delete(self, batch):
        for v in batch:
            del self.order_dict[v]

    def fit(self):
        cluster_dist=copy.deepcopy(self.np_order) #待定
        used_orders=set()
        for v in self.batch_order:
            for order in v:
                used_orders.add(order)
        logging.warning("step2:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

        cluster_node_dict = {key: ClusterNode(vec=val, id=key, order_list=np.zeros(1,dtype=np.int64)+key)
                             for key, val in self.order_dict.items()}

        cluster_dist_gpu=cuda.to_device(cluster_dist)
        while len(cluster_node_dict) > 1:
            order_list=np.setdiff1d(range(self.order_amount),list(used_orders))
            length=order_list.shape[0]
            result=np.empty((length,length,3),dtype=np.int64)
            self.wrap(length,cluster_dist_gpu,order_list,result)
            # transform[length,length](cluster_dist1, order_list,result)
            key1,key2,min_dist =get_min_cluster_distance(result)

            # 合并两个聚类
            node1, node2 = cluster_node_dict[key1], cluster_node_dict[key2]
            new_node = ClusterNode(vec=np.union1d(node1.vec,node2.vec),
                                   left=node1,
                                   right=node2,
                                   distance=min_dist,
                                   id=key1,
                                   count=node1.count + node2.count,
                                   order_list=np.concatenate((node1.order_list,node2.order_list)))
            del cluster_node_dict[key1]
            del cluster_node_dict[key2]
            self.new_cluster_distance(cluster_dist, key1, key2)
            for v in cluster_node_dict.values():
                d=bla(v.order_list,new_node.order_list,self.np_order)
                cluster_dist[key1,v.id,-5]=d
            
            used_orders.add(key2)
            cluster_node_dict[key1] = new_node

        self.main_node = cluster_node_dict[key1]

        logging.warning("step3:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    def wrap(self,length,cluster_dist1,order_list,result):
        transform[length,length](cluster_dist1, order_list,result)

    def new_cluster_distance(self, cluster_dist, key1, key2):
        cluster_dist[key1,:,-5]+=10**10
        cluster_dist[:,key2,-5]+=10**10
        cluster_dist[key2,:,-5]+=10**10
        cluster_dist[:,key1,-5]+=10**10

        
    def get_route(self):
        bins_list = []
        for v in self.batch_order:
            bins = set()
            for v1 in v:
                for v2 in self.origin_order_dict[v1]:
                    bins.add(v2)
            bins_list.append(bins)

        process_list = []
        cores = mp.cpu_count()
        process_pool = Pool(cores)
        for v in bins_list:
            process_list.append(process_pool.apply_async(
                sa_njit.get_route, args=(np.array(list(v)),self.np_dist,1000.0,0.0001,0.95,10000.0,10000.0,)))
        process_pool.close()
        process_pool.join()

        for proc in process_list:
            res = proc.get()
            labels(res)
            self.batch_distance.append(res[1])
            self.batch_route.append(res[2])
        logging.warning("sa_njit:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    def merge_order(self, order_list0: list, order_list1: list, target_amount: int):
        if len(order_list0) == target_amount or len(order_list1) == 0:
            return order_list0

        n = math.inf
        order = None
        for v in order_list0:
            for v1 in order_list1:
                dist = self.np_order[v,v1,-5]
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
            self.batch_order.append(list(left_child.order_list))
            self.delete(left_child.order_list)
        if right_count <= self.max_batch and right_count >= self.min_batch:
            self.batch_order.append(list(right_child.order_list))
            self.delete(right_child.order_list)

        if left_count < self.min_batch and right_count < self.min_batch:
            batch = self.merge_order(
                list(left_child.order_list[:]), list(right_child.order_list[:]), self.max_batch)
            self.batch_order.append(batch)
            self.delete(batch)

@cuda.jit
def transform(cluster_dist, order_list,result):
    tid = cuda.threadIdx.x
    bid = cuda.blockIdx.x
    result[bid,tid,0]=cluster_dist[order_list[bid],order_list[tid],-5]
    result[bid,tid,1]=cluster_dist[order_list[bid],order_list[tid],-4]
    result[bid,tid,2]=cluster_dist[order_list[bid],order_list[tid],-3]

@njit
def bla(order_list0,new_order_list,np_order):
    minv=math.inf
    for order in order_list0:
        for order1 in new_order_list:
            if np_order[order,order1,-5]<minv:
                minv=np_order[order,order1,-5]
    return minv

@njit(parallel=True)
def get_min_cluster_distance(cluster_dist):
    ix=np.argmin(cluster_dist)
    c_d=cluster_dist.ravel()
    min_dist=c_d[ix]
    key1=c_d[ix+2]%10**10
    key2=c_d[ix+1]%10**10
    return key1,key2,min_dist

@njit
def get_np_order(np_order,max_shape,np_dist,np_compute,np_container1,np_container2):
    shape=np_order.shape[0]
    for inx in range(shape):
        arr=np_order[inx]
        i=arr[-3]
        j=arr[-4]
        if not i==j:
            d=order_distance(arr,np_dist,np_compute,np_container1,np_container2)
            arr[-5]=d
    return np_order

@njit
def order_distance(order_list,np_dist,np_compute,np_container1,np_container2):
    len0=order_list[-1]
    len1=order_list[-2] 
    for i in range(len0):
        for j in range(len1):
            u=order_list[i]
            v=order_list[len0+j]
            np_compute[i*len1+j] =complex(np_dist[u, v],u*10**10+v)
    np_container1[-1]=0
    main_dist = main_distance(np_compute,np_container1,np_container2,len0,len1)

    pointer=np_container1[-1]
    all_comm = np.unique(order_list[0:len0+len1])
    main_comm = np.unique(np.concatenate((np_container1[:pointer],np_container2[:pointer])))

    main_len=main_comm.shape[0]
    all_len=all_comm.shape[0]
    resi_len=all_len-main_len

    residue_comm=np.empty(resi_len,dtype=np.int64)
    p=0
    for v in all_comm:
        for v1 in main_comm:
            if v==v1:
                break
        else:
            residue_comm[p]=v
            p+=1

    np_container2[-1]=0
    np_compute[:resi_len*all_len]=np_compute[:resi_len*all_len]*0+10**10
    for i1 in range(main_len):
        for j1 in range(resi_len):
            v0=main_comm[i1]
            v1=residue_comm[j1]
            np_compute[i1*resi_len+j1] =complex(np_dist[v0, v1],v1*10**10+v0)

    resi_dist = residue_distance(np_compute, residue_comm,resi_len, all_len,np_dist,np_container2)
    return main_dist + resi_dist

@njit
def main_distance(np_compute,np_container1,np_container2, len0,len1):
    pointer=np_container1[-1]
    if pointer== min(len0,len1):
        return 0

    inx=-1
    minc=math.inf +0j
    for i1 in range(len0*len1):
        if np_compute[i1].real<minc.real:
            minc=np_compute[i1]
            inx=i1
    key0=int(round(minc.imag/10**10))
    key1=int(minc.imag%10**10)
    np_container1[pointer]=key0
    np_container2[pointer]=key1
    np_container1[-1]+=1

    row=int(inx/len1)
    col=int(inx%len1)
    np_compute[row*len1:(row+1)*len1]+=10**10
    for i3 in range(len0):
        np_compute[i3*len1+col]+=10**10
    return minc.real + main_distance(np_compute, np_container1,np_container2,len0,len1)


@njit
def residue_distance(np_compute, residue_comm,residue_len,all_len, np_dist,np_container2):
    pointer=np_container2[-1]
    if pointer == residue_len:
        return 0
    inx=-1
    minc=math.inf +0j
    length=residue_len*all_len
    for ic in range(length):
        if np_compute[ic].real<minc.real:
            minc=np_compute[ic]
            inx=ic
    key0=int(round(minc.imag/10**10))
    np_container2[pointer]=key0
    pointer+=1
    np_container2[-1]+=1
    
    for i in range(length):
        v=np_compute[i]
        k0=int(round(v.imag/10**10))
        if key0==k0:
            np_compute[i]+=10**10

    main_index=residue_len*(residue_len+pointer-1)
    for i1,v1 in enumerate(residue_comm):
        np_compute[i1+main_index]=complex(np_dist[v1,key0],v1*10**10+key0) 
    
    return minc.real + residue_distance(np_compute, residue_comm,residue_len,all_len, np_dist,np_container2)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARN)

    host = '47.110.133.110'
    port = 3389
    date = '2019-05-08'

    argvs = sys.argv
    if len(argvs) > 1:
        host = '10.0.130.7'
        port = 4000
        date = argvs[1]

    conn = connect(host, port)
    cur = conn.cursor()

    # sqlCommDist = '''WITH bin_id AS (
    #                 SELECT sku1,row_number() over(ORDER BY sku1 ) -1 id FROM
    #                 (SELECT DISTINCT sku1 FROM tmp.pick_model_estimate_3 WHERE  version=5 ) a
    #                 )
    #                 SELECT q.id,r.id,p.move_cost FROM tmp.pick_model_estimate_3 p LEFT JOIN bin_id q ON p.sku1=q.sku1 LEFT JOIN bin_id	r ON p.sku2=r.sku1 WHERE  p.version=5 and q.id<=600 and r.id<=600 limit 10000000'''
    # cur.execute(sqlCommDist)
    # CommDist = cur.fetchall()
    # comm_dist = {}
    # for cd in CommDist:
    #     uc.update_dict2(comm_dist, cd[0], cd[1], cd[2])
    #     uc.update_dict2(comm_dist, cd[1], cd[0], cd[2])

    k=600
    np_dist=np.zeros([k,k],dtype=np.int64)
    for i in range(k):
        for j in range(k):
            np_dist[i][j]=random.randint(1, 50) #uc.get_dict_value2(comm_dist,i,j,0)
            
    sqlBatchOrder = '''SELECT distinct period FROM tmp.pick_order_model_input_2 a 
    	where EXISTS ( SELECT 1 FROM tmp.pick_model_location_3 b WHERE a.pos_abbr = b.loc) ORDER BY period'''
    cur.execute(sqlBatchOrder)
    batchOrder = cur.fetchall()

    for v in batchOrder:
        period = v[0]
        sqlOrderDetail = '''SELECT * FROM tmp.pick_order_model_input_2 a  WHERE period = {}
    	    AND EXISTS ( SELECT 1 FROM tmp.pick_model_location_3 b WHERE a.pos_abbr = b.loc) limit 5000'''.format(period)
        cur.execute(sqlOrderDetail)
        orderDetail = cur.fetchall()
        conn.close()

        order_dict = {} 
        for od in orderDetail:
            if not od[2] in order_dict:
                order_dict[od[2]] = []
            order_dict[od[2]].append(int(od[4])*36+int(od[5]))
        order_dict1={}
        for i,v in enumerate(order_dict.items()):
            order_dict1[i]=np.unique(v[1]) # 库位去重



        max_param=10
        max_bin=100
        start = time.time()
        hr = Hierarchical(np_dist, order_dict1, 14, 16,max_bin,max_param)
        # profile.run('hr = Hierarchical(np_dist, order_dict1, 14, 16,max_bin,max_param)')
        profile.run('hr.solve()')
        exit(0)
        hr.solve()
        hr.get_route()
        end =time.time()
        labels(end-start)
        exit(0)

        sql0 = "INSERT OVERWRITE tmp.pick_order_model_output_by_pos PARTITION(data_dt = CAST('2019-05-15' AS VARCHAR(10)),period = {}) VALUES".format(
            period)
        sql1 = ''
        for i, v in enumerate(hr.batch_route): 
            for j, v1 in enumerate(v):
                sql1 += "({},{},'{}',{},'{}',{}),".format(i, j, v1, uc.get_dict_value2(
                    comm_dist, v[j], v[j-1], 0) if not j == 0 else 0, '', int(end-start))
        sql1 = sql1[:len(sql1)-1]

        conn = connect(host, port)
        cur = conn.cursor()
        cur.execute(sql0+sql1)

        logging.warning('period:{}'.format(period))
        logging.warning('total_order:{}'.format(
            sum([len(i) for i in hr.batch_order])))
        logging.warning('total_dist:{} {}'.format(
            sum(hr.batch_distance), hr.batch_distance))
