from typing import Annotated

import asyncpg
from fastapi import Depends, Request


async def get_pg_connection(
    request: Request
) -> asyncpg.Connection:
    async with request.app.state.db_pool.acquire() as connection:
        yield connection


pg_conn_dep = Annotated[asyncpg.Connection, Depends(get_pg_connection)]