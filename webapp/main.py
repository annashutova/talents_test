from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webapp.infrastructure.middleware.logger import LogServerMiddleware
from webapp.infrastructure.middleware.metrics import MetricsMiddleware, metrics
from webapp.infrastructure.on_startup.logger import setup_logger
from webapp.api.auth.router import auth_router
from webapp.api.trait.router import trait_router
from webapp.api.test.router import test_router
from webapp.api.user.router import user_router
from webapp.api.invoice.router import invoice_router


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(LogServerMiddleware)
    app.add_middleware(MetricsMiddleware)

    # CORS Middleware should be the last.
    app.add_middleware(
        CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*']
    )


def setup_routers(app: FastAPI) -> None:
    app.add_route('/metrics', metrics)

    routers = [
        auth_router,
        user_router,
        trait_router,
        test_router,
        invoice_router,
    ]

    for router in routers:
        app.include_router(router)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logger()
    print('START APP')
    yield
    print('STOP APP')


def create_app() -> FastAPI:
    app = FastAPI(docs_url='/swagger', lifespan=lifespan)

    setup_middleware(app)
    setup_routers(app)

    return app
