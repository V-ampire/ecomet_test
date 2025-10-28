import asyncio
import time

import aiohttp
import click

from config.di import init_di_container
from config.http import ClickhouseClientSession
from config.logger import get_logger
from github.use_cases import DownloadGithubReposUseCase


logger = get_logger(__name__)


async def _run():
    di_container = init_di_container()
    try:
        use_case: DownloadGithubReposUseCase = di_container.resolve(
            DownloadGithubReposUseCase,
        )
        downloaded, ch_data = await use_case.download()
        result_msg = (f"Downloaded: {len(downloaded)} repositories, "
               f"processed to clickhouse: {len(ch_data.repositories)} repositories, "
               f"{len(ch_data.repositories_authors_commits)} authors commits, "
               f"{len(ch_data.repositories_positions)} repositories positions.")
        logger.info(result_msg)
    except Exception as exc:
        logger.exception(exc)
    finally:
        await di_container.resolve(aiohttp.ClientSession).close()
        await di_container.resolve(ClickhouseClientSession).close()


@click.command(name='run')
def run():
    asyncio.run(_run())


@click.command(name='run_forever')
def run_forever():
    """Just run app e.g. to enter container using bash."""
    while True:
        logger.info('Empty start app')
        time.sleep(120)


@click.group()
def cli():
    """Initialize CLI."""


cli.add_command(run)
cli.add_command(run_forever)

if __name__ == '__main__':
    cli()
