from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    warehouse_ids: list[int] = []


class UserUpdate(BaseModel):
    is_active: bool | None = None
    role: str | None = None
    warehouse_ids: list[int] | None = None


class UserWithBindings(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    warehouse_ids: list[int]
