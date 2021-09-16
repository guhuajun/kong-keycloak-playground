import uuid
from datetime import datetime

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.routing import Route


async def index(request):
    return JSONResponse({
        'version': '0.0.2',
        'service': 'backend01'
    })


async def date(request):
    return JSONResponse({
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'signature': str(uuid.uuid4())
    })

routes = [
    Route('/', index),
    Route('/date', date)
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=[
               '*'], allow_methods=['*'], allow_headers=['*'])
]

app = Starlette(debug=True, routes=routes, middleware=middleware)


if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8081, log_level='info')
