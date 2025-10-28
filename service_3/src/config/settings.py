import pathlib

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import NamedTuple


class RPSLimit(NamedTuple):
    max_rate: int
    time_period: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=pathlib.Path(__file__).parent.parent / '.env', env_file_encoding='utf-8')


    GITHUB_ACCESS_TOKEN: str
    MCR_LIMIT: int = 5
    # https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api?apiVersion=2022-11-28#primary-rate-limit-for-authenticated-users
    RPC_LIMIT: RPSLimit = RPSLimit(max_rate=5000, time_period=3600)
    # Clickhouse
    CLICKHOUSE_HOST: str
    CLICKHOUSE_PORT: int
    CLICKHOUSE_USER: str
    CLICKHOUSE_PASSWORD: str
    CLICKHOUSE_DB: str
    # DLQ
    DLQ_DIRECTORY: pathlib.Path = pathlib.Path('/var/lib/service_3/dlq')

    @property
    def github_auth(self) -> dict:
        return {
            "Authorization": f"Bearer {self.GITHUB_ACCESS_TOKEN}",
        }

    @property
    def clickhouse_params(self):
        return {
            'url': f"http://{self.CLICKHOUSE_HOST}:{self.CLICKHOUSE_PORT}/",
            'user': self.CLICKHOUSE_USER,
            'password': self.CLICKHOUSE_PASSWORD,
            'database': self.CLICKHOUSE_DB
        }

    @property
    def clickhouse_connection_config(self) -> dict:
        return dict(
            limit=100,
            keepalive_timeout=60,
        )

    @property
    def http_connection_config(self) -> dict:
        return dict(
            limit=50,
            keepalive_timeout=60,
            ttl_dns_cache=300
        )