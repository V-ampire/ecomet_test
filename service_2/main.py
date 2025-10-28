import asyncio

from aiolimiter import AsyncLimiter

from config.http import http_session_factory
from config.logger import get_logger
from config.settings import Settings
from github.scrapper import GithubReposScrapper


logger = get_logger(__name__)


async def main():
    settings = Settings()
    semaphore = asyncio.Semaphore(settings.MCR_LIMIT)
    rate_limit = AsyncLimiter(*settings.RPC_LIMIT)
    async with http_session_factory() as http_session:
        try:
            scrapper = GithubReposScrapper(
                http_session=http_session,
                settings=settings,
                semaphore=semaphore,
                rate_limit=rate_limit,
            )
            repositories = await scrapper.get_repositories()
            # ToDo do smth with repos
            total_repos = len(repositories)
            total_commits = sum(commits.commits_num for repo in repositories for commits in repo.authors_commits_num_today)
            print(f"{total_repos=}, {total_commits=}")
        except Exception as exc:
            logger.exception(exc)



if __name__ == '__main__':
    asyncio.run(main())
