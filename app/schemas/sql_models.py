from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    id: int = Field(primary_key = True, index=True)
    email: str = Field(unique_items=True, index=True)
    username: str = Field(unique=True, index=True)
    password: str = Field()

    cart_items: Optional["CartItem"] = Relationship(back_populates="user")
    orders: Optional["Order"] = Relationship(back_populates="user")


class Admin(SQLModel, table=True):
    id: int = Field(primary_key = True, index=True)
    email: str = Field(unique_items=True, index=True)
    adminname: str = Field(unique=True, index=True)
    password: str = Field()

    products: Optional["Product"] = Relationship(back_populates="admin")


class Product(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    name: str = Field(index=True)
    description: str = Field(index=True)
    price: float = Field()
    image_path: str = Field(nullable=True)
    admin_id: int = Field(foreign_key="admin.id")

    cart_items: Optional["CartItem"] = Relationship(back_populates="product")
    orders: Optional["Order"] = Relationship(back_populates="product")
    admin: Optional["Admin"] = Relationship(back_populates="products")

class CartItem(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int

    user: Optional["User"] = Relationship(back_populates="cart_items")
    product: Optional["Product"] = Relationship(back_populates="cart_items")



class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int
    total_amount: float
    order_date: datetime


    user: Optional["User"] = Relationship(back_populates="orders")
    product: Optional["Product"] = Relationship(back_populates="orders")
