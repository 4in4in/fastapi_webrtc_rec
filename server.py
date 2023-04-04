import logging

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response

from app.routers.webrtc import webrtc_router
from app.settings import settings

app = FastAPI()

if settings.is_debug:
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # settings.BACKEND_CORS_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    logging.basicConfig(level=logging.INFO)

    @app.get("/")
    def index_route():
        with open("./app/static/index2.html") as file:
            return HTMLResponse(content=file.read())

    @app.get("/client.js")
    def client_route():
        with open("./app/static/client2.js") as file:
            return Response(content=file.read(), media_type="application/javascript")


app.include_router(webrtc_router)
