__author__ = 'LiGuangyu'
from www.webFram import get,post
import logging;logging.basicConfig(level=logging.INFO)
import www.orm as orm
from www.models import User,Blog,Comment
import asyncio
import time

@get('/hello/world/{name}')
async def test(name):
    logging.info('called')
    return 'hello world %s' % name

@get('/')
def index(request):
    summary = "The summary of the Project. liguangyu's Demo"
    blogs = [
        Blog (id = 1, name = 'Test Blog', summary= summary, created_at = time.time() - 120),
        Blog (id = 2, name = 'Something New', summary = summary, created_at = time.time() - 3600),
        Blog (id = 3, name = 'Learn Swift', summary=summary, created_at = time.time() - 72000)
    ]
    return {
        '__template__':'blogs.html',
        'blogs':blogs
    }

@get('/api/users')
async def api_get_users(*, page='1', pageSize = '20'):
    num = await User.findNumber()
    users = await User.findAll()
