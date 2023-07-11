from fastapi import FastAPI

from service.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI()

    app.include_router(router)
    return app
