from src.cdn_purge import build_purge_request


def test_purge_uses_tenant_region():
    assert build_purge_request("tenant-42", "eu-west") == {"tenant": "tenant-42", "region": "eu-west"}
