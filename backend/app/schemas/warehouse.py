from pydantic import BaseModel


class WarehouseResponse(BaseModel):
    id: int
    code: str
    name: str | None
    is_active: bool


class WarehouseCreate(BaseModel):
    code: str
    name: str | None = None
