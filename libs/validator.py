# coding=utf8
__author__ = 'zeewell'

import re
import time
import libs.citizen_id
from schema import Schema, And, Or


class ValidationError(ValueError):
    """
        Raised when a validator fails to validate its input.
    """

    def __init__(self, message='', *args, **kwargs):
        ValueError.__init__(self, message, *args, **kwargs)


def required(value, message=None):
    if not message:
        message = '值不能为空'
    
    if not value:
        raise ValidationError(message)

def integer(value, min_value=None, max_value=None, message=None):
    if not type(value)==int:
        raise ValidationError('值应为int')
    if min_value and value<min_value: 
        raise ValidationError('值应不小于{}'.format(min_value))
    if max_value and value>max_value: 
        raise ValidationError('值应不大于{}'.format(max_value))

def length(value, min_length=-1, max_length=-1, message=None):
    if not message:
        message = '请输入%d-%d位字符，一个汉字为两个字符' % (min_length, max_length)

    value = '{0}'.format(value)
    l = value and len(str.encode(value, 'GB18030')) or 0
    if l < min_length or max_length != -1 and l > max_length:
        raise ValidationError(message)

    return l


def password(value):
    try:
        Schema(str).validate(value)
    except:
        message = '参数类型异常'
        raise ValidationError(message)

    if not re.search(r'^(?=.*\d)(?=.*[a-zA-Z]).{6,12}$', value):
        message = '密码格式错误, 要求6到12位数字与字母混合字符'
        raise ValidationError(message)

    return True


def equal(value1, value2, message=None):
    if not message:
        message = '不一致'

    if value1 != value2:
        raise ValidationError(message)

    return True


def choices(value, choice_values=list(), message=None):
    if not message:
        message = '非法值'

    if value not in choice_values:
        raise ValidationError(message)

    return True


def email(value, message=None):
    if not message:
        message = '格式不正确'

    if not re.match(r'^.+@[^.].*\.[a-z]{2,10}$', value, re.IGNORECASE):
        raise ValidationError(message)

    return True


def mobile(value, message=None):
    try:
        message = '参数类型异常'
        Schema(str).validate(value)
    except:
        raise ValidationError(message)
    if not value:
        message = '请输入手机号'

    if not message:
        message = '手机号不正确'

    if not re.match(r'^1(([3578][0-9])|(4[57])|(70))\d{8}$', value, re.IGNORECASE):
        raise ValidationError(message)

    return True


def citizen_id(value, message=None):
    if not message:
        message = '请您输入正确的身份证信息'

    citizen_valid, error_info = libs.citizen_id.check(value)
    if not citizen_valid:
        raise ValidationError(error_info)

    return True


def smscode(value, message=None):
    try:
        message = '参数类型异常'
        Schema(str).validate(value)
    except:
        raise ValidationError(message)
    if not value:
        message = '请输入手机验证码'

    if not message:
        message = '手机验证码不正确'

    if not re.match(r'^\d{4}$', value):
        raise ValidationError(message)

    return True


def dob(value):
    try:
        Schema(str).validate(value)
    except:
        message = '参数类型异常'
        raise ValidationError(message)

    if not re.match(r'\d\d\d\d-[0-1][0-9]-[0-3][0-9]', value, re.IGNORECASE):
        message = '日期格式错误'
        raise ValidationError(message)

    return True


def dob_timezone(value):
    try:
        Schema(str).validate(value)
    except:
        message = '参数类型异常'
        raise ValidationError(message)

    if not re.match(r"\d\d\d\d-[0-1][0-9]-[0-3][0-9]T\d\d:\d\d:\d\d\.\d\d\d\+\d\d:\d\d", value, re.IGNORECASE):
        message = '日期格式错误'
        raise ValidationError(message)

    return True

def username(value, message=None):
    try:
        Schema(str).validate(value)
    except:
        message = '参数类型异常'
        raise ValidationError(message)

    if not message:
        message = '用户名只能由字母、数字和下划线组成。并且第一个字符只能是字母'

    if len(value) == 0:
        message = '用户名不可为空'
        raise ValidationError(message)

    if len(value) > 16:
        message = '用户名过长'
        raise ValidationError(message)

    # [\u4E00-\u9FA5] 匹配简体
    # [\u4E00-\u9FFF] 匹配简体和繁体
    # [\u2E80-\u9FFF] 匹配所有东亚区的语言
    #
    #
    # 2E80～33FFh：中日韩符号区。收容康熙字典部首、中日韩辅助部首、注音符号、日本假名、韩文音符，中日韩的符号、标点、带圈或带括符文数字、月份，以及日本的假名组合、单位、年号、月份、日期、时间等。
    # 3400～4DFFh：中日韩认同表意文字扩充A区，总计收容6,582个中日韩汉字。
    # 4E00～9FFFh：中日韩认同表意文字区，总计收容20,902个中日韩汉字。
    # A000～A4FFh：彝族文字区，收容中国南方彝族文字和字根。
    # AC00～D7FFh：韩文拼音组合字区，收容以韩文音符拼成的文字。
    # F900～FAFFh：中日韩兼容表意文字区，总计收容302个中日韩汉字。
    # FB00～FFFDh：文字表现形式区，收容组合拉丁文字、希伯来文、阿拉伯文、中日韩直式标点、小符号、半角符号、全角符号等。

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]{3,15}$', value, re.IGNORECASE):
        raise ValidationError(message)

    return True


def account_id(value):
    try:
        Schema(str).validate(value)
    except:
        message = '参数类型异常'
        raise ValidationError(message)

    if len(value) == 0:
        message = 'account_id 不能为空'
        raise ValidationError(message)

    if len(value) > 20:
        message = 'account_id 长度过长'
        raise ValidationError(message)


def year(value):
    try:
        Schema(int).validate(value)
    except:
        message = '参数类型异常'
        raise ValidationError(message)

    if 1900 > value or value > 9999:
        message = '年份异常'
        raise ValidationError(message)


def batch(value):
    try:
        Schema(And(int, lambda n: 0 < n < 9999)).validate(value)
    except:
        message = '批次数量异常: {}'.format(value)
        raise ValidationError(message)


def orderForGrouping(value):
    try:
        Schema({str: {str: int}}).validate(value)
    except:
        message = '订单须为Dict<string,Dict<string,int>>类型'
        raise ValidationError(message)

def relevance(value):
    try:
        Schema(And([[str]], lambda n: len(n) < 5000000)).validate(value)
    except:
        message = '集合须为List<List<string>>类型,且长度小于5000000'
        raise ValidationError(message)

def ir_category(value):
    category = ['sr', 'ic']
    if not value in category:
        raise ValidationError('category参数异常')

def image_length(value):
    if len(value) > 512:
        raise ValidationError('图像不得超过512张')