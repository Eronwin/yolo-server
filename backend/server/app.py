from contextlib import asynccontextmanager
import aiohttp
from fastapi import FastAPI

from backend.api import middlewares, exceptions
from backend.config import Config
from backend.config.envs import TCP_CONNECTOR_LIMIT
from backend.routes.routes import api_router


def create_app(cfg: Config) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        connector = aiohttp.TCPConnector(
            limit=TCP_CONNECTOR_LIMIT,
        )
        app.state.http_client = aiohttp.ClientSession(connector=connector)
        yield
        await app.state.http_client.close()

    app = FastAPI(
        lifespan=lifespan,
        response_model_exclude_unset=True,
        docs_url=None if (cfg and cfg.disable_openapi_docs) else "/docs",
        redoc_url=None if (cfg and cfg.disable_openapi_docs) else "/redoc",
        openapi_url=None if (cfg and cfg.disable_openapi_docs) else "/openapi.json",
    )
    app.add_middleware(middlewares.RequestTimeMiddleware)
    app.include_router(api_router)
    exceptions.register_handlers(app)
    return app
