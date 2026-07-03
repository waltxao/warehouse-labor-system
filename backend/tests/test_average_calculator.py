import pytest
from app.services.average_calculator import compute_averages


@pytest.mark.asyncio
async def test_compute_averages_empty_db(db_session):
    """空数据库时应返回 0"""
    count = await compute_averages(db_session, "2026-W24")
    assert count == 0
