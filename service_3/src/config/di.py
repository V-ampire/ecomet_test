import asyncio

import aiohttp
from aiochclient import ChClient
from aiolimiter import AsyncLimiter
from handybits.di_container import DIContainer

from config.http import http_session_factory, ClickhouseClientSession
from config.settings import Settings
from github.data_layer import RepositoryDataLayer, AuthorCommitsDataLayer, RepositoryPositionDataLayer
from github.dlq import DLQInterface, JsonDLQ
from github.scrapper import GithubReposScrapper
from github.use_cases import DownloadGithubReposUseCase


def init_di_container() -> DIContainer:
    container = DIContainer()

    settings = Settings()
    ch_session = http_session_factory(ClickhouseClientSession, **settings.clickhouse_connection_config)

    # singletons
    container.register_instance(Settings, settings)
    container.register_instance(asyncio.Semaphore, asyncio.Semaphore(settings.MCR_LIMIT))
    container.register_singleton(aiohttp.ClientSession, lambda: http_session_factory(**settings.http_connection_config))
    container.register_instance(ClickhouseClientSession, ch_session)
    container.register_singleton(
        ChClient,
        lambda: ChClient(ch_session, **settings.clickhouse_params)
    )

    # not singleton because limiter can be token bound
    container.register(AsyncLimiter, lambda: AsyncLimiter(*settings.RPC_LIMIT))

    # data layers
    container.register(RepositoryDataLayer)
    container.register(AuthorCommitsDataLayer)
    container.register(RepositoryPositionDataLayer)

    container.register(GithubReposScrapper)
    container.register(DLQInterface, lambda: JsonDLQ(directory=settings.DLQ_DIRECTORY))

    # Use cases
    container.register(DownloadGithubReposUseCase)

    return container
