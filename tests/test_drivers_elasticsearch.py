"""T10: Elasticsearch 驱动。"""
from app.core import status
from app.models.connection import ElasticsearchConn
from app.models.specs import ElasticsearchSpec
from app.drivers.elasticsearch import ElasticsearchDriver, derive_heap


def _spec(**kw):
    base = dict(name="es-01", engine_type="elasticsearch", cpu="1", memory="2Gi", storage="20Gi")
    base.update(kw)
    return ElasticsearchSpec(**base)


def test_derive_heap_half_of_memory():
    # heap 约为容器内存一半，不再写死 256m
    assert derive_heap("2Gi") == "-Xms1g -Xmx1g"
    assert derive_heap("4Gi") == "-Xms2g -Xmx2g"
    assert derive_heap("1Gi") == "-Xms512m -Xmx512m"
    assert derive_heap("512Mi") == "-Xms256m -Xmx256m"


def test_build_body_uses_derived_heap():
    d = ElasticsearchDriver()
    body = d.build_body(_spec(memory="4Gi"))
    env = body["spec"]["nodeSets"][0]["podTemplate"]["spec"]["containers"][0]["env"]
    heap = next(e["value"] for e in env if e["name"] == "ES_JAVA_OPTS")
    assert heap == "-Xms2g -Xmx2g"


def test_build_body_count_and_storage():
    d = ElasticsearchDriver()
    body = d.build_body(_spec(replicas=3, storage="50Gi"))
    ns = body["spec"]["nodeSets"][0]
    assert ns["count"] == 3
    vct = ns["volumeClaimTemplates"][0]
    assert vct["spec"]["resources"]["requests"]["storage"] == "50Gi"


def test_parse_status():
    d = ElasticsearchDriver()
    assert d.parse_status({"phase": "Ready", "health": "green"}) == status.READY
    assert d.parse_status({"phase": "ApplyingChanges"}) == status.INITIALIZING
    assert d.parse_status({}) == status.CREATING


def test_parse_connection():
    d = ElasticsearchDriver()
    c = d.parse_connection("es-01")
    assert isinstance(c, ElasticsearchConn)
    assert c.host == "es-01-es-http.elastic-system.svc"
    assert c.port == 9200
    assert c.scheme == "https"
    assert c.username == "elastic"
