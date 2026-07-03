import pytest


@pytest.mark.asyncio
async def test_upload_requires_admin(client):
    """非 admin 用户不能上传"""
    resp = await client.post("/api/v1/upload")
    assert resp.status_code == 403 or resp.json().get("code") in (401, 403)


@pytest.mark.asyncio
async def test_upload_no_file(client, admin_token):
    """admin 上传但未提供文件"""
    resp = await client.post("/api/v1/upload", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.json()["code"] == 400
