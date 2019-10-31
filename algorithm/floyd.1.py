import logging
import math
import time
import copy
import sa
import sys

import numpy as np
import numpy.random as nr
from impala.dbapi import connect

import utilities.collection as uc

host = '47.110.133.110'
port = 3389


def init_model():
    sql0 = "INSERT OVERWRITE tmp.pick_model_estimate_3 PARTITION (version = {}) VALUES".format(5)
    sql1 = ''
            
    d1 = 1
    row=12
    col=36
    for i in range(row):
        for j in range(col-1):
            sql1 += "('B-{}-{}','B-{}-{}',{},{},{}),".format(i+1,j+1, i+1,j+2, 0, 0, d1)

    for i in range(row-1):
            sql1 += "('B-{}-{}','B-{}-{}',{},{},{}),".format(i+1,1, i+2,col, 0, 0, d1)
            sql1 += "('B-{}-{}','B-{}-{}',{},{},{}),".format(i+1,col, i+2,1, 0, 0, d1)

    sql1 = sql1[:len(sql1)-1]

    conn = connect(host, port)
    cur = conn.cursor()
    cur.execute(sql0+sql1)


def floyd(comm: set, comm_dist: dict):
    for i in comm:
        for j in comm:
            for k in comm:
                new_dist = uc.get_dict_value2(
                    comm_dist, i, j, math.inf)+uc.get_dict_value2(comm_dist, i, k, math.inf)
                if new_dist < uc.get_dict_value2(comm_dist, j, k, math.inf):
                    uc.update_dict2(comm_dist, j, k, new_dist)
                    uc.update_dict2(comm_dist, k, j, new_dist)
    return comm_dist


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    # init_model()
    # exit(0)

    conn = connect(host, port)
    cur = conn.cursor()

    sqlCommDist = ' SELECT * FROM tmp.pick_model_estimate_3 where version=5'
    cur.execute(sqlCommDist)
    CommDist = cur.fetchall()
    comm_dist = {}
    comm = set()
    for cd in CommDist:
        comm.add(cd[0])
        comm.add(cd[1])
        uc.update_dict2(comm_dist, cd[0], cd[1], cd[4])
        uc.update_dict2(comm_dist, cd[1], cd[0], cd[4])

    comm_dist = floyd(comm, comm_dist)

    sql0 = "INSERT OVERWRITE tmp.pick_model_estimate_3 PARTITION(version = {}) VALUES".format(5)
    sql1 = ''
    for k, v in comm_dist.items():
        for k1, v1 in v.items():
            sql1 += "('{}','{}',{},{},{}),".format(k, k1, 0, 0, v1)
    sql1 = sql1[:len(sql1)-1]

    conn = connect(host, port)
    cur = conn.cursor()
    cur.execute(sql0+sql1)
