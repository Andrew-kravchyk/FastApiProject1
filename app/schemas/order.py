from pydantic import BaseModel
from decimal import Decimal


class OrderCreate(BaseModel):
    user_id: int
    total_price: Decimal = 0


class OrderUpdate(BaseModel):
    total_price: Decimal