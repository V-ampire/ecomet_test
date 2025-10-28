from abc import ABC, abstractmethod


class TableInterface(ABC):
    table_name = None

    @classmethod
    @abstractmethod
    def get_insert_sql(cls, **options) -> str:
        """Return sql to insert data."""
        raise NotImplementedError


class RepositoryTable(TableInterface):
    table_name = 'test.repositories'

    @classmethod
    def get_insert_sql(cls) -> str:
        return f"""INSERT INTO {cls.table_name}
            (name, owner, stars, watchers, forks, language, updated)
            VALUES
        """


class AuthorCommitsTable(TableInterface):
    table_name = 'test.repositories_authors_commits'

    @classmethod
    def get_insert_sql(cls) -> str:
        return f"""INSERT INTO {cls.table_name}
            (date, repo, author, commits_num)
            VALUES
        """


class RepositoryPositionsTable(TableInterface):
    table_name = 'test.repositories_positions'

    @classmethod
    def get_insert_sql(cls) -> str:
        return f"""INSERT INTO {cls.table_name}
            (date, repo, position)
            VALUES
        """