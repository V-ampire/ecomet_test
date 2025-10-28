from typing import Type

import aiohttp
from aiohttp import ClientError
from tenacity import stop_after_attempt, wait_exponential, retry, retry_if_exception_type

retry_helper = retry(
    retry=retry_if_exception_type(ClientError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=3),
    reraise=True
)


def http_session_factory(
    session_cls: Type[aiohttp.ClientSession] = aiohttp.ClientSession,
    **connector_options
) -> aiohttp.ClientSession:
    # ToDo Setup poll settings if need
    return session_cls(
        connector=aiohttp.TCPConnector(**connector_options)
    )

class ClickhouseClientSession(aiohttp.ClientSession):
    """Class to split dependencies"""

