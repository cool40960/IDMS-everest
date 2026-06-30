"""T4: 参数模型（设计稿 §五）。"""
import pytest
from pydantic import ValidationError

from app.models import specs


# ---------- name 校验 ----------
@pytest.mark.parametrize("name", ["ck-01", "redis", "a1", "my-db-123"])
def test_valid_names(name):
    s = specs.BaseSpec(name=name, engine_type="redis", cpu="1", memory="2Gi", storage="20Gi")
    assert s.name == name


@pytest.mark.parametrize(
    "name",
    ["CK-01", "1redis", "-foo", "foo_bar", "a" * 64, "", "foo.bar"],
)
def test_invalid_names(name):
    with pytest.raises(ValidationError):
        specs.BaseSpec(name=name, engine_type="redis", cpu="1", memory="2Gi", storage="20Gi")


def test_name_max_63():
    specs.BaseSpec(name="a" * 63, engine_type="redis", cpu="1", memory="2Gi", storage="20Gi")
    with pytest.raises(ValidationError):
        specs.BaseSpec(name="a" * 64, engine_type="redis", cpu="1", memory="2Gi", storage="20Gi")


# ---------- cpu / memory / storage 校验 ----------
@pytest.mark.parametrize("cpu", ["1", "2", "500m", "0.5"])
def test_valid_cpu(cpu):
    s = specs.BaseSpec(name="x", engine_type="redis", cpu=cpu, memory="2Gi", storage="20Gi")
    assert s.cpu == cpu


@pytest.mark.parametrize("cpu", ["1G", "abc", "500", "1.2.3", ""])
def test_invalid_cpu(cpu):
    # 注意 "500" 不带 m 视为核数合法（^\d+$），这里放进的是真错的
    if cpu == "500":
        return  # 500 其实合法（500 核），跳过
    with pytest.raises(ValidationError):
        specs.BaseSpec(name="x", engine_type="redis", cpu=cpu, memory="2Gi", storage="20Gi")


@pytest.mark.parametrize("val", ["2Gi", "512Mi", "100Gi"])
def test_valid_memory_storage(val):
    s = specs.BaseSpec(name="x", engine_type="redis", cpu="1", memory=val, storage=val)
    assert s.memory == val


@pytest.mark.parametrize("val", ["2G", "512M", "2gb", "2", "2GiB"])
def test_invalid_memory_storage(val):
    with pytest.raises(ValidationError):
        specs.BaseSpec(name="x", engine_type="redis", cpu="1", memory=val, storage="20Gi")


# ---------- replicas ----------
def test_replicas_default_and_floor():
    s = specs.BaseSpec(name="x", engine_type="redis", cpu="1", memory="2Gi", storage="20Gi")
    assert s.replicas == 1
    with pytest.raises(ValidationError):
        specs.BaseSpec(name="x", engine_type="redis", cpu="1", memory="2Gi", storage="20Gi", replicas=0)


# ---------- engine_type 枚举 ----------
def test_engine_type_enum():
    with pytest.raises(ValidationError):
        specs.BaseSpec(name="x", engine_type="oracle", cpu="1", memory="2Gi", storage="20Gi")


# ---------- ClickHouse 专属 shards ----------
def test_clickhouse_shards_default():
    s = specs.ClickHouseSpec(name="ck", engine_type="clickhouse", cpu="1", memory="2Gi", storage="50Gi")
    assert s.shards == 1
    s2 = specs.ClickHouseSpec(name="ck", engine_type="clickhouse", cpu="1", memory="2Gi", storage="50Gi", shards=3)
    assert s2.shards == 3


def test_other_specs_no_shards():
    s = specs.RedisSpec(name="r", engine_type="redis", cpu="1", memory="2Gi", storage="20Gi")
    assert not hasattr(s, "shards")


# ---------- 工厂 spec_for ----------
def test_spec_for_picks_right_class():
    payload = {"name": "ck", "engine_type": "clickhouse", "cpu": "1", "memory": "2Gi", "storage": "50Gi", "shards": 2}
    s = specs.spec_for("clickhouse", payload)
    assert isinstance(s, specs.ClickHouseSpec)
    assert s.shards == 2


def test_spec_for_rejects_unknown():
    with pytest.raises(ValueError):
        specs.spec_for("oracle", {"name": "x"})
