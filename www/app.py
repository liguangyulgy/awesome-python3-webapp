import asyncio,os,json,time

import www.orm
from datetime import datetime
from aiohttp import web
import www.webFram as webFram
import logging;logging.basicConfig(level=logging.INFO)
from jinja2 import Environment,FileSystemLoader
from www.config import config

def index(request):
    return web.Response(content_type=r'text\html',body=b'<h1>Awesome</h1>')

def datetime_filter(t):
    delta = init(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


def init_jinja2(app,**kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape = kw.get('autoescape', True),
        block_start_string = kw.get('block_start_string', '{%'),
        block_end_string = kw.get('block_end_string', '%}'),
        variable_start_string = kw.get('variable_start_string','{{'),
        variable_end_string = kw.get('variable_end_string', '}}'),
        auto_reload = kw.get('auto_reload',True)
    )
    path = kw.get('path',None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters',None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env

async def init(loop):
    app = web.Application(loop=loop, middlewares=[webFram.logger_factory,webFram.response_factory])
    init_jinja2(app,filters = dict(datetime=datetime_filter))
    await www.orm.init(loop,**config['db'])
    webFram.add_routes(app,'www.handlers')
    # app.router.add_route('GET','/',index)
    webFram.add_static(app)
    srv = await loop.create_server(app.make_handler(),'127.0.0.1',9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()

