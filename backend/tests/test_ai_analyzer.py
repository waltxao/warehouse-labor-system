import pytest
from app.services.ai_analyzer import _build_prompt


@pytest.mark.asyncio
async def test_build_prompt_empty(db_session):
    """空数据库时 prompt 应包含模板文字"""
    prompt = await _build_prompt(db_session, "weekly_compare", ["101D"], "2026-W24")
    assert "倉庫人力資源分析專家" in prompt
    assert "繁體中文" in prompt
