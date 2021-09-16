import uvicorn

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.endpoints import HTTPEndpoint
from starlette import status
from starlette.routing import Route


def version(request):
    return JSONResponse({'version': '0.0.1'}, status_code=status.HTTP_200_OK)


class ShopLocation(HTTPEndpoint):
    async def get(self, request):
        locations = [
            {'name': 'shanghai'}
        ]
        return JSONResponse(locations, status_code=status.HTTP_200_OK)


routes = [
    Route('/', version),
    Route('/location', ShopLocation, methods=['GET']),
]

app = Starlette(debug=True, routes=routes)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
