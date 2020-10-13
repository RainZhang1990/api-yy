import numpy
import pulp
import time
import logging
import random
import json
import requests
# from gurobipy import *

M = 99999


def get_join_key(key1, key2):
    return str(key1)+"-"+str(key2)


def get_category_join_key(skus: dict):
    s = ''
    for key, val in skus.items():
        fmt = '{}_{}'.format(key, val)
        if s == '':
            s = fmt
        else:
            s = get_join_key(s, fmt)
    return s


class Vividict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


def ob_an(order_src: dict, min_batch_amount):
    """
    order_src:订单明细，以 dictionary<string,dictionary<string,int>> 的方式传入.
    min_batch_amount:最小批次数量
    """
    logging.info('step1:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
    order_distinct = order_src.keys()
    model = pulp.LpProblem("OrderGrouping", pulp.LpMaximize)

    vd_order = Vividict()
    vd_cate = Vividict()

    category_dict = {}  # 订单内各sku数量-1 生成分类类别
    for order, detail in order_src.items():
        for sku, amount in detail.items():
            tmp_dict = {}
            n = amount-1
            if n > 0:
                tmp_dict[sku] = n
            for sku1, amount1 in detail.items():
                if not sku == sku1:
                    tmp_dict[sku1] = amount1
            category_key = ''
            if len(tmp_dict) > 0:
                category_key = json.dumps(tmp_dict)
            else:
                category_key = 'single'
                tmp_dict['single'] = 0
            category_dict[category_key] = tmp_dict

            lv = pulp.LpVariable(order+sku, cat='Binary')
            vd_order[order][category_key] = lv
            vd_cate[category_key][order] = lv

    category_distinct = category_dict.keys()
    dm = {}
    for i, cate in enumerate(category_distinct):
        dm[cate] = pulp.LpVariable(
            "M-{}".format(str(i)), cat='Binary')

    model += pulp.lpSum(
        [[v for v in val.values()] for val in vd_order.values()]
    )

    logging.info('step2:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))

    for order in order_distinct:
        model += pulp.lpSum([val for val in vd_order[order].values()]) <= 1

    logging.info('step3:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))

    for cate in category_distinct:
        model += pulp.lpSum([val for val in vd_cate[cate].values()]
                            ) >= min_batch_amount-M*dm[cate]
        model += pulp.lpSum([val for val in vd_cate[cate].values()]
                            ) <= 0+M*(1-dm[cate])

    logging.info('step4:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))

    model.solve()
    # model.solve(pulp.solvers.PULP_CBC_CMD(maxSeconds=30))
    # model.solve(pulp.PULP_CBC_CMD(msg=True,fracGap=0.1))
    # model.solve(pulp.GUROBI_CMD())

    result = {}
    result['lpstatus'] = pulp.LpStatus[model.status]
    covered = int(pulp.value(model.objective))
    result['covered'] = covered
    result['rate'] = '{:.1%}'.format(covered/len(order_src))
    
    items = []
    for i, cate in enumerate(vd_cate.keys()):
        for order, var in vd_cate[cate].items():
            if (var.varValue == 1):
                items.append({'order': order, 'category': cate, 'no': i})
    result['items'] = items
    
    logging.info('step5:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
    logging.info("lpstatus: {} covered: {} rate: {} total: {}".format(
        result['lpstatus'], result['covered'], result['rate'], len(order_src)))

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
