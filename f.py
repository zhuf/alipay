# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for

import datetime

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
conn = MongoClient(host='localhost', port=5430)
db = conn.test

from alipay_api import *
from config import alipay_config

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    orders = [i for i in db.alipay.orders.find()]

    if request.method == 'POST':
        form = request.form
        name = form['name']
        money = form['money']
        remark = form.get('remark', '')
        created = str(datetime.date.today())
        status = 'no'

        d = {'name': name, 'money': money, 'remark': remark, 'created': created, 'status': status}

        id = db.alipay.orders.save(d)

        req = create_req('alipay.wap.trade.create.direct', alipay_config.partner)
        req['req_id'] = str(id)
        req['req_data'] = {
            'subject': '捐款',
            'out_trade_no': str(id),
            'total_fee': money,
            'seller_account_name': 'zhufeng9282@163.com',
            'call_back_url': 'http://127.0.0.1:5000/notify',
            'notify_url': 'http://127.0.0.1:5000/notify',
            'out_user': '朱峰',
            'merchant_url': 'http://127.0.0.1:5000/',
            'pay_expire': 10
        }
        req['req_data'] = to_req_data('direct_trade_create_req', req['req_data'])
        req['sign'] = get_sign(req, alipay_config.key)

        response = parse_response(send_create(req))

        if response != 'error':
            token = response.get('request_token')

            req = create_req('alipay.wap.auth.authAndExecute', alipay_config.partner)
            req['req_data'] = to_req_data('auth_and_execute_req', {'request_token': token})
            req['sign'] = get_sign(req, alipay_config.key)

            url = create_auth_url(req)
            print url
            return redirect(url)

        return redirect('/')

    return render_template('index.html', orders=orders)

@app.route('/notify', methods=['GET', 'POST'])
def notify():

    if request.method == 'GET':
        sign = request.args.get('sign', '')     # 签名
        result = request.args.get('result', '')     # 支付结果  result=success
        out_trade_no = request.args.get('out_trade_no', '')     # 商户网站唯一订单号
        trade_no = request.args.get('trade_no', '')     # 支付宝交易号
        request_token = request.args.get('request_token', '')   # 授权令牌

        d = {'sign': sign, 'result': result, 'out_trade_no': out_trade_no, 'trade_no': trade_no, 'request_token': request_token}

        if result == 'success':
            db.alipay.sync_notify.insert(d)
            db.alipay.orders.update({'_id': ObjectId(out_trade_no)}, {'$set': {'status': 'yes'}})
            return redirect('/order/'+out_trade_no)
        else:
            return 'error'
    elif request.method == 'POST':
        service = request.form.get('service', '')       # 接口名称
        v = request.form.get('v', '')       # 接口版本号
        sec_id = request.form.get('sec_id', '')     # 签名方式
        sign = request.form.get('sign', '')     # 签名
        notify_data = request.form.get('notify_data', '')       # 通知业务参数

        d = {}
        d['service'] = service
        d['v'] = v
        d['sec_id'] = sec_id
        d['sign'] = sign
        d['notify_data'] = notify_data

        out_trade_no, trade_status = parse_trade_status(notify_data)

        if (trade_status == 'TRADE_FINISHED' or trade_status == 'TRADE_SUCCESS') and (sign == get_notify_sign(d, alipay_config.key)):

            if sign == get_notify_sign(d, alipay_config.key):
                db.alipay.aync_notify.insert(d)
                db.alipay.orders.update({'_id': ObjectId(out_trade_no)}, {'$set': {'status': 'yes'}})
                return 'success'
            else:
                return 'bad sign'
        else:
            return 'unknow trade status'


@app.route('/order/<id>')
def order(id):
    order = db.alipay.orders.find_one({'_id': ObjectId(id)})
    return render_template('order.html', order=order)



if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)








