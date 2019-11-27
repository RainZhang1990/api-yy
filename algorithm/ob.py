import numpy
import pulp
import time
import logging
import algorithm.utilities.collection as uc
# from impala.dbapi import connect

M = 99999


def getJoinKey(key1, key2):
    return str(key1)+"-"+str(key2)


def getCategoryJoinKey(skus: dict):
    s = ''
    l = list(skus.keys())
    l.sort()
    for sku in l:
        fmt = '{}_{}'.format(sku, skus[sku])
        if s == '':
            s = fmt
        else:
            s = getJoinKey(s, fmt)
    return s


def getOrder(orderDetail):
    orders = {}
    for od in orderDetail:
        orders[od['order']] = 1
    return orders.keys()


def ob_lp(orderDetail, minBatchAmount):
    """
    orderDetail:订单明细，以数组【字典】的方式传入.
    minBatchAmount：批次最小订单数量.
    """
    orderDistinct = getOrder(orderDetail)
    
    logging.info("step1:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    model = pulp.LpProblem("Order Grouping", pulp.LpMaximize)

    orderDict = {}
    lpVariableDict = {}
    for order in orderDetail:
        uc.update_dict2(orderDict, order['order'],
                    order['sku'], int(order['amount']))

    categoryDict = {}  # 订单内各sku数量-1 生成分类类别
    for order in orderDict.keys():
        for sku in orderDict[order].keys():
            temDict = {}
            n = orderDict[order][sku]-1
            if n > 0:
                temDict[sku] = n
            for sku1 in orderDict[order].keys():
                if not sku == sku1:
                    temDict[sku1] = orderDict[order][sku1]
            categoryKey = ''
            if len(temDict) > 0:
                categoryKey = getCategoryJoinKey(temDict)
            else:
                categoryKey = 'single'
                temDict['single'] = 0
            categoryDict[categoryKey] = temDict
            uc.update_dict2(lpVariableDict, order, categoryKey, pulp.LpVariable(getJoinKey(
                        order, categoryKey), cat='Binary'))

    dm = {}
    for cate in categoryDict.keys():
        dm[cate] = pulp.LpVariable(
            "M-{}".format(str(cate)), cat='Binary')

    model += pulp.lpSum(
        [[v for v in val.values()] for val in lpVariableDict.values()]
    )

    logging.info("step2:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    for row in orderDistinct:
        model += pulp.lpSum([val for val in lpVariableDict[row].values()]) <= 1
    for col in categoryDict.keys():
        model += pulp.lpSum(uc.get_dict_value2(lpVariableDict, row, col, 0)
                            for row in orderDistinct) >= minBatchAmount-M*dm[col]
        model += pulp.lpSum(uc.get_dict_value2(lpVariableDict, row, col, 0)
                            for row in orderDistinct) <= 0+M*(1-dm[col])

    logging.info("step3:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    model.solve()
    # model.solve(pulp.solvers.PULP_CBC_CMD(msg=True,threads=4))
    # model.solve(pulp.solvers.GUROBI())

    result = {}
    result['lpstatus'] = pulp.LpStatus[model.status]
    result['value'] = pulp.value(model.objective)
    items = []
    for key in lpVariableDict.keys():
        for key1 in lpVariableDict[key].keys():
            if(lpVariableDict[key][key1].varValue == 1):
                items.append({'order': key, 'category': categoryDict[key1]})

    result['items'] = items

    logging.info("step4:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    return result


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    conn = connect(host='47.110.133.110', port=3389)
    # conn = connect(host='10.0.130.7', port=4000)
    cur = conn.cursor()
    sqlOrderDetail = '''SELECT p.o_id,p.sku_id FROM tmp.tmp_order_item_20190401_10046913 p
            INNER JOIN
            (SELECT a.o_id,count(a.sku_id) AS _count
            FROM (
                    SELECT o_id,sku_id FROM tmp.tmp_order_item_20190401_10046913
                    WHERE io_date between '2019-04-01 07:45:00' AND '2019-04-01 08:00:00'
                    GROUP BY o_id,sku_id
                ) a
            GROUP BY a.o_id
            ) q ON p.o_id=q.o_id'''

    cur.execute(sqlOrderDetail)
    orderDetail = cur.fetchall()
    odList = []
    for od in orderDetail:
        odList.append({'order': od[0], 'sku': od[1], 'amount': 1})

    labels(ob_lp(odList, 2))
