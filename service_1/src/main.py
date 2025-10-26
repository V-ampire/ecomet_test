import uvicorn

from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI, APIRouter
from starlette.types import Lifespan

from settings import Settings
from depends import pg_conn_dep


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = Settings()
    app.state.settings = settings
    async with asyncpg.create_pool(**settings.pg_config) as db_pool:
        app.state.db_pool = db_pool
        yield


async def get_db_version(conn: pg_conn_dep):
    return await conn.fetchval("SELECT version()")


def register_routes(app: FastAPI):
    router = APIRouter(prefix="/api")
    router.add_api_route(path="/db_version", endpoint=get_db_version)
    app.include_router(router)


def create_app(app_lifespan: Lifespan = lifespan) -> FastAPI:
    app = FastAPI(title="e-Comet", lifespan=app_lifespan)
    register_routes(app)
    return app


if __name__ == "__main__":
    server_config = dict(
        port=8000,
        host='0.0.0.0',
        lifespan='on',
        factory=True
    )
    uvicorn.run("main:create_app", **server_config)
