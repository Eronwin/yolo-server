import logging
import asyncio
import os
from multiprocessing import Process
from typing import List

import uvicorn
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from backend.config.config import Config
from backend.logging import setup_logging
from backend.security import JWTManager
from backend.server.app import create_app
from backend.server.db import init_db, get_engine
from backend.utils.process import add_signal_handlers_in_loop

logger = logging.getLogger(__name__)


class Server:
    def __init__(self, config: Config, sub_process: List[Process] = None):
        if sub_process is None:
            sub_process = []
        self._config: Config = config
        self._sub_process = sub_process
        self._async_tasks = []

    @property
    def all_processes(self):
        return self._sub_process

    def _create_async_task(self, coro):
        self._async_tasks.append(asyncio.create_task(coro))

    @property
    def config(self) -> Config:
        return self._config

    async def start(self):
        logger.info("Starting server.")

        add_signal_handlers_in_loop()

        self._run_migrations()
        await self._prepare_data()

        port = 80
        # TODO ssl
        if self._config.port:
            port = self._config.port
        host = "0.0.0.0"
        if self._config.host:
            host = self._config.host

        jwt_manager = JWTManager(self._config.jwt_secret_key)

        # Start FastAPI server
        app = create_app(self._config)
        app.state.server_config = self._config
        app.state.jwt_manager = jwt_manager

        if self._config.enable_cors:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=self._config.allow_origins,
                allow_credentials=self._config.allow_credentials,
                allow_methods=self._config.allow_methods,
                allow_headers=self._config.allow_headers,
            )
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            access_log=False,
            log_level="error",
        )

        setup_logging()
        logger.info(f"Serving on {config.host}:{config.port}.")

        server = uvicorn.Server(config)
        self._create_async_task(server.serve())

        await asyncio.gather(*self._async_tasks)

    def _run_migrations(self):
        logger.info("Running database migrations.")
        pass

    async def _prepare_data(self):
        self._setup_data_dir(self._config.data_dir)

        await init_db(self._config.database_url)

        engine = get_engine()
        async with AsyncSession(engine) as session:
            await self._init_data(session)

        logger.debug("Data initialization completed.")

    @staticmethod
    def _setup_data_dir(data_dir: str):
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    async def _init_data(self, session: AsyncSession):
        init_data_funcs = [self._init_user]
        for init_data_func in init_data_funcs:
            await init_data_func(session)

    async def _init_user(self, session: AsyncSession):
        # TODO insert first user
        pass
