import math
import random
import copy
import time
import logging
import profile

import numpy as np
import numba
from numba import njit

from impala.dbapi import connect
from multiprocessing import Process, Pool
import multiprocessing as mp

@njit
def get_route(comm_list,np_dist,tmax=1000.0,tmin=0.0001,cx=0.95,it=10000.0,qt=10000.0):
    # if len(comm_list)<=1:
    #     return tmax,cx,it,qt,0,0
    count = 0
    old_comm_list =comm_list
    new_comm_list =np.empty_like(comm_list)
    # 模拟退火过程
    while(tmax > tmin):
        for _ in range(it):
            get_new_order(old_comm_list,new_comm_list)
            de = cj(new_comm_list,np_dist)-cj(old_comm_list,np_dist)
            if de < 0:
                count = 1
                tem=old_comm_list
                old_comm_list = new_comm_list
                new_comm_list=tem
            else:
                count = count+1
                d = math.e**(-de/tmax)
                if random.random() < d:
                    tem=old_comm_list
                    old_comm_list = new_comm_list
                    new_comm_list=tem
                else:
                    pass
        tmax = tmax * cx
        if count > qt:
            break

    # return tmax,tmin,cx,it,qt,count,cj(old_comm_list,np_dist)
    return old_comm_list

@njit
def cj(comm_list,np_dist):
    sum=0
    for i in range(len(comm_list)-1):
        sum += np_dist[comm_list[i]][comm_list[i+1]]
    return sum

@njit
def get_new_order(comm_list,new_comm_list):
    new_comm_list[:]=comm_list
    # for i,v in enumerate(comm_list):
    #     new_comm_list[i]=v

    rnd=random.randint(0,2)
    length=comm_list.shape[0]
    a=random.randint(0, length-1)
    b=random.randint(0, length-1)
    if a==b:
        return comm_list
    if a>b:
        tem=a
        a=b
        b=tem

    result=None
    if rnd==0:
        result= exchange(comm_list,new_comm_list,a,b)
    elif rnd==1:
        result= reverse(comm_list,new_comm_list,a,b)
    else:
        result= move(comm_list,new_comm_list,a,b)
    return result

@njit
def exchange(comm_list,new_comm_list,a,b):
    new_comm_list[a]=comm_list[b]
    new_comm_list[b]=comm_list[a]

@njit
def reverse(comm_list,new_comm_list,a,b):
    for i,v in enumerate(range(b,a,-1)):
        new_comm_list[a+i+1]=comm_list[v]

@njit
def move(comm_list,new_comm_list,a,b):
    for i in range(a,b):
        new_comm_list[i+1]=comm_list[i]
    if a<b:
        new_comm_list[a]=comm_list[b]

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    start=time.time()
    res=get_route(comm_list,np_dist,tmax=1000,tmin=0.0001,cx=0.9,it=20000,qt=20000)
    labels(res)
    end=time.time()
    labels('time:{}s'.format(end-start))

    