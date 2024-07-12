from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app import schemas
from app.database import get_session
from app.schemas.cartitem_schema import CartItemResponse, CartItemCreate
from app.schemas.sql_models import CartItem, Product, User
from app.schemas import product_schema, cartitem_schema
from app.schemas import user_schema

router = APIRouter(tags=["Cart"])


# @router.post("/users/{user_id}/cart/add", response_model=cartitem_schema.CartItemResponse)
# def add_to_cart(user_id: int, cart_item: cartitem_schema.CartItemCreate, db: Session = Depends(get_session)):
#     # Check if the product exists
#     db_product = db.query(Product).get(cart_item.product_id)
#     if not db_product:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
#
#     # Retrieve user details
#     db_user = db.query(User).get(user_id)
#     if not db_user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#
#     # Check if the product is already in the user's cart
#     existing_cart_item = (
#         db.query(CartItem)
#         .filter(CartItem.user_id == user_id)
#         .filter(CartItem.product_id == cart_item.product_id)
#         .first()
#     )
#
#     if existing_cart_item:
#         # If the product is already in the cart, increment the quantity
#         existing_cart_item.quantity += cart_item.quantity
#         db.commit()
#         db.refresh(existing_cart_item)
#         new_cart_item = existing_cart_item
#     else:
#         # Otherwise, create a new cart item associated with the user
#         new_cart_item = CartItem(
#             user_id=user_id,
#             product_id=cart_item.product_id,
#             admin_id=db_product.admin_id,  # Set admin_id from the product's admin_id
#             quantity=cart_item.quantity
#         )
#         db.add(new_cart_item)
#         db.commit()
#         db.refresh(new_cart_item)
#
#     # Construct the product details for the newly added cart item
#     product_detail = db_product
#
#     # Construct the user details
#     user_details = user_schema.UserResponse(
#         id=db_user.id,
#         username=db_user.username,
#         email=db_user.email
#     )
#
#     # Construct the CartItemResponse with the user and product details
#     cart_item_response = cartitem_schema.CartItemResponse(
#         id=new_cart_item.id,
#         user_details=user_details,
#         product_id=new_cart_item.product_id,
#         product_details=product_detail,
#         quantity=new_cart_item.quantity
#     )
#
#     return cart_item_response




@router.post("/users/{user_id}/cart/add", response_model=cartitem_schema.CartItemResponse)
def add_to_cart(user_id: int, cart_item: cartitem_schema.CartItemCreate, db: Session = Depends(get_session)):
    # Check if the product exists
    db_product = db.query(Product).get(cart_item.product_id)
    if not db_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Retrieve user details
    db_user = db.query(User).get(user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if the product is already in the user's cart
    existing_cart_item = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .filter(CartItem.product_id == cart_item.product_id)
        .first()
    )

    if existing_cart_item:
        # If the product is already in the cart, increment the quantity
        existing_cart_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_cart_item)
        new_cart_item = existing_cart_item
    else:
        # Otherwise, create a new cart item associated with the user
        new_cart_item = CartItem(
            user_id=user_id,
            product_id=cart_item.product_id,
            admin_id=db_product.admin_id,  # Set admin_id from the product's admin_id
            quantity=cart_item.quantity
        )
        db.add(new_cart_item)
        db.commit()
        db.refresh(new_cart_item)

    # Construct the product details for the newly added cart item
    product_detail = db_product

    # Construct the user details
    user_details = user_schema.UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email
    )

    # Construct the CartItemResponse with the user and product details
    cart_item_response = cartitem_schema.CartItemResponse(
        id=new_cart_item.id,
        user_details=user_details,
        product_id=new_cart_item.product_id,
        product_details=product_detail,
        quantity=new_cart_item.quantity
    )

    return cart_item_response



@router.get("/cart/items/", response_model=List[cartitem_schema.CartItemResponse])
def get_cart_items(user_id: int, db: Session = Depends(get_session)):
    # Retrieve cart items for the specified user including product details
    cart_items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .all()
    )

    if not cart_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cart items found for user {user_id}")

    # Dictionary to aggregate cart items by product ID
    product_dict = {}
    for cart_item in cart_items:
        if cart_item.product_id in product_dict:
            # If product ID already exists in the dictionary, increment the quantity
            product_dict[cart_item.product_id]["quantity"] += cart_item.quantity
        else:
            # If product ID is not in the dictionary, add a new entry
            product_dict[cart_item.product_id] = {
                "id": cart_item.id,
                "product_id": cart_item.product_id,
                "quantity": cart_item.quantity
            }

    # List to hold the final cart item responses
    cart_item_responses = []
    for product_id, item_info in product_dict.items():
        # Retrieve the associated product details
        db_product = db.query(Product).get(product_id)

        if not db_product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {product_id} not found")

        # Retrieve user details (including the username) from the database
        db_user = db.query(User).get(user_id)

        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")

        # Construct the ProductResponse for the associated product
        product_details = db_product

        # Construct the UserResponse with the retrieved username
        user_details = user_schema.UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email
        )

        # Construct the CartItemResponse
        cart_item_response = cartitem_schema.CartItemResponse(
            id=item_info["id"],
            user_details=user_details,
            product_id=item_info["product_id"],
            product_details=product_details,
            quantity=item_info["quantity"],
        )
        cart_item_responses.append(cart_item_response)

    return cart_item_responses



