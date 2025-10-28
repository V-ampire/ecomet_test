import datetime
from typing import Any, NamedTuple

from handybits.exceptions import str_exception

from github.dto import Repository

class MapperError(Exception):
    """Error in mapping process."""


def github_to_repository_dtos_mapper(github_items: list[dict[str, Any]], start_position: int = 0) -> list[Repository]:
    try:
        return [
            Repository(
                name=dict_data['name'],
                owner=dict_data['owner']['login'],
                position=start_position + position,
                stars=dict_data['stargazers_count'],
                watchers=dict_data['watchers'],
                forks=dict_data['forks_count'],
                language=dict_data['language'],
            )
            for position, dict_data in enumerate(github_items, 1)
        ]
    except KeyError as exc:
        raise MapperError(f"Error to map repository from github {str_exception(exc)}")


class ClickhouseRepositoryData(NamedTuple):
    repositories: list
    repositories_authors_commits: list
    repositories_positions: list


def repositories_to_clickhouse_mapper(repositories: list[Repository], date_at: datetime.datetime) -> ClickhouseRepositoryData:
    ch_repositories = []
    repositories_authors_commits = []
    repositories_positions = []
    for repository in repositories:
        ch_repositories.append((
            repository.name,
            repository.owner,
            int(repository.stars),
            int(repository.watchers),
            int(repository.forks),
            repository.language,
            date_at.strftime('%Y-%m-%d %H:%M:%S')
        ))
        repositories_authors_commits.extend([
            (date_at.date(), repository.name, commit.author, commit.commits_num) for commit in repository.authors_commits_num_today
        ])
        repositories_positions.append((date_at.date(), repository.name, repository.position))

    return ClickhouseRepositoryData(
        repositories=ch_repositories,
        repositories_authors_commits=repositories_authors_commits,
        repositories_positions=repositories_positions
    )
