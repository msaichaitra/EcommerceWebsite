from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select
from app.database import get_session
from app.schemas import order_schema, product_schema, user_schema
from datetime import datetime
from pytz import timezone
from app.utils import get_current_user
from app import schemas
from app.schemas.cartitem_schema import CartItemResponse, CartBase
from app.schemas.sql_models import Order, User, CartItem, Product, Admin
from app.schemas.order_schema import OrderCreate, OrderResponse, PlaceOrderRequest, OrderUpdate
from app.schemas.user_schema import UserResponse

router = APIRouter(prefix="/orders", tags=["Orders"])



@router.post("/place", response_model=List[order_schema.OrderResponse], status_code=status.HTTP_201_CREATED)
def place_order(user_id: int, db: Session = Depends(get_session)):
    # Retrieve cart items for the specified user_id
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()

    if not cart_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cart items found for user ID {user_id}")

    # List to hold order details
    order_details = []
    total_order_amount = 0.0

    for cart_item in cart_items:
        # Retrieve product details
        product = db.query(Product).get(cart_item.product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {cart_item.product_id} not found")

        # Calculate total amount for the current cart item
        item_total_amount = product.price * cart_item.quantity
        total_order_amount += item_total_amount

        # Create Order record
        order = Order(
            user_id=user_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            total_amount=item_total_amount,
            order_date=datetime.now()
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        # Prepare OrderResponse
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")

        user_details = user_schema.UserResponse(
            id=user.id,
            username=user.username,
            email=user.email
        )

        product_details = product_schema.ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            price=product.price,
            image_path=product.image_path,
            admin_id=product.admin_id
        )

        order_response = order_schema.OrderResponse(
            id=order.id,
            user_details=user_details,
            products=[product_details],
            quantity=[cart_item.quantity],
            total_amount=item_total_amount,
            order_date=order.order_date
        )

        order_details.append(order_response)

    # Clear the cart after placing the order
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()

    return order_details


@router.get("/{user_id}", response_model=List[order_schema.OrderEachResponse], status_code=200)
def get_user_orders(user_id: int, db: Session = Depends(get_session)):
    try:
        # Retrieve all orders for the specified user within no_autoflush block
        with db.no_autoflush:
            orders = db.query(Order).filter(Order.user_id == user_id).all()

            if not orders:
                raise HTTPException(status_code=404, detail=f"No orders found for user ID {user_id}")

            # Prepare response
            order_responses = []
            for order in orders:
                user = db.query(User).get(order.user_id)
                if not user:
                    raise HTTPException(status_code=404, detail=f"User with ID {order.user_id} not found")

                user_details = order_schema.UserResponse(id=user.id, username=user.username, email=user.email)
                product = db.query(Product).get(order.product_id)
                if not product:
                    raise HTTPException(status_code=404, detail=f"Product with ID {order.product_id} not found")

                # Get Indian Standard Time (IST) timezone
                ist = timezone('Asia/Kolkata')

                # Convert order_date to Indian Standard Time (IST) and make it naive
                order_date_ist = order.order_date.astimezone(ist).replace(tzinfo=None)

                order_response = order_schema.OrderEachResponse(
                    id=order.id,
                    user_details=user_details,
                    products=order_schema.Product.from_orm(product),
                    quantity=order.quantity,
                    total_amount=order.total_amount,
                    order_date=order_date_ist  # Include order_date in IST without timezone info
                )
                order_responses.append(order_response)

        return order_responses

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/admin/{admin_id}/orders", response_model=List[order_schema.OrderEachResponse], status_code=200)
def get_admin_orders(admin_id: int, db: Session = Depends(get_session)):
    try:
        with db.no_autoflush:
            # Retrieve all orders for the specified admin_id by joining with Product table
            orders = db.query(Order).join(Product, Product.id == Order.product_id).filter(Product.admin_id == admin_id).all()

            if not orders:
                raise HTTPException(status_code=404, detail=f"No orders found for admin ID {admin_id}")

            order_responses = []
            for order in orders:
                # Retrieve user details for the order
                user = db.query(User).get(order.user_id)
                if not user:
                    raise HTTPException(status_code=404, detail=f"User with ID {order.user_id} not found")

                user_details = order_schema.UserResponse(id=user.id, username=user.username, email=user.email)

                # Retrieve product details for the order
                product = db.query(Product).get(order.product_id)
                if not product:
                    raise HTTPException(status_code=404, detail=f"Product with ID {order.product_id} not found")

                # Get Indian Standard Time (IST) timezone
                ist = timezone('Asia/Kolkata')

                # Convert order_date to Indian Standard Time (IST) and make it naive
                order_date_ist = order.order_date.astimezone(ist).replace(tzinfo=None)

                # Construct order response
                order_response = order_schema.OrderEachResponse(
                    id=order.id,
                    user_details=user_details,
                    products=order_schema.Product.from_orm(product),
                    quantity=order.quantity,
                    total_amount=order.total_amount,
                    order_date=order_date_ist
                )
                order_responses.append(order_response)

            return order_responses

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.delete("/{order_id}", response_model=dict)
def delete_order(order_id: int, db: Session = Depends(get_session)):
    try:
        # Retrieve the order by its ID
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found")

        # Get Indian Standard Time (IST) timezone
        ist = timezone('Asia/Kolkata')

        # Convert order_date to Indian Standard Time (IST) and make it naive
        order_date_ist = db_order.order_date.astimezone(ist).replace(tzinfo=None)

        # Get the ID of the order being deleted
        deleted_order_id = db_order.id

        # Delete the order from the database
        db.delete(db_order)
        db.commit()

        # Return a dictionary with the details of the deleted order
        return {
            "id": deleted_order_id,
            "user_id": db_order.user_id,
            "product_id": db_order.product_id,
            "quantity": db_order.quantity,
            "total_amount": db_order.total_amount,
            "order_date": order_date_ist,
            "message": f"Order {deleted_order_id} deleted successfully"
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



