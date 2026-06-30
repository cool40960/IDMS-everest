"""连接对象模型（设计稿 §七）。

不硬塞统一的 {host,port,username,password}：Kafka 无账密、Redis 有 sentinel、
ES 走 HTTPS——硬塞会逼前台对各引擎做 if-else。改用「带 type 字段的连接对象」：
公共最小基（type+host+port），各引擎按需扩展自己的字段。前台按 type 分支渲染。

实现为 Pydantic 判别联合（discriminated union，按 type 区分），Swagger 会
分别列出每种引擎的连接字段。
"""
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field


class BaseConnection(BaseModel):
    """公共最小基：所有连接都有 host + port。type 由各子类用 Literal 固定。"""
    host: str
    port: int


class MySQLConn(BaseConnection):
    type: Literal["mysql"] = "mysql"
    username: str
    password: str


class PostgreSQLConn(BaseConnection):
    type: Literal["postgresql"] = "postgresql"
    username: str
    password: str


class MongoDBConn(BaseConnection):
    type: Literal["mongodb"] = "mongodb"
    username: str
    password: str


class ClickHouseConn(BaseConnection):
    type: Literal["clickhouse"] = "clickhouse"
    username: str
    password: str
    http_port: int = 8123


class ElasticsearchConn(BaseConnection):
    type: Literal["elasticsearch"] = "elasticsearch"
    scheme: str = "https"  # ECK 默认开 TLS
    username: str = "elastic"
    password: str
    ca_cert: Optional[str] = None


class KafkaConn(BaseConnection):
    type: Literal["kafka"] = "kafka"
    bootstrap_servers: str
    security: str = "PLAINTEXT"  # 内部 plain listener；无 username/password


class SentinelInfo(BaseModel):
    host: str
    port: int = 26379
    master_name: str = "mymaster"


class RedisConn(BaseConnection):
    type: Literal["redis"] = "redis"
    password: str
    sentinel: Optional[SentinelInfo] = None


# 判别联合：按 type 字段自动选对应模型
Connection = Annotated[
    Union[
        MySQLConn,
        PostgreSQLConn,
        MongoDBConn,
        ClickHouseConn,
        ElasticsearchConn,
        KafkaConn,
        RedisConn,
    ],
    Field(discriminator="type"),
]
