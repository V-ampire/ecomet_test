from dataclasses import dataclass, field
from typing import Any, NamedTuple

from utils import str_exception


@dataclass
class RepositoryAuthorCommitsNum:
    author: str
    commits_num: int


@dataclass
class Repository:
    name: str
    owner: str
    position: int
    stars: int
    watchers: int
    forks: int
    language: str
    authors_commits_num_today: list[RepositoryAuthorCommitsNum] = field(default_factory=list)


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
