from pydantic import BaseModel


class ComparisonRequest(BaseModel):
    warehouse_codes: list[str]
    iso_week: str
    metric: str = "actual_attendance"  # attendance / required_so / savings / fulfillment_rate


class ComparisonData(BaseModel):
    iso_week: str
    metric: str
    warehouses: list[dict]  # [{code, values: [{date, value}]}]