@router.delete("/{user_id}/cart/{product_id}")
def delete_cart_item(user_id: int, product_id: int, db: Session = Depends(get_session)):
    # Check if the user exists
    user = db.query(schemas.sql_models.User).filter(schemas.sql_models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if there are cart items with the specified product ID for the user
    cart_items = db.query(schemas.sql_models.CartItem).filter(
        schemas.sql_models.CartItem.user_id == user_id,
        schemas.sql_models.CartItem.product_id == product_id
    ).all()

    if not cart_items:
        raise HTTPException(status_code=404, detail=f"No cart items found for user with product ID {product_id}")

    # Delete all cart items with the specified product ID for the user
    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()

    return {"message": f"All cart items with product ID {product_id} deleted successfully for user"}



@router.put("/cart/items/{item_id}", response_model=schemas.cartitem_schema.CartItemResponse)
def update_cart_item_quantity(cart_item_id: int, quantity: int, db: Session = Depends(get_session)):
    # Retrieve the cart item by its ID
    cart_item = db.query(schemas.sql_models.CartItem).get(cart_item_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail=f"Cart item with ID {cart_item_id} not found")

    # Update the quantity of the cart item
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)

    # Retrieve associated product and user details
    db_product = db.query(schemas.sql_models.Product).get(cart_item.product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail=f"Product with ID {cart_item.product_id} not found")

    db_user = db.query(schemas.sql_models.User).get(cart_item.user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User with ID {cart_item.user_id} not found")

    # Construct the CartItemResponse with updated details
    product_details = schemas.sql_models.Product.from_orm(db_product)
    user_details = schemas.user_schema.UserResponse(id=db_user.id, username=db_user.username, email=db_user.email)

    cart_item_response = schemas.cartitem_schema.CartItemResponse(
        id=cart_item.id,
        user_details=user_details,
        product_id=cart_item.product_id,
        product_details=product_details,
        quantity=cart_item.quantity
    )

    return cart_item_response
































































































# from typing import List
#
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlmodel import Session
#
# from app import schemas
# from app.database import get_session
# from app.schemas.cartitem_schema import CartItemResponse, CartItemCreate
# from app.schemas.sql_models import CartItem, Product, User
# from app.schemas import product_schema, cartitem_schema
# from app.schemas import user_schema
#
# router = APIRouter(tags=["Cart"])
#
#
# @router.post("/users/{user_id}/cart/add", response_model=cartitem_schema.CartItemResponse)
# def add_to_cart(user_id: int, cart_item: cartitem_schema.CartItemCreate, db: Session = Depends(get_session)):
#     # Check if the product exists
#     db_product = db.query(Product).get(cart_item.product_id)
#     if not db_product:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
#
#     # Retrieve user details
#     db_user = db.query(User).get(user_id)
#     if not db_user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#
#     # Check if the product is already in the user's cart
#     existing_cart_item = (
#         db.query(CartItem)
#         .filter(CartItem.user_id == user_id)
#         .filter(CartItem.product_id == cart_item.product_id)
#         .first()
#     )
#
#     if existing_cart_item:
#         # If the product is already in the cart, increment the quantity
#         existing_cart_item.quantity += cart_item.quantity
#         db.commit()
#         db.refresh(existing_cart_item)
#         new_cart_item = existing_cart_item
#     else:
#         # Otherwise, create a new cart item associated with the user
#         new_cart_item = CartItem(user_id=user_id, **cart_item.dict())
#         db.add(new_cart_item)
#         db.commit()
#         db.refresh(new_cart_item)
#
#     # Construct the product details for the newly added cart item
#     product_detail = db_product
#
#     # Construct the user details
#     user_details = user_schema.UserResponse(
#         id=db_user.id,
#         username=db_user.username,
#         email=db_user.email
#     )
#
#     # Construct the CartItemResponse with the user and product details
#     cart_item_response = cartitem_schema.CartItemResponse(
#         id=new_cart_item.id,
#         user_details=user_details,
#         product_id=new_cart_item.product_id,
#         product_details=product_detail,
#         quantity=new_cart_item.quantity
#     )
#
#     return cart_item_response
#
#
# @router.get("/cart/items/", response_model=List[cartitem_schema.CartItemResponse])
# def get_cart_items(user_id: int, db: Session = Depends(get_session)):
#     # Retrieve cart items for the specified user including product details
#     cart_items = (
#         db.query(CartItem)
#         .filter(CartItem.user_id == user_id)
#         .all()
#     )
#
#     if not cart_items:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No cart items found for user {user_id}")
#
#     # Dictionary to aggregate cart items by product ID
#     product_dict = {}
#     for cart_item in cart_items:
#         if cart_item.product_id in product_dict:
#             # If product ID already exists in the dictionary, increment the quantity
#             product_dict[cart_item.product_id]["quantity"] += cart_item.quantity
#         else:
#             # If product ID is not in the dictionary, add a new entry
#             product_dict[cart_item.product_id] = {
#                 "id": cart_item.id,
#                 "product_id": cart_item.product_id,
#                 "quantity": cart_item.quantity
#             }
#
#     # List to hold the final cart item responses
#     cart_item_responses = []
#     for product_id, item_info in product_dict.items():
#         # Retrieve the associated product details
#         db_product = db.query(Product).get(product_id)
#
#         if not db_product:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with id {product_id} not found")
#
#         # Retrieve user details (including the username) from the database
#         db_user = db.query(User).get(user_id)
#
#         if not db_user:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found")
#
#         # Construct the ProductResponse for the associated product
#         product_details = db_product
#
#         # Construct the UserResponse with the retrieved username
#         user_details = user_schema.UserResponse(
#             id=db_user.id,
#             username=db_user.username,
#             email=db_user.email
#         )
#
#         # Construct the CartItemResponse
#         cart_item_response = cartitem_schema.CartItemResponse(
#             id=item_info["id"],
#             user_details=user_details,
#             product_id=item_info["product_id"],
#             product_details=product_details,
#             quantity=item_info["quantity"],
#         )
#         cart_item_responses.append(cart_item_response)
#
#     return cart_item_responses
#
#
#
# @router.delete("/{user_id}/cart/{product_id}")
# def delete_cart_item(user_id: int, product_id: int, db: Session = Depends(get_session)):
#     # Check if the user exists
#     user = db.query(schemas.sql_models.User).filter(schemas.sql_models.User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     # Check if there are cart items with the specified product ID for the user
#     cart_items = db.query(schemas.sql_models.CartItem).filter(
#         schemas.sql_models.CartItem.user_id == user_id,
#         schemas.sql_models.CartItem.product_id == product_id
#     ).all()
#
#     if not cart_items:
#         raise HTTPException(status_code=404, detail=f"No cart items found for user with product ID {product_id}")
#
#     # Delete all cart items with the specified product ID for the user
#     for cart_item in cart_items:
#         db.delete(cart_item)
#
#     db.commit()
#
#     return {"message": f"All cart items with product ID {product_id} deleted successfully for user"}
#
#
#
# @router.put("/cart/items/{item_id}", response_model=schemas.cartitem_schema.CartItemResponse)
# def update_cart_item_quantity(cart_item_id: int, quantity: int, db: Session = Depends(get_session)):
#     # Retrieve the cart item by its ID
#     cart_item = db.query(schemas.sql_models.CartItem).get(cart_item_id)
#     if not cart_item:
#         raise HTTPException(status_code=404, detail=f"Cart item with ID {cart_item_id} not found")
#
#     # Update the quantity of the cart item
#     cart_item.quantity = quantity
#     db.commit()
#     db.refresh(cart_item)
#
#     # Retrieve associated product and user details
#     db_product = db.query(schemas.sql_models.Product).get(cart_item.product_id)
#     if not db_product:
#         raise HTTPException(status_code=404, detail=f"Product with ID {cart_item.product_id} not found")
#
#     db_user = db.query(schemas.sql_models.User).get(cart_item.user_id)
#     if not db_user:
#         raise HTTPException(status_code=404, detail=f"User with ID {cart_item.user_id} not found")
#
#     # Construct the CartItemResponse with updated details
#     product_details = schemas.sql_models.Product.from_orm(db_product)
#     user_details = schemas.user_schema.UserResponse(id=db_user.id, username=db_user.username, email=db_user.email)
#
#     cart_item_response = schemas.cartitem_schema.CartItemResponse(
#         id=cart_item.id,
#         user_details=user_details,
#         product_id=cart_item.product_id,
#         product_details=product_details,
#         quantity=cart_item.quantity
#     )
#
#     return cart_item_response
