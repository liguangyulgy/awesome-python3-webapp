__author__ = 'LiGuangyu'
from www.webFram import get,post
import logging;logging.basicConfig(level=logging.INFO)
import www.orm as orm
from www.models import User,Blog,Comment
import asyncio

@get('/hello/world/{name}')
async def test(name):
    logging.info('called')
    return 'hello world %s' % name

@get('/')
async  def index(request):
    users = await User.findAll()
    return {
        '__template__':'test.html',
        'users':users
    }