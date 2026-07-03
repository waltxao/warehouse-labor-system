import pytest
from app.services.excel_parser import parse_excel, WAREHOUSE_CODE_PATTERN


def test_warehouse_code_pattern():
    assert WAREHOUSE_CODE_PATTERN.match("101D")
    assert WAREHOUSE_CODE_PATTERN.match("1800")
    assert WAREHOUSE_CODE_PATTERN.match("CA11")
    assert WAREHOUSE_CODE_PATTERN.match("GA11")
    assert not WAREHOUSE_CODE_PATTERN.match("Total")
    assert not WAREHOUSE_CODE_PATTERN.match("项目")
    assert not WAREHOUSE_CODE_PATTERN.match("")
