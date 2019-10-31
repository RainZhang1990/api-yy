__author__ = 'zeewell'

import time, random

ARR = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
LAST = ('1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2')

AREA = {"11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古", "21": "辽宁", "22": "吉林", "23": "黑龙江", "31": "上海", "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东", "41": "河南", "42": "湖北",
        "43": "湖南", "44": "广东", "45": "广西", "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53": "云南", "54": "西藏", "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆", "71": "台湾", "81": "香港", "82": "澳门",
        "91": "国外"}


def check(citizen_id):
    '''
    验证身份证号码有效性
    @param citizen_id: citizen id number
    @return:
    '''
    # check length
    id_len = len(citizen_id)
    if id_len not in [15, 18]:
        return False, '身份证号码位数不正确'

    # check area
    if citizen_id[0:2] not in AREA:
        return False, '身份证地区不正确'

    # check birthday
    try:
        if id_len == 18:
            x2 = citizen_id[6:14]
            x3 = time.strptime(x2, '%Y%m%d')
            if x2 < '19000101' or x3 > time.localtime():
                return False, '时间错误，出生日期不合法'
        else:
            x2 = time.strptime(citizen_id[6:12], '%y%m%d')
    except:
        return False, '时间错误，出生日期不合法'

    if id_len == 18:
        y = 0
        for i in range(17):
            y += int(citizen_id[i]) * ARR[i]

        if LAST[y % 11] != citizen_id[-1].upper():
            return False, '身份证验证码错误'

    return True, '身份证验证通过'


def generator():
    '''
    生成随机身份证号码
    @return:
    '''
    t = time.localtime()[0]
    province = random.choice(list(AREA.keys()))
    id_number = '{0}{1}{2}{3}{4}{5}{6}'.format(province,
                                                random.randint(10, 99),
                                                random.randint(10, 99),
                                                random.randint(t - 80, t - 18),
                                                random.randint(1, 12),
                                                random.randint(1, 28),
                                                random.randint(1, 999))
    y = 0
    for i in range(17):
        y += int(id_number[i]) * ARR[i]
    return '{0}{2}'.format(id_number, LAST[y % 11])


def citizen_15_to_18(citizen_15):
    '''
    15位身份证号码转换为18位身份证号码
    @param citizen_15:
    @return:
    '''
    if len(citizen_15) == 15:
        return False, '身份证号码输入错误，身份证号码长度要求15位'

    checked, error = check(citizen_15)
    if not checked:
        return error

    new_id_number = '{0}19{1}'.format(citizen_15[:6], citizen_15[6:])
    y = 0
    for i in range(17):
        y += int(new_id_number[i]) * ARR[i]

    return '{0}{2}'.format(new_id_number, LAST[y % 11])


def extract_dob_gender(citizen_id):
    '''
    extract dob and gender from citizen id number
    @param citizen_id:
    @return: dob, gender
    '''
    dob = None
    gender = None
    if len(citizen_id) == 15:
        dob = '19{0}'.format(citizen_id[6:12])
        gender = citizen_id[-1:]
    else:
        dob = citizen_id[6:14]
        gender = citizen_id[-2:-1]

    gender = int(gender) & 1 and 'm' or 'f'
    return dob, gender
