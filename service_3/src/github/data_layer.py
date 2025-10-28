import logging
from dataclasses import dataclass
from typing import ClassVar

from aiochclient import ChClient
from handybits.iterated import chunks

from github.tables import RepositoryTable, TableInterface, AuthorCommitsTable, RepositoryPositionsTable

class InsertBatchError(Exception):
    def __init__(self, message, batch_name, batch_data):
        self.batch_name = batch_name
        self.batch_data = batch_data
        super().__init__(message)


@dataclass
class ClickhouseDataLayer:
    table: ClassVar[TableInterface]

    clickhouse: ChClient

    @property
    def table_name(self):
        return self.table.table_name

    async def insert(
        self,
        rows: list[tuple],
        batch_size: int = 1000
    ):
        responses = []
        for idx, batch in enumerate(chunks(rows, batch_size)):
            sql = self.table.get_insert_sql()
            try:
                resp = await self.clickhouse.execute(sql, *batch)
            except Exception as exc:
                batch_name = f"{self.table_name}_{idx}_{batch_size}_{len(batch)}"
                raise InsertBatchError(
                    f"Fail to insert batch {batch_name}",
                    batch_name=batch_name,
                    batch_data=batch
                ) from exc
            responses.append(resp)
        return responses


@dataclass
class RepositoryDataLayer(ClickhouseDataLayer):
    clickhouse: ChClient

    table: ClassVar[TableInterface] = RepositoryTable


@dataclass
class AuthorCommitsDataLayer(ClickhouseDataLayer):
    clickhouse: ChClient

    table: ClassVar[TableInterface] = AuthorCommitsTable


@dataclass
class RepositoryPositionDataLayer(ClickhouseDataLayer):
    clickhouse: ChClient

    table: ClassVar[TableInterface] = RepositoryPositionsTable
