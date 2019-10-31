import math
import random
import copy
import time
import utilities.collection as uc
import logging

import numpy as np
import numba
from numba import njit
from numba import cuda
from numba.cuda.random import create_xoroshiro128p_states, xoroshiro128p_uniform_float32

from impala.dbapi import connect

@cuda.jit
def get_route(target,rng_states,comm_list,tem_list,np_dist,tmax=1000.0,tmin=0.001,cx=0.5,it=5000.0,qt=5000.0):
    count = 0
    index=cuda.grid(1)
    old_comm_list =comm_list[index]
    new_comm_list=tem_list[index]
    
    # 模拟退火过程
    while(tmax > tmin):
        for i in range(it):
            get_new_order(old_comm_list,new_comm_list,rng_states,index)
            de = cj(new_comm_list,np_dist)-cj(old_comm_list,np_dist)
            if de < 0:
                count = 1
                tem=old_comm_list
                old_comm_list = new_comm_list
                new_comm_list=tem
            else:
                count = count+1
                d = math.e**(-de/tmax)
                if xoroshiro128p_uniform_float32(rng_states,index) < d:
                    tem=old_comm_list
                    old_comm_list = new_comm_list
                    new_comm_list=tem
                else:
                    pass
        tmax = tmax * cx
        if count > qt:
            break
    cuda.atomic.min(target,0,cj(old_comm_list,np_dist))

@cuda.jit(device=True)
def cj(comm_list,np_dist):
    sum=0
    for i in range(len(comm_list)-1):
        x=comm_list[i]
        y=comm_list[i+1]
        sum += np_dist[x,y]
    return sum

@cuda.jit(device=True)
def get_new_order(comm_list,new_comm_list,rng_states,index):
    for i,v in enumerate(comm_list):
        new_comm_list[i]=v

    rnd1=xoroshiro128p_uniform_float32(rng_states,index)
    rnd2=xoroshiro128p_uniform_float32(rng_states,index)
    rnd3=xoroshiro128p_uniform_float32(rng_states,index)
    length=comm_list.shape[0]
    rnd=int(rnd1*10)%3
    a=int(rnd2*10000)%length
    b=int(rnd3*10000)%length

    if rnd==0:
        exchange(comm_list,new_comm_list,a,b)
    elif rnd==1:
        reverse(comm_list,new_comm_list,a,b)
    else:
        move(comm_list,new_comm_list,a,b)

@cuda.jit(device=True)
def exchange(comm_list,new_comm_list,a,b):
    new_comm_list[a]=comm_list[b]
    new_comm_list[b]=comm_list[a]

@cuda.jit(device=True)
def reverse(comm_list,new_comm_list,a,b):
    for i,v in enumerate(range(b,a,-1)):
        new_comm_list[a+i+1]=comm_list[v]

@cuda.jit(device=True)
def move(comm_list,new_comm_list,a,b):
    for i in range(a,b):
        new_comm_list[i+1]=comm_list[i]
    if a<b:
        new_comm_list[a]=comm_list[b]

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    conn=connect(host='47.110.133.110', port=3389)
    # conn = connect(host='10.0.130.7', port=4000)
    cur=conn.cursor()
    sqlCommDist='''WITH bin_id AS (
                    SELECT sku1,row_number() over(ORDER BY sku1 ) -1 id FROM
                    (SELECT DISTINCT sku1 FROM tmp.pick_model_estimate_3 WHERE  version=4 ) a
                    )
                    SELECT q.id,r.id,p.move_cost FROM tmp.pick_model_estimate_3 p LEFT JOIN bin_id q ON p.sku1=q.sku1 LEFT JOIN bin_id	r ON p.sku2=r.sku1 WHERE  p.version=4 and q.id<=200 and r.id<=200 limit 1000000'''
    cur.execute(sqlCommDist)
    CommDist=cur.fetchall()
    conn.close()

    comm_dist={}
    for cd in CommDist:
        uc.update_dict2(comm_dist, cd[0], cd[1], cd[2])
        uc.update_dict2(comm_dist, cd[1], cd[0], cd[2])


    k=200
    target=np.ones(5)*math.inf
    block=128
    thread=1
    total=block*thread
    comm_list=np.arange(total*k,dtype=int).reshape(total,k)%k
    tem_list=np.empty_like(comm_list)
    for i in range(total):
        random.shuffle(comm_list[i])
    np_dist=np.empty([k,k],dtype=float)
    for i in range(k):
        for j in range(k):
            np_dist[i][j]=uc.get_dict_value2(comm_dist,i,j,0)

    start=time.time()

    rng_states = create_xoroshiro128p_states(block*thread, seed=1)
    get_route[block,thread](target,rng_states,comm_list,tem_list,np_dist,1000.0,0.01,0.95,10000,10000)
    # res.sort()
    labels(target)

    end=time.time()
    labels('time:{}s'.format(end-start))

    