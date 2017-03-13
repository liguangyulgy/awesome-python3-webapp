__author__ = 'LiGuangyu'

from www.webFram import get,post
from aiohttp import web
import logging;logging.basicConfig(level=logging.INFO)

from www.models import User,Blog,Comment

@get('/redict/wxx')
def api_redict_test(request):
    logging.info(request)
    return  web.Response(status=301,headers={'Location':'https://wx.tenpay.com/f2f?t=AQAAABbYA7QM%2Bvt5%2B8NjyyGKBzc%3D'})

@get('/redict/ali')
def api_redict_ali(request):
    logging.info(request)
    return  web.Response(status=301,headers={'Location':'https://QR.ALIPAY.COM/FKX01923JGUEDEXZFHKI65'})

@get('/redict/unionpay')
def api_redict_unionpay(request):
    logging.info(request)
    return web.Response(status=301, headers={'Location':'https://qr.95516.com/00010000/62275911101538427893'})

@get('/show/qrPage')
def showQrPage(request):
    str = 'http://192.168.0.193:9000/redict/unionpay'
    return {
        '__template__': 'qrDemo.html',
        'qrStr': str
    }