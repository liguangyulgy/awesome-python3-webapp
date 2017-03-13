# __author__ = 'LiGuangyu'
# from www.webFram import get,post
# import logging;logging.basicConfig(level=logging.INFO)
# import www.orm as orm
# from aiohttp import web
#
# from www.models import User,Blog,Comment
# import asyncio
# import time
#
# @get('/hello/world/{name}')
# async def test(name):
#     logging.info('called')
#     return 'hello world %s' % name
#
# @get('/')
# def index(request):
#     summary = "The summary of the Project. liguangyu's Demo"
#     blogs = [
#         Blog (id = 1, name = 'Test Blog', summary= summary, created_at = time.time() - 120),
#         Blog (id = 2, name = 'Something New', summary = summary, created_at = time.time() - 3600),
#         Blog (id = 3, name = 'Learn Swift', summary=summary, created_at = time.time() - 72000)
#     ]
#     return {
#         '__template__':'blogs.html',
#         'blogs':blogs
#     }
#
# @get('/api/users')
# async def api_get_users(*, page=1, pageSize = 20):
#     num = await User.findNumber()
#     pageSize = int(pageSize)
#     start = pageSize * (int(page) - 1)
#     users = await User.findAll(start=start, step=pageSize, orderby=' created_at ')
#     return {'users':users}
#
# @get('/redict/wxx')
# def api_redict_test(request):
#     logging.info(request)
#     return  web.Response(status=301,headers={'Location':'https://wx.tenpay.com/f2f?t=AQAAABbYA7QM%2Bvt5%2B8NjyyGKBzc%3D'})
#
# @get('/redict/ali')
# def api_redict_ali(request):
#     logging.info(request)
#     return  web.Response(status=301,headers={'Location':'https://QR.ALIPAY.COM/FKX01923JGUEDEXZFHKI65'})
#
# @get('/redict/unionpay')
# def api_redict_unionpay(request):
#     logging.info(request)
#     return web.Response(status=301, headers={'Location':'https://qr.95516.com/00010000/62275911101538427893'})
#
# @get('/show/qrPage')
# def showQrPage(request):
#     str = 'http://192.168.0.193:9000/redict/unionpay'
#     return {
#         '__template__': 'qrDemo.html',
#         'qrStr': str
#     }