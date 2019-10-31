import logging
import math
import time
import copy
import sa_njit
import sys
import profile
import random

from numba import njit,prange,cuda
from numba import types
import numba

import numpy as np
import numpy.random as nr
from impala.dbapi import connect
from multiprocessing import Process, Pool
import multiprocessing as mp

class Hierarchical(object):
    def __init__(self, np_dist, order_dict, min_batch=18, max_batch=20,max_bin=64):
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
        self.cluster = None
        self.batch_order = []
        self.batch_route = []
        self.batch_distance = []

        self.order_amount=len(order_dict)
        self.max_shape=max_bin*2
        
        logging.warning("step1:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

        self.order_list=np.empty((self.order_amount,max_bin),dtype=np.int16)
        for k,v in self.order_dict.items():
            length=len(v)
            self.order_list[k,:length]=v
            self.order_list[k,-1]=length

        self.np_order_device=cuda.device_array((self.order_amount,self.order_amount,self.max_shape,4),dtype=np.int16)
        init_np_order[self.order_amount,self.order_amount](self.order_list,self.np_order_device)
        logging.warning("step1.1:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

        get_np_order[(self.order_amount,self.order_amount),self.max_shape](self.np_order_device,self.np_dist)
        logging.warning("step1.2:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))        
        self.np_order_host=self.np_order_device.copy_to_host()
        
        np_cluster=np.empty((self.order_amount*2,self.order_amount+10),dtype=np.int16)
        for i in self.order_dict.keys():
            np_cluster[i,0]=i #order list
            np_cluster[i,-1]=1 #order length
            np_cluster[i,-2]=i #id
            np_cluster[i,-3]=0 #node status 0:待合并 1：已合并
            np_cluster[i,-4]=2**15-1 #min dist
            np_cluster[i,-5]=-1 #min index
            np_cluster[i,-6]=-1 #node dist
            np_cluster[i,-7]=-1 #left
            np_cluster[i,-8]=-1 #right
            np_cluster[i,-9]=0 #分类状态
        np_cluster[-1,0]=self.order_amount*2 #总长度
        self.np_cluster=np_cluster
        
        batch_amount=int(self.order_amount/self.min_batch)+1
        self.batch_order_device=cuda.device_array((batch_amount,self.max_batch+1))

    def solve(self):
        self.fit()

    def fit(self):
        logging.warning("step2:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))                
        self.np_cluster[-1,1]=self.order_amount # 原始指针
        self.np_cluster[-1,2]=self.max_batch # 最大订单数
        self.np_cluster[-1,3]=self.min_batch # 最小订单数
        self.np_cluster[-1,4]=0 #批次订单数 终止标记
        self.np_cluster[-1,5]=-1 #当前批次数
        self.np_cluster[-1,6]=self.order_amount #动态指针
        self.np_cluster[-1,7]=0 #已分类订单数
        fit_gpu[1,self.order_amount](self.np_order_device,self.np_cluster,self.batch_order_device)

        batch_order=self.batch_order_device.copy_to_host()
        logging.warning("step3:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
        exit(0)
        
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
            self.batch_distance.append(res[-1])
            self.batch_route.append(res[2])
        logging.warning("sa_njit:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))


@cuda.jit
def fit_gpu(np_order,np_cluster,batch_order):
    while(np_cluster[-1,7]<np_cluster[-1,1]):
    # while(np_cluster[-1,4]==0):
        tid = cuda.threadIdx.x
        np_cluster[tid,-3]=np_cluster[tid,-9]
        np_cluster[tid,-4]=2**15-1
        np_cluster[tid+np_cluster[-1,1],-3]=1
        np_cluster[tid+np_cluster[-1,1],-4]=2**15-1
        if tid==0:
            np_cluster[-1,4]=0 #标记开启
            np_cluster[-1,5]+=1 #当前批次数
            np_cluster[-1,6]=np_cluster[-1,1] #重置动态指针
        cuda.syncthreads()
        while(np_cluster[-1,4]==0):
            length=np_cluster[-1,0]

            if np_cluster[tid,-3]==0: #计算类最小值
                minv=2**15-1
                inx=0
                for i in range(length):
                    len0=np_cluster[i,-1]
                    len1=np_cluster[tid,-1]
                    if np_cluster[i,-3]==0 and (len1<len0 or (len0==len1 and tid<i)):
                        # for v0 in range(len0):
                        #     for v1 in range(len1):
                        #         dist=100-len0+len1
                        #         if dist<minv:
                        #             minv=dist
                        #             inx=i
                        for v0 in np_cluster[i,:len0]:
                            for v1 in np_cluster[tid,:len1]:
                                dist=np_order[v1,v0,-1,2]
                                if dist<minv:
                                    minv=dist
                                    inx=i
                np_cluster[tid,-4]=minv
                np_cluster[tid,-5]=inx
            cuda.syncthreads()

            if np_cluster[tid,-3]==0:
                minv=2**15-1
                inx1=0
                for i1 in range(length):
                    dist=np_cluster[i1,-4]
                    if dist<minv and np_cluster[i1,-3]==0:
                        minv=dist
                        inx1=i1
                #合并类
                if tid==inx1:
                    matched_inx=np_cluster[tid,-5]
                    np_cluster[matched_inx,-3]=1
                    np_cluster[tid,-3]=1
                    len00=np_cluster[matched_inx,-1]
                    len11=np_cluster[tid,-1]
                    new_length=len00+len11
                    new_id=np_cluster[-1,6]
                    for j in range(len00):
                        np_cluster[new_id,j]=np_cluster[matched_inx,j]
                    for j1 in range(len11):
                        np_cluster[new_id,len00+j1]=np_cluster[tid,j1]
                    np_cluster[new_id,-1]=new_length
                    np_cluster[new_id,-2]=new_id
                    np_cluster[new_id,-3]=0
                    np_cluster[new_id,-4]=2**15-1
                    np_cluster[new_id,-6]=minv
                    np_cluster[new_id,-7]=tid
                    np_cluster[new_id,-8]=matched_inx
                    np_cluster[-1,6]+=1
                    tid=new_id
                    if np_cluster[-1,3]<=new_length<=np_cluster[-1,2] or np_cluster[-1,7]+new_length==np_cluster[-1,1]:
                        for k in range(new_length):
                            batch_order[np_cluster[-1,5],k]=np_cluster[new_id,k]
                            np_cluster[np_cluster[new_id,k],-9]=1
                        batch_order[np_cluster[-1,5],-1]=new_length
                        np_cluster[-1,4]=1 #标记中止
                        np_cluster[-1,7]+=new_length #已分类订单数

                    elif new_length>np_cluster[-1,2]:
                        for k in range(np_cluster[-1,2]):
                            batch_order[np_cluster[-1,5],k]=np_cluster[new_id,k]
                            np_cluster[np_cluster[new_id,k],-9]=1
                        batch_order[np_cluster[-1,5],-1]=np_cluster[-1,2]
                        np_cluster[-1,4]=1 #标记中止
                        np_cluster[-1,7]+=np_cluster[-1,2]
            cuda.syncthreads()
    


@cuda.jit
def init_np_order(order_list,np_order):
    block_id_x=cuda.blockIdx.x
    thread_id = cuda.threadIdx.x
    arr=np_order[block_id_x,thread_id]

    if block_id_x>=thread_id:
        for i in range(arr.shape[0]): #初始化状态
            arr[i,1]=0

        l=order_list[block_id_x,-1]
        l1=order_list[thread_id,-1]
        for i in range(l):
            arr[i,0]=order_list[block_id_x,i]
            arr[i,1]=10
        for i in range(l1):
            arr[l+i,0]=order_list[thread_id,i]
            arr[l+i,1]=11
        arr[-1,0]=l+l1 #长度
        arr[-1,1]=-1 #global status
        arr[-1,2]=0 #sum 
        arr[-1,3]=block_id_x
        # arr[-1,4]=thread_id

@cuda.jit
def get_np_order(np_order,np_dist):
    block_id_x=cuda.blockIdx.x
    block_id_y=cuda.blockIdx.y
    thread_id = cuda.threadIdx.x
    arr=np_order[block_id_x,block_id_y]
    length=arr[-1,0]
    while(not arr[-1,1]==-3 and block_id_x>=block_id_y):
        if arr[-1,1]==-1: #一阶段
            status=arr[thread_id,1]
            if 10<=status<=11:
                opposite=21-status
                minv=2**15-1
                inx=-1
                for i in range(length):
                    if arr[i,1]==opposite:
                        dist=np_dist[arr[i,0],arr[thread_id,0]]
                        if dist<minv:
                            minv=dist
                            inx=i
                arr[thread_id,2]=minv
                arr[thread_id,3]=inx
            cuda.syncthreads()

            if status<0:
                minv=2**15-1
                inx1=-1
                for i1 in range(length):
                    dist=arr[i1,2]
                    if dist<minv and 10<=arr[i1,1]<=11:
                        minv=dist
                        inx1=i1
                if minv==2**15-1:
                    arr[-1,1]=-2
                    for i2 in range(length):
                        if 10<=arr[i2,1]<=11:
                            arr[i2,1]=13
                else:
                    matched_inx=arr[inx1,3]
                    arr[inx1,1]=12
                    arr[matched_inx,1]=12
                    arr[-1,2]+=arr[inx1,2]
            cuda.syncthreads()

        if arr[-1,1]==-2: #二阶段
            status=arr[thread_id,1]
            if status==13:
                opposite=12
                minv=2**15-1
                inx=-1
                for i in range(length):
                    if arr[i,1]==opposite:
                        dist=np_dist[arr[i,0],arr[thread_id,0]]
                        if dist<minv:
                            minv=dist
                            inx=i
                arr[thread_id,2]=minv
                arr[thread_id,3]=inx
            cuda.syncthreads()

            if status<0:
                minv=2**15-1
                inx1=-1
                for i1 in range(length):
                    dist=arr[i1,2]
                    if dist<minv and arr[i1,1]==13:
                        minv=dist
                        inx1=i1
                if minv==2**15-1:
                    arr[-1,1]=-3
                else:
                    arr[inx1,1]=12
                    arr[-1,2]+=arr[inx1,2]
            cuda.syncthreads()
    if block_id_x>block_id_y:
        np_order[block_id_y,block_id_x,-1,2]=np_order[block_id_x,block_id_y,-1,2]

def order_integrity_check(batch_order,n):
    for i in range(n):
        for l in batch_order:
            for order in l:
                if order==i:
                    break
            else:
                continue
            break
        else:
            raise Exception('Order missing') 

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.WARN)

    host = '47.110.133.110'
    port = 3389
    date = '2019-05-15'

    argvs = sys.argv
    if len(argvs) > 1:
        host = '10.0.130.7'
        port = 4000
        date = argvs[1]

    conn = connect(host, port)
    cur = conn.cursor()

    sqlCommDist = '''SELECT * FROM tmp.pick_model_estimate_3 WHERE  version=5'''
    cur.execute(sqlCommDist)
    CommDist = cur.fetchall()
    k=432
    np_dist=np.empty([k,k],dtype=np.int16)
    for cd in CommDist:
        np_dist[cd[2],cd[3]]=cd[4]
            
    sqlBatchOrder = '''SELECT DISTINCT period FROM tmp.pick_order_model_input_2 WHERE data_dt = '{}' ORDER BY period'''.format(date)
    cur.execute(sqlBatchOrder)
    batchOrder = cur.fetchall()

    for v in batchOrder:
        period = v[0]
        sqlOrderDetail = '''SELECT dense_rank() over(ORDER BY o_id)-1 AS o_id_small,* FROM tmp.pick_order_model_input_2 
                            WHERE period = {} AND data_dt = '{}' limit 6000'''.format(period,date)
        cur.execute(sqlOrderDetail)
        orderDetail = cur.fetchall()
        conn.close()

        order_dict = {} 
        for od in orderDetail:
            if not od[0] in order_dict:
                order_dict[od[0]] = set()
            order_dict[od[0]].add(od[9])
        for k,v in order_dict.items():
            order_dict[k]=list(v) 



        start = time.time()
        hr = Hierarchical(np_dist, order_dict, 14, 16)
        # profile.run('hr = Hierarchical(np_dist, order_dict1, 14, 16,max_bin,max_param)')
        # profile.run('hr.solve()')
        # exit(0)
        hr.solve()
        order_integrity_check(hr.batch_order,hr.order_amount)
        # hr.get_route()
        end =time.time()
        labels(end-start)

        sql0 = "INSERT OVERWRITE tmp.pick_order_model_output_by_pos PARTITION(data_dt = CAST('' AS VARCHAR(10)),period = {}) VALUES".format(period,date)
        sql1 = ''

        for i, v in enumerate(hr.batch_distance): 
            sql1 += "({},{},'{}',{},'{}',{}),".format(i, 0, 0,  v, '', int(end-start))
        # for i, v in enumerate(hr.batch_route): 
        #     for j, v1 in enumerate(v):
        #         sql1 += "({},{},'{}',{},'{}',{}),".format(i, j, v1, np_dist[v[j], v[j-1]] if not j == 0 else 0, '', int(end-start))
        sql1 = sql1[:len(sql1)-1]

        conn = connect(host, port)
        cur = conn.cursor()
        cur.execute(sql0+sql1)

        logging.warning('period:{}'.format(period))
        logging.warning('total_order:{}'.format(
            sum([len(i) for i in hr.batch_order])))
        logging.warning('total_dist:{} {}'.format(
            sum(hr.batch_distance), hr.batch_distance))