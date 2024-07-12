from typing import List

from pydantic import BaseModel
from sqlmodel import SQLModel

from app.schemas.order_schema import OrderEachResponse


class ProductBase(BaseModel):
    id: int
    name: str
    description: str
    price: float


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_path: str
    admin_id: int


class ProductCreate(ProductBase):
    pass


class ProductSalesData(BaseModel):
    name: str
    total_quantity: int


class ProductUpdate(ProductBase):
    pass


class ProductWithOrdersResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_path: str
    orders: List[OrderEachResponse]


    class Config:
        orm_mode = True

