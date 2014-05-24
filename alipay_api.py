# -*- coding: utf-8 -*-
'''
    支付宝接口公用函数
'''

import hashlib
import types
import urllib
import urllib2
import xml.etree.ElementTree as ET

from config import alipay_config

_GATEWAY = 'http://wappaygw.alipay.com/service/rest.htm?'

# 将字符串编码成utf-8格式
# https://github.com/fengli/alipay_python/blob/master/alipay/alipay.py
def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if not isinstance(s, basestring):
        try:
            return s
        except UnicodeEncodeError, e:
            if isinstance(s, Exception):
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s


# 除去数组中的空值和签名参数
# params 签名参数组
# return 去掉空值与签名参数后的新签名参数组
def params_filter(params):
    keys = params.keys()
    keys.sort()
    new_params = {}
    prestr = ''

    for k in keys:
        v = params[k]
        k = smart_str(k, alipay_config.input_charset)
        if k not in ('sign', 'sign_type') and v != '':
            new_params[k] = smart_str(v, alipay_config.input_charset)
            prestr += '%s=%s&' % (k, new_params[k])

    return new_params, prestr[:-1]

# 生成签名结果
def build_mysign(prestr, key, sign_type='MD5'):
    if sign_type == 'MD5':
        return hashlib.md5(prestr + key).hexdigest()
    return ''

def to_req_data(name, obj):
    arr = '<%s>' % name
    for k, v in obj.items():
        arr += '<%s>%s</%s>' % (smart_str(k, alipay_config.input_charset), smart_str(v, alipay_config.input_charset), smart_str(k, alipay_config.input_charset))
    arr += '</%s>' % name
    return arr

def create_req(service, partner):
    req = {}
    req['service'] = service
    req['format'] = 'xml'
    req['v'] = '2.0'
    req['partner'] = partner
    req['sec_id'] = 'MD5'
    req['req_data'] = {}
    return req

def parse_response(str_text):

    if 'res_data' not in str_text:
        return 'error'

    para_split = urllib.unquote(str_text.replace('+', ' ')).decode('utf-8').split('&')
    para_text = {}

    for item in para_split:
        index = item.find('=')
        para_text[item[:index]] = item[index+1:]

    xml = ET.fromstring(para_text['res_data'])
    para_text['request_token'] = xml.find('request_token').text

    return para_text

def parse_trade_status(str_text):
    xml = ET.fromstring(smart_str(str_text, alipay_config.input_charset))
    return xml.find('out_trade_no').text, xml.find('trade_status').text

def get_sign(obj, key=''):
    keys = obj.keys()
    keys.sort()

    prestr = ''

    for k in keys:
        if k == 'sign' or obj[k] == '':
            continue
        prestr += '%s=%s&' % (smart_str(k, alipay_config.input_charset), smart_str(obj[k], alipay_config.input_charset))
    prestr = prestr[:-1]

    return hashlib.md5(prestr + key).hexdigest()

def get_notify_sign(obj, key=''):
    src = '&'.join([k+'='+smart_str(obj[k], alipay_config.input_charset) for k in ['service', 'v', 'sec_id', 'notify_data']])
    return hashlib.md5(src + key).hexdigest()


def create_create_url(req):
    params = {}

    params['req_data'] = req.get('req_data', '')
    params['service'] = req.get('service', '')
    params['sec_id'] = req.get('sec_id', '')
    params['partner'] = req.get('partner', '')
    params['req_id'] = req.get('req_id', '')
    params['sign'] = req.get('sign', '')
    params['format'] = req.get('format', '')
    params['v'] = req.get('v', '')

    return _GATEWAY + urllib.urlencode(params)

def create_auth_url(req):
    params = {}

    params['req_data'] = req.get('req_data', '')
    params['service'] = req.get('service', '')
    params['sec_id'] = req.get('sec_id', '')
    params['partner'] = req.get('partner', '')
    params['sign'] = req.get('sign', '')
    params['format'] = req.get('format', '')
    params['v'] = req.get('v', '')

    return _GATEWAY + urllib.urlencode(params)


def send_create(req):
    url = create_create_url(req)
    response = urllib2.urlopen(url)
    return response.read()







