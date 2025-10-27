import asyncio
import datetime
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Final, ClassVar, Any, NamedTuple

from aiohttp import ClientSession, ClientError
from aiolimiter import AsyncLimiter

from config.http import retry_helper
from config.settings import Settings
from github.dto import Repository, github_to_repository_dtos_mapper, RepositoryAuthorCommitsNum, MapperError
from utils import str_exception


class CommitData(NamedTuple):
    author: str
    repository_owner: str
    repository_name: str


@dataclass
class GithubReposScrapper:
    settings: Settings
    semaphore: asyncio.Semaphore
    rate_limit: AsyncLimiter
    http_session: ClientSession
    logger: logging.Logger

    api_base_url: ClassVar[Final[str]] = "https://api.github.com"

    def _get_base_headers(self):
        return dict(Accept="application/vnd.github.v3+json", **self.settings.github_auth)

    @retry_helper
    async def _make_request(self, endpoint: str, method: str = "GET", params: dict[str, Any] | None = None) -> Any:
        async with self.semaphore:
            async with self.rate_limit:
                self.logger.debug(f"_make_request: {endpoint}, {params=}")
                async with self.http_session.request(
                    method,
                    f"{self.api_base_url}/{endpoint}",
                    params=params,
                    headers=self._get_base_headers()
                ) as response:
                    return await response.json()

    async def _get_top_repositories(self, limit: int = 100) -> list[Repository]:
        """GitHub REST API: https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#search-repositories"""
        data = await self._make_request(
            endpoint="search/repositories",
            params={"q": "stars:>1", "sort": "stars", "order": "desc", "per_page": limit},
        )
        return github_to_repository_dtos_mapper(data.get('items', []))

    async def _get_repository_commits(self, owner: str, repo: str, since: datetime.datetime) -> dict[CommitData, int]:
        """GitHub REST API: https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#list-commits"""
        commits = await self._make_request(
            endpoint=f"repos/{owner}/{repo}/commits",
            params={"since": since.strftime('%Y-%m-%dT%H:%M:%SZ')},
        )
        commits_count_map = defaultdict(int)
        for commit in commits:
            author = (commit.get('author', {}) or {}).get('login') # Cases with author=None
            if not author:
                raise MapperError(f"Fail to get commit author {commit.get('url')}")
            commit_data = CommitData(
                repository_name=repo,
                repository_owner=owner,
                author=author,
            )
            commits_count_map[commit_data] += 1
        return commits_count_map


    async def get_repositories(self) -> list[Repository]:
        try:
            top_repos_map = {(repo.owner, repo.name): repo for repo in await self._get_top_repositories()}
        except (MapperError, ClientError) as exc:
            self.logger.error(f"Fail to get top repositories, {str_exception(exc)}")
            return []
        self.logger.info(f"Requested top repost {len(top_repos_map.values())}")
        # Since for the last 24 hours
        since_date = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=1)
        commits_tasks = [self._get_repository_commits(repo.owner, repo.name, since_date) for repo in top_repos_map.values()]
        for commit_task in asyncio.as_completed(commits_tasks):
            try:
                commits = await commit_task
                if commits:
                    for commit_data, commits_num in commits.items():
                        if repo := top_repos_map.get((commit_data.repository_owner, commit_data.repository_name)):
                            repo.authors_commits_num_today.append(RepositoryAuthorCommitsNum(
                                author=commit_data.author,
                                commits_num=commits_num
                            ))
            except (MapperError, ClientError) as exc:
                # Log error, try to get next commits batch
                self.logger.exception(exc)
        return list(top_repos_map.values())