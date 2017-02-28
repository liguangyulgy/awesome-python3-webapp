import asyncio,os,json,time
from datetime import datetime
from aiohttp import web
import logging;logging.basicConfig(level=logging.INFO)

def index(request):
    return web.Response(content_type=r'text\html',body=b'<h1>Awesome</h1>')

async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET','/',index)
    srv = await loop.create_server(app.make_handler(),'127.0.0.1',9000)
    logging.info('server started at http://127.0.0.1:9000...')

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()

