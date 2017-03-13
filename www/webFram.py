__author__ = 'LiGuangyu'

import logging;logging.basicConfig(level=logging.INFO)
import asyncio,functools,inspect,os
from aiohttp import web
from urllib import parse
import json

def get(path):
    '''
    decorator @get('/path')
    :param path:
    :return:
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator

def post(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator

class RequestHandler(object):
    def __init__(self, app, fn):
        self._app = app
        self._func = fn

    async def __call__(self, request):
        sigArgs = inspect.signature(self._func).parameters
        kw ={}
        qs = request.query_string
        if qs:
            kw.update({ x:(y[0] if len(y) == 1 else y) for x,y in parse.parse_qs(qs,True).items()})
        urlArgs = request.match_info or {}
        kw.update(dict(**urlArgs))
        contentType = request.content_type.lower() if request.has_body else ''
        if contentType.startswith('application/json'):
            body = await request.json()
        elif contentType.startswith('application/x-www-form') or contentType.startswith('multipart/form-data'):
            body = await request.post()
        else:
            body = {}
        kw.update(dict(**body))
        kw.update({'body':body,'request':request})
        try:
            args = {x:kw[x] for x in sigArgs if x in kw}
        except ValueError as e :
            return web.HTTPBadRequest(e)
        for x in sigArgs:
            if x not in args and '=' not in str(sigArgs[x]):
                message = 'Missing args %s' % x
                resp = web.HTTPBadRequest(body= message.encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        r = await self._func(**args)
        return r

def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'static')
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' %( '/static', path))

def add_route(app,fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine (fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ','.join(inspect.signature(fn).parameters.keys())))
    hr = RequestHandler(app,fn)
    app.router.add_route(method, path, hr)

def add_routes(app, module_name):
    n = module_name.rfind('.')
    if n == (-1):
        mod = __import__(module_name,globals(),locals())
    else:
        name = module_name[n+1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(),[name]),name)
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn = getattr(mod,attr)
        if callable(fn)  :
            method = getattr(fn,'__method__',None)
            path = getattr(fn, '__method__', None)
            if method and path:
                add_route(app,fn)

async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request:%s %s' % (request.method,request.path))
        return (await handler(request))
    return logger

async def response_factory(app, handler):
    async def response(request):
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r,str):
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r,dict):
            template = r.get('__template__')
            if template:
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
            else:
                resp = web.Response(body=json.dumps(r).encode('utf-8'))
                resp.content_type = 'application/json'
            return resp
    return response



