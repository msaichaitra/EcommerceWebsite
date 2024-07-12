from pydantic import BaseModel
from app.schemas.sql_models import Product
from app.schemas.user_schema import UserResponse


class CartItemBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

class CartBase(BaseModel):
    id: int

class CartItemResponse(BaseModel):
    id: int
    user_details: UserResponse
    product_id: int
    product_details: Product
    quantity: int

