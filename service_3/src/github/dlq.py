import json
import pathlib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeAlias, Any


class DLQInterface(ABC):

    @abstractmethod
    async def enqueue(self, batch_name, batch_data):
        raise NotImplementedError


JSONSerializable: TypeAlias = (
    None
    | bool
    | int
    | float
    | str
    | list["JSONSerializable"]
    | dict[str, "JSONSerializable"]
)

# ToDo JSON as test or emo, in real app probably you wanna use kafka, rabbitmq or even clickhouse
@dataclass
class JsonDLQ(DLQInterface):
    directory: pathlib.Path

    async def enqueue(self, batch_name: str, batch_data: JSONSerializable):
        filename = f"{batch_name}_{int(time.time())}.json"
        with open(self.directory / filename, 'w') as fp:
            json.dump(batch_data, fp, ensure_ascii=False)
