from contextlib import asynccontextmanager
from dataclasses import dataclass

from handybits.datetime import utcnow

from config.logger import get_logger
from github.data_layer import RepositoryDataLayer, AuthorCommitsDataLayer, RepositoryPositionDataLayer, \
    ClickhouseDataLayer, InsertBatchError
from github.dlq import DLQInterface
from github.dto import Repository
from github.mappers import repositories_to_clickhouse_mapper, ClickhouseRepositoryData
from github.scrapper import GithubReposScrapper


logger = get_logger(__name__)


@asynccontextmanager
async def dlq_on_insert_fail(dlq: DLQInterface):
    try:
        yield
    except InsertBatchError as exc:
        logger.exception(exc)
        await dlq.enqueue(exc.batch_name, exc.batch_data)


@dataclass
class DownloadGithubReposUseCase:
    scrapper: GithubReposScrapper
    repository_data_layer: RepositoryDataLayer
    author_commits_data_layer: AuthorCommitsDataLayer
    repository_position_data_layer: RepositoryPositionDataLayer
    dlq: DLQInterface

    async def download(self) -> tuple[list[Repository], ClickhouseRepositoryData]:
        logger.info("Loading repositories")
        repositories = await self.scrapper.get_repositories()
        logger.info(f"Loaded {len(repositories)} repositories")
        updated = utcnow()
        save_to_clickhouse = repositories_to_clickhouse_mapper(repositories, date_at=updated)
        async with dlq_on_insert_fail(self.dlq):
            await self.repository_data_layer.insert(save_to_clickhouse.repositories)
        logger.info(f"Saved {len(save_to_clickhouse.repositories)} into {self.repository_data_layer.table_name}")
        async with dlq_on_insert_fail(self.dlq):
            await self.author_commits_data_layer.insert(
                save_to_clickhouse.repositories_authors_commits
            )
        logger.info(f"Saved {len(save_to_clickhouse.repositories_authors_commits)} into {self.author_commits_data_layer.table_name}")
        async with dlq_on_insert_fail(self.dlq):
            await self.repository_position_data_layer.insert(save_to_clickhouse.repositories_positions)
        logger.info(
            f"Saved {len(save_to_clickhouse.repositories_positions)} into {self.repository_position_data_layer.table_name}")
        return repositories, save_to_clickhouse
