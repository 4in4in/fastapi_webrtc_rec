import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response

from app.routers.webrtc import webrtc_router
from app.settings import settings

logging.basicConfig(level=logging.DEBUG if settings.is_debug else logging.INFO)

app = FastAPI()

app.include_router(webrtc_router)

if settings.is_debug:

    @app.get("/")
    def index_route():
        with open("./app/static/index.html") as file:
            return HTMLResponse(content=file.read())

    @app.get("/client.js")
    def client_route():
        with open("./app/static/client.js") as file:
            return Response(content=file.read(), media_type="application/javascript")
