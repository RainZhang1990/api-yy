# coding=utf8
__author__ = 'zeewell'

import re
import time
import libs.citizen_id
from schema import Schema, And, Or


class ValidationError(ValueError):
    def __init__(self, message='', *args, **kwargs):
        ValueError.__init__(self, message, *args, **kwargs)

def required(value, var_name):
    if not value:
        raise ValidationError('{}不能为空'.format(var_name))

def integer(value, var_name, min_value=None, max_value=None):
    if not type(value) == int:
        raise ValidationError('{}应为int'.format(var_name, value))
    if min_value and value < min_value:
        raise ValidationError('{}应不小于{}'.format(var_name, min_value))
    if max_value and value > max_value:
        raise ValidationError('{}应不大于{}'.format(var_name, max_value))

def dict_str(value, var_name):
    try:
        Schema({str:str}).validate(value)
    except:
        raise ValidationError('{}应为Dict<string,string>类型'.format(var_name))


def length(value, var_name, min_length=None, max_length=None):
    l=len(value)
    if min_length and value < min_length:
        raise ValidationError('{}长度应不小于{}'.format(var_name, min_length))
    if max_length and value > max_length:
        raise ValidationError('{}长度应不大于{}'.format(var_name, max_length))

def password(value, var_name):
    try:
        Schema(str).validate(value)
    except:
        raise ValidationError('{}应为字符类型'.format(var_name))

    if not re.search(r'^(?=.*\d)(?=.*[a-zA-Z]).{6,12}$', value):
        raise ValidationError('{}密码格式错误, 要求6到12位数字与字母混合字符'.format(var_name))

def choices(value, choice_values, var_name):
    if value not in choice_values:
        raise ValidationError('{}参数取值异常'.format(var_name))

def email(value, var_name):
    if not re.match(r'^.+@[^.].*\.[a-z]{2,10}$', value, re.IGNORECASE):
        raise ValidationError('{}邮件格式错误'.format(var_name))

def citizen_id(value, var_name):
    citizen_valid, error_info = libs.citizen_id.check(value)
    if not citizen_valid:
        raise ValidationError('{}身份证格式错误'.format(var_name))

def order_for_grouping(value, var_name):
    try:
        Schema({str: {str: int}}).validate(value)
    except:
        message = '{}订单须为Dict<string,Dict<string,int>>类型'.format(var_name)
        raise ValidationError(message)

def order_for_relevance(value, var_name):
    try:
        Schema(And([[str]], lambda n: len(n) < 5000000)).validate(value)
    except:
        message = '{}集合须为List<List<string>>类型,且长度小于5000000'.format(var_name)
        raise ValidationError(message)
