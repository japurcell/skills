def build_payload(tenant_id, zone):
    return {"tenant_id": tenant_id, "zone": zone, "operation": "purge"}
