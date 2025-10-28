import aiohttp
from aiohttp import ClientError
from tenacity import stop_after_attempt, wait_exponential, retry, retry_if_exception_type

retry_params = dict(
    retry=retry_if_exception_type(ClientError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=3),
)


retry_helper = retry(
        retry=retry_if_exception_type(ClientError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=3),
        reraise=True
    )


def http_session_factory() -> aiohttp.ClientSession:
    # ToDo Setup poll settings if need
    return aiohttp.ClientSession()
