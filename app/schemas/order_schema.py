from datetime import datetime

from pydantic import BaseModel
from typing import List
from app.schemas.sql_models import Product
from app.schemas.user_schema import UserResponse

class OrderBase(BaseModel):
    id: int
    user_id: int
    products: List[Product]
    quantity: List[int]
    order_date: datetime

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    products: List[Product]

class PlaceOrderRequest(BaseModel):
    cart_id: int

class OrderResponse(BaseModel):
    id: int
    user_details: UserResponse
    products: List[Product]
    quantity: List[int]
    total_amount: float
    order_date: datetime

class OrderEachResponse(BaseModel):
    id: int
    user_details: UserResponse
    products: Product
    quantity: int
    total_amount: float
    order_date: datetime

    class Config:
        orm_mode = True



