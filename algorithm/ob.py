import numpy
import pulp
import time
import logging
import random
import json
import requests
# from gurobipy import *

M = 99999


def getJoinKey(key1, key2):
    return str(key1)+"-"+str(key2)


def getCategoryJoinKey(skus: dict):
    s = ''
    for key, val in skus.items():
        fmt = '{}_{}'.format(key, val)
        if s == '':
            s = fmt
        else:
            s = getJoinKey(s, fmt)
    return s


class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


def ob_lp(orderDetail: dict, minBatchAmount):
    """
    orderDetail:订单明细，以数组【字典】的方式传入.
    minBatchAmount：批次最小订单数量.
    """
    orderDistinct = orderDetail.keys()

    logging.info("step1:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    model = pulp.LpProblem("OrderGrouping", pulp.LpMaximize)

    lpVariableDict_order = Vividict()
    lpVariableDict_cate = Vividict()

    categoryDict = {}  # 订单内各sku数量-1 生成分类类别
    for order, detail in orderDetail.items():
        for sku, amount in detail.items():
            temDict = {}
            n = amount-1
            if n > 0:
                temDict[sku] = n
            for sku1, amount1 in detail.items():
                if not sku == sku1:
                    temDict[sku1] = amount1
            categoryKey = ''
            if len(temDict) > 0:
                categoryKey = json.dumps(temDict)
            else:
                categoryKey = 'single'
                temDict['single'] = 0
            categoryDict[categoryKey] = temDict

            lv = pulp.LpVariable(order+sku, cat='Binary')
            lpVariableDict_order[order][categoryKey] = lv
            lpVariableDict_cate[categoryKey][order] = lv

    categoryDistinct = categoryDict.keys()
    dm = {}
    for i, cate in enumerate(categoryDistinct):
        dm[cate] = pulp.LpVariable(
            "M-{}".format(str(i)), cat='Binary')

    model += pulp.lpSum(
        [[v for v in val.values()] for val in lpVariableDict_order.values()]
    )

    logging.info("step2:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    for order in orderDistinct:
        model += pulp.lpSum([val for val in lpVariableDict_order[order].values()]) <= 1

    logging.info("step2.1:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
    for cate in categoryDistinct:
        model += pulp.lpSum([val for val in lpVariableDict_cate[cate].values()]
                            ) >= minBatchAmount-M*dm[cate]
        model += pulp.lpSum([val for val in lpVariableDict_cate[cate].values()]
                            ) <= 0+M*(1-dm[cate])

    logging.info("step3:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    model.solve()
    # model.solve(pulp.solvers.PULP_CBC_CMD(maxSeconds=30))
    # model.solve(pulp.PULP_CBC_CMD(msg=True,fracGap=0.1))
    # model.solve(pulp.GUROBI_CMD())

    result = {}
    result['lpstatus'] = pulp.LpStatus[model.status]
    covered = int(pulp.value(model.objective))
    result['covered'] = covered
    result['rate'] = '{:.1%}'.format(covered/len(orderDetail))
    items = []

    for i, cate in enumerate(lpVariableDict_cate.keys()):
        for order, var in lpVariableDict_cate[cate].items():
            if (var.varValue == 1):
                items.append({'order': order, 'category': cate, 'no': i})

    result['items'] = items
    logging.info("step4:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))
    logging.info("result: {}  {}  {}".format(
        result['lpstatus'], result['covered'], len(orderDetail)))

    return result


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    # order_amount=10000
    # sku=5000
    # orders={}
    # for od in range(order_amount):
    #     tem={}
    #     for _ in range(random.randint(2,5)):
    #         tem['sku{}'.format(random.randint(1,sku))]=random.randint(1,2)
    #     orders['order{}'.format(od)]=tem

    orders = {'o2': {'sku1': 1, 'sku3': 1, }, 'o3': {'sku1': 1, 'sku4': 1, }, 'o4': {'sku2': 1, 'sku3': 1, }, 'o5': {'sku3': 1, 'sku4': 1, }, 'o6': {
        'sku3': 1, 'sku5': 1, }, 'o7': {'sku5': 1, 'sku7': 1, }, 'o8': {'sku6': 1, 'sku7': 1, }, 'o9': {'sku4': 1, 'sku7': 1, }, 'o10': {'sku8': 1, 'sku3': 1, }}
    t1 = time.time()
    print(ob_lp(orders, 3))
    t2 = time.time()
    print('{:.0f}s'.format(t2-t1))

    # orders={'o2':{'sku1':1,'sku3':1,},'o3':{'sku1':1,'sku4':1,},'o4':{'sku2':1,'sku3':1,},'o5':{'sku3':1,'sku4':1,},'o6':{'sku3':1,'sku5':1,}
    #     ,'o7':{'sku5':1,'sku7':1,},'o8':{'sku6':1,'sku7':1,},'o9':{'sku4':1,'sku7':1,},'o10':{'sku8':1,'sku3':1,}}
    # r=requests.post('https://47.99.184.53:443/api-yy/algorithm/orderbatch'
    #     ,json={'batch':3,'app_id':1001,'token':'4NjUpZ9RJiaayYir','orderDetail':orders},verify=False)
    # print(r.json())
