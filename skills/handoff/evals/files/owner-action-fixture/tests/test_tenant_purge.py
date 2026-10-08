from src.tenant_purge import build_payload


def test_payload_keeps_tenant_scope():
    assert build_payload("tenant-42", "eu-west") == {
        "tenant_id": "tenant-42",
        "zone": "eu-west",
        "operation": "purge",
    }
