from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    category_id: int


class ProductRead(ProductCreate):
    id: int

    class Config:
        from_attributes = True