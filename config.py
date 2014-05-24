# -*- coding: utf-8 -*-

class alipay_config:

    # 合作身份者ID, 以2088开头由16位纯数字组成的字符串
    partner = ''

    # 交易安全校验码, 由数字和字母组成的32位字符串
    # 如果签名方式设置为"MD5"时, 请设置该参数
    key = ''

    # 商户的私钥
    # 如果签名方式设置为"0001", 请设置该参数
    private_key = ''

    # 支付宝的公钥
    # 如果签名方式设置为"0001", 请设置该参数
    ali_public_key = ''

    # 调式用, 创建TXT日志文件夹路径
    log_path = '~/'

    # 字符编码格式 目前支持 utf-8
    input_charset = 'utf-8'

    # 签名方式, 选择项: 0001(RSA), MD5
    sign_type = 'MD5'
