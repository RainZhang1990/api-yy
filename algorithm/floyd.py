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
    region = ['A', 'B', 'C', 'D', 'E', 'F']
    sql0 = "INSERT OVERWRITE tmp.pick_model_estimate_3 PARTITION(version = {}) VALUES".format(4)
    sql1 = ''
    d0 = 0.5
    length = 28

    for i in range(-1, length):
        for j in range(len(region)):
            d1 = 1
            if i % 7 == 6 and j < len(region)-1:
                d1 = 1
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+1, region[j+1],2*(length-i-2)+1, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+1, region[j+1],2*(length-i-2)+2, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+1, region[j+1],2*(length-i-2)+3, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+1, region[j+1],2*(length-i-2)+4, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+2, region[j+1],2*(length-i-2)+1, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+2, region[j+1],2*(length-i-2)+2, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+2, region[j+1],2*(length-i-2)+3, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+2, region[j+1],2*(length-i-2)+4, 0, 0, d1)

                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+3, region[j+1],2*(length-i-2)+1, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+3, region[j+1],2*(length-i-2)+2, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+3, region[j+1],2*(length-i-2)+3, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+3, region[j+1],2*(length-i-2)+4, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+4, region[j+1],2*(length-i-2)+1, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+4, region[j+1],2*(length-i-2)+2, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+4, region[j+1],2*(length-i-2)+3, 0, 0, d1)
                sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+4, region[j+1],2*(length-i-2)+4, 0, 0, d1)
            if i % 7 == 6:
                d1 = 2
            sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+1, region[j],2*i+2, 0, 0, d0)
            sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+1, region[j],2*i+3, 0, 0, d1)
            sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+1, region[j],2*i+4, 0, 0, d1)
            sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+2, region[j],2*i+3, 0, 0, d1)
            sql1 += "('{}-{}','{}-{}',{},{},{}),".format(region[j],2*i+2, region[j],2*i+4, 0, 0, d1)

    sql1 += "('A-59','A-57',0,0,1),"

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

    conn = connect(host, port)
    cur = conn.cursor()

    sqlCommDist = ' SELECT * FROM tmp.pick_model_estimate_3 '
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

    sql0 = "INSERT OVERWRITE tmp.pick_model_estimate_3 PARTITION(version = {}) VALUES".format(4)
    sql1 = ''
    for k, v in comm_dist.items():
        for k1, v1 in v.items():
            sql1 += "('{}','{}',{},{},{}),".format(k, k1, 0, 0, v1)
    sql1 = sql1[:len(sql1)-1]

    conn = connect(host, port)
    cur = conn.cursor()
    cur.execute(sql0+sql1)
