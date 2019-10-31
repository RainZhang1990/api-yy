import numpy
import pulp
import sys
import time
import logging
import utilities.collection as uc
from impala.dbapi import connect
from gurobipy import *

def getJoinKey(key1, key2):
    return str(key1)+"-"+str(key2)


def ob_lp(sale_dict, sku_per_bin,tolerate):
    sku_amount=len(sale_dict)
    bin_amount=sku_amount//sku_per_bin if sku_amount%sku_per_bin==0 else sku_amount//sku_per_bin+1 
    average=int(sum(sale_dict.values())/bin_amount)
    logging.info("step1:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    model = pulp.LpProblem("Bin Balance", pulp.LpMinimize)

    lpVariableDict = {}
    for sku in sale_dict.keys():
        for _bin in range(bin_amount):
            uc.update_dict2(lpVariableDict, sku, _bin, pulp.LpVariable(getJoinKey(
                        sku, _bin), cat='Binary'))

    x01 = []
    for i in range(bin_amount):
        x01.append((pulp.LpVariable("x0-{}".format(str(i)),lowBound=0,upBound=average*tolerate, cat='Continuous')
            ,pulp.LpVariable("x1-{}".format(str(i)),lowBound=0,upBound=average*tolerate, cat='Continuous')))

    model += pulp.lpSum(
        [val[0]+val[1] for val in x01]
    )

    logging.info("step2:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    for sku in sale_dict.keys():
        model += pulp.lpSum([val for val in lpVariableDict[sku].values()]) == 1
    for i in range(bin_amount):
        model += pulp.lpSum([uc.get_dict_value2(lpVariableDict, sku, i, 0) for sku in sale_dict.keys()])== sku_per_bin
        model += pulp.lpSum([sale_dict[sku]*uc.get_dict_value2(lpVariableDict, sku, i, 0) for sku in sale_dict.keys()])+x01[i][0]-x01[i][1]== average

    logging.info("step3:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    # model.solve()
    # model.solve(pulp.solvers.GUROBI(epgap = 0.9))
    model.solve(pulp.solvers.GUROBI_CMD(options=[('MIPGapAbs',average*0.01)]))
    # model.solve(pulp.solvers.PULP_CBC_CMD(msg=True,fracGap=0.01))
    # model.solve(pulp.solvers.PULP_CBC_CMD(maxSeconds=30))

    result = {}
    result['lpstatus'] = pulp.LpStatus[model.status]

    result['value'] = pulp.value(model.objective)
    result['average']=average
    bin_sale=[]
    for i in range(bin_amount):
        s=0
        count=0
        for sku in sale_dict.keys():
            if(lpVariableDict[sku][i].varValue == 1):
                s+=sale_dict[sku]
                count+=1
        bin_sale.append((s,count))
    result['bin_sale']=bin_sale

    
    items = []
    for key in lpVariableDict.keys():
        for key1 in lpVariableDict[key].keys():
            if(lpVariableDict[key][key1].varValue == 1):
                items.append({'sku': key,'bin':key1})
    result['items'] = items

    logging.info("step4:{}".format(time.strftime('%Y-%m-%d %H:%M:%S')))

    return result


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    host = '47.110.133.110'
    port = 3389
    argvs = sys.argv
    if len(argvs) > 1:
        host = '10.0.130.7'
        port = 4000
    conn = connect(host=host, port=port)
    # conn = connect(host='10.0.130.7', port=4000)
    cur = conn.cursor()
    # sqlOrderDetail = '''SELECT a.sku_id,a.num FROM tmp.yunqie_ordernum_by_sku_id a
    #                     INNER JOIN (SELECT DISTINCT sku_id FROM tmp.pick_order_model_input WHERE data_dt = '2019-05-07') b ON a.sku_id = b.sku_id
    #                     ORDER BY num DESC limit 490 '''

    sqlOrderDetail = '''SELECT b.sku_id,count(DISTINCT o_id) AS ordernum
                        FROM tmp.pick_sku20 a
                            RIGHT OUTER JOIN tmp.pick_sku_57 b ON a.sku_id = b.sku_id
                        WHERE b.sku_id != 'M1803'
                        GROUP BY b.sku_id
                        ORDER BY count(DISTINCT o_id) DESC limit 4900'''

    cur.execute(sqlOrderDetail)
    sales = cur.fetchall()
    sale_dict = {}
    for od in sales:
        sale_dict[od[0]]=od[1]

    

    result=ob_lp(sale_dict,35,0.1)
    labels(result)
    sql0 = "INSERT OVERWRITE tmp.bin_balance  VALUES"
    sql1 = ''
    for v in result['items']:
        sql1 += "('{}',{},{},'{}'),".format(v['sku'],v['bin'],sale_dict[v['sku']],time.strftime('%Y-%m-%d %H:%M:%S'))
    sql1 = sql1[:len(sql1)-1]
    
    # conn.close()
    # conn = connect(host, port)
    # cur = conn.cursor()
    cur.execute(sql0+sql1)