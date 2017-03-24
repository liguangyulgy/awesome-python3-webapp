__author__ = 'LiGuangyu'
from www.webFram import get,post
import logging;logging.basicConfig(level=logging.INFO)
import www.orm as orm
from aiohttp import web

from www.models import User,Blog,Comment
import asyncio,hashlib,json
import time

COOKIE_NAME = "liguangyuCookie"
_COOKIE_KEY = "testyet"

def user2cookie(user,max_age):
    expires = str(int(time.time()) + max_age)
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id ,expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

async def cookie2user(cookie_str):
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires,sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8').hexdigest()):
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None






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
async def api_get_users(*, page=1, pageSize = 20):
    num = await User.findNumber()
    pageSize = int(pageSize)
    start = pageSize * (int(page) - 1)
    users = await User.findAll(start=start, step=pageSize, orderby=' created_at ')
    return {'users':users}

'''user register'''
@post('/api/users/register')
async def api_reqister_user(*,email,name,passwd):
    users = await User.findAll(cond={'email':email},step=1)
    if users:
        return ' User exists'

    user = User(name=name.strip(), email=email, passwd=passwd)
    await user.save()
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user,86400),max_age=86400,httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r

@get('/userRegister.html')
async def userRegisterPage(request):
    rev = {
        '__template__':'userRegister.html'
    }
    return rev

@post('/api/login')
async  def login(*,email,passwd):
    users = await User.findAll({'email':email},step=1)
    if len(users) == 0:
        raise Exception('Email not exist')
    user = users[0]

    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigst():
        raise Exception('Invalide passwd')
    r = web.Response()
    r.set_cookie(COOKIE_NAME,user2cookie(user,86400), max_age=86400,httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r


async def cookie_check(app, handler):
    async def check(request):
        request.__user__ = None
        cookie = request.cookies.get(COOKIE_NAME)
        if cookie:
            user = await cookie2user(cookie_str=cookie)
            if user:
                request.__user__ = user
        return await(handler(request))
    return check


@get('/createBlog.html')
def createBlogPage(request, id=None):
    '''demo create only'''
    rev={
        '__template__':'createBlog.html',
        'action':'/api/blogs/0'
    }
    if id:
        rev['id'] = id
    return rev

@post('/api/blogs/{id}')
async def createBlog(request, *, name, summary, content,id):
    #check_admin(request)
    if 0 == id:
        blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name = name.strip(),
                    summary=summary.strip(), content=content.strip())
        await blog.save()
    else :
        blog = await Blog.find(id)
        if blog:
            blog.update({
                'name':name,
                'summary':summary,
                'content':content
            });
            await blog.save();
        else :
            return Exception('No blog found')
    return blog



@get('/api/blogs/{id}')
async def showBlogs(request,id):
    return None

