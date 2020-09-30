import math
import random
import copy
import time
import utilities.collection as uc
import logging
from impala.dbapi import connect
from multiprocessing import Process, Pool
import multiprocessing as mp
import profile

class SA(object):
    def __init__(self, commodity_dist={},tmax=1000,tmin=1e-8,cx=0.95,it=10000,qt=10000):
        '''commodity_dist库位距离表, tmax初始最高温度，tmin最低温度，cx降温系数, it迭代次数，qt退出阈值'''
        self.commodity_dist = commodity_dist
        self.tmax = tmax
        self.tmin = tmin
        self.cx = cx
        self.it = it
        self.qt = qt

    def get_route(self, comm_list: list):
        if len(comm_list)<=1:
            return 0,0,[]
        start=time.time()
        count = 0
        old_comm_list = copy.deepcopy(comm_list)
        # 模拟退火过程
        while(self.tmax > self.tmin):
            for _ in range(self.it):
                new_comm_list = self.get_new_order(old_comm_list)
                de = self.cj(new_comm_list)-self.cj(old_comm_list)
                if de < 0:
                    count = 1
                    old_comm_list = new_comm_list
                else:
                    count = count+1
                    d = math.e**(-de/self.tmax)
                    if random.random() < d:
                        old_comm_list = new_comm_list
                    else:
                        pass
            self.tmax = self.tmax * self.cx
            if count > self.qt:
                break
        end=time.time()
        print('param:cx:{},it:{},qt:{}'.format(self.cx,self.it,self.qt))
        print('time:{}s'.format(end-start))
        print('target:{}'.format(self.cj(old_comm_list)))
        print(old_comm_list)

        return count,self.cj(old_comm_list),old_comm_list


    def comm_distance(self, comm1, comm2):
        if comm1 == comm2:
            return 0
        d=uc.get_dict_value2(self.commodity_dist, comm1, comm2, math.inf)
        if d == math.inf:
            raise Exception('库位间距不存在：{}-{}'.format(comm1, comm2))
        return d

    def cj(self, comm_list):
        sum=0
        for i in range(len(comm_list)-1):
            sum += self.comm_distance(comm_list[i], comm_list[i+1])
        return sum

    def get_new_order(self,comm_list):
        a=random.randint(0,2)
        if a==0:
            return self.exchange(comm_list)
        elif a==1:
            return self.reverse(comm_list)
        else:
            return self.move(comm_list)

    def exchange(self, comm_list):
        length=len(comm_list)
        a=random.randint(0, length-1)
        b=random.randint(0, length-1)

        tem_list=comm_list[:]
        temp=tem_list[a]
        tem_list[a]=tem_list[b]
        tem_list[b]=temp
        return tem_list
    
    def reverse(self,comm_list):
        length=len(comm_list)
        a=random.randint(0, length-1)
        b=random.randint(0, length-1)

        if a>b:
            tem=a
            a=b
            b=tem

        tem_list0=comm_list[0:a]
        tem_list1=comm_list[a:b]
        tem_list2=comm_list[b:length]
        tem_list1.reverse()
        return tem_list0+tem_list1+tem_list2
    
    def move(self,comm_list):
        length=len(comm_list)
        a=random.randint(0, length-1)
        b=random.randint(0, length-1)

        if a>b:
            tem=a
            a=b
            b=tem

        tem_list0=comm_list[0:a]
        tem_list1=comm_list[a:b]
        tem_list2=comm_list[b:b+1]
        tem_list3=comm_list[b+1:length]

        return tem_list0+tem_list2+tem_list1+tem_list3

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    # conn=connect(host='47.110.133.110', port=3389)
    conn = connect(host='10.0.130.7', port=4000)
    cur=conn.cursor()
    sqlCommDist='SELECT * FROM tmp.pick_model_estimate_3 where version=4'
    cur.execute(sqlCommDist)
    CommDist=cur.fetchall()
    conn.close()

    comm_dist={}
    for cd in CommDist:
        uc.update_dict2(comm_dist, cd[0], cd[1], cd[4])
        uc.update_dict2(comm_dist, cd[1], cd[0], cd[4])

    test=['F-21', 'E-29', 'E-31', 'E-30', 'E-32', 'E-34', 'E-33', 'E-36', 'E-38', 'E-42', 'D-11', 'C-38', 'C-33', 'C-31', 'C-29', 'C-30', 'B-28', 'A-32', 'A-29', 'B-26', 'B-24', 'B-23', 'B-22', 'B-19', 'B-20', 'B-18', 'A-43', 'A-44', 'A-50', 'A-51', 'A-56', 'A-57', 'B-2', 'B-4', 'B-7', 'B-12', 'B-13', 'C-44', 'C-45', 'C-48', 'C-49', 'C-54', 'C-53', 'D-3', 'D-2', 'F-2', 'F-5', 'F-9', 'F-10', 'E-48', 'E-46', 'D-16', 'D-20', 'D-19', 'D-23', 'E-27', 'E-25', 'E-24', 'E-21', 'E-20', 'E-19', 'E-18', 'E-16', 'E-17', 'E-22', 'E-23', 'E-26', 'E-28', 'D-31', 'D-34', 'D-35', 'D-33', 'D-36', 'D-38', 'D-37', 'D-40', 'D-41', 'C-14', 'B-43', 'B-47', 'B-51', 'A-1', 'A-4', 'A-3', 'A-7', 'A-9', 'A-14', 'A-13', 'B-42', 'B-41', 'B-40', 'B-39', 'B-37', 'B-36', 'B-35', 'B-33', 'B-34', 'B-32', 'C-27', 'C-28', 'A-28', 'A-26', 'A-24', 'A-22', 'A-23', 'A-21', 'A-19', 'A-18', 'A-16', 'A-17', 'A-15', 'B-44', 'C-17', 'C-19', 'C-22', 'C-24', 'C-21', 'C-20', 'C-18', 'C-16', 'D-43', 'D-45', 'D-47', 'D-46', 'D-48', 'D-49', 'D-50', 'D-51', 'D-53', 'C-2', 'E-2', 'E-1', 'E-3', 'E-4', 'E-6', 'E-7', 'E-10', 'E-8', 'E-12', 'E-9', 'E-11', 'E-14', 'D-42', 'E-13', 'D-44', 'C-13', 'C-11', 'C-10', 'C-12', 'C-9', 'C-8', 'C-7', 'C-6', 'C-5']
    sa=SA(comm_dist,cx=0.9,it=1000,qt=1000)
    

    profile.run('sa.get_route(test)')
    # process_list=[]
    # cores = mp.cpu_count()
    # process_pool = Pool(cores)
    # for v in range(1000,30000,2000):
    #     sa=SA(comm_dist,cx=0.5,it=v,qt=v)
    #     process_list.append(process_pool.apply_async(sa.get_route, args=(test,)))
    # process_pool.close()
    # process_pool.join()

    