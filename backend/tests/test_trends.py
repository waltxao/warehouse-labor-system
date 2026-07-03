import pytest


@pytest.mark.asyncio
async def test_trend_not_found(client, admin_token):
    resp = await client.get(
        "/api/v1/trends/FAKE/chart?iso_week=2026-W24",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.json()["code"] == 404


@pytest.mark.asyncio
async def test_comparison_too_many(client, admin_token):
    resp = await client.post(
        "/api/v1/comparison",
        json={"warehouse_codes": ["A", "B", "C", "D", "E", "F", "G"], "iso_week": "2026-W24"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.json()["code"] == 400
