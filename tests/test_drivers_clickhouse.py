"""T8: ClickHouse 驱动。"""
from app.core import status
from app.models.connection import ClickHouseConn
from app.models.specs import ClickHouseSpec
from app.drivers.clickhouse import ClickHouseDriver


def _spec(**kw):
    base = dict(name="ck-01", engine_type="clickhouse", cpu="1", memory="2Gi", storage="50Gi")
    base.update(kw)
    return ClickHouseSpec(**base)


def test_build_body_basics():
    d = ClickHouseDriver()
    body = d.build_body(_spec(shards=2))
    assert body["kind"] == "ClickHouseInstallation"
    layout = body["spec"]["configuration"]["clusters"][0]["layout"]
    assert layout["shardsCount"] == 2


def test_build_body_idms_user_block():
    d = ClickHouseDriver()
    body = d.build_body(_spec())
    users = body["spec"]["configuration"]["users"]
    assert "idms/password" in users
    assert users["idms/networks/ip"] == "::/0"
    assert users["idms/profile"] == "default"


def test_build_body_resources_and_storage():
    d = ClickHouseDriver()
    body = d.build_body(_spec(cpu="2", memory="4Gi", storage="100Gi"))
    pod = body["spec"]["templates"]["podTemplates"][0]
    res = pod["spec"]["containers"][0]["resources"]["requests"]
    assert res["cpu"] == "2" and res["memory"] == "4Gi"
    vct = body["spec"]["templates"]["volumeClaimTemplates"][0]
    assert vct["spec"]["resources"]["requests"]["storage"] == "100Gi"


def test_parse_status():
    d = ClickHouseDriver()
    assert d.parse_status({"status": "Completed"}) == status.READY
    assert d.parse_status({"status": "InProgress"}) == status.INITIALIZING
    assert d.parse_status({}) == status.CREATING


def test_parse_connection():
    d = ClickHouseDriver()
    c = d.parse_connection("ck-01")
    assert isinstance(c, ClickHouseConn)
    assert c.host == "clickhouse-ck-01.clickhouse.svc"
    assert c.port == 9000
    assert c.http_port == 8123
    assert c.username == "idms"
