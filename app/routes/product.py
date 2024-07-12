import os
from typing import List

from fastapi import APIRouter, HTTPException, Form, File, Depends, UploadFile
from sqlalchemy import func, extract
from sqlmodel import Session, select

from app import schemas
from app.schemas.sql_models import Product, Order
from app.schemas.product_schema import ProductSalesData
from app.database import get_session

router = APIRouter(tags=["Products"])

@router.post("/admins/{admin_id}/products/", response_model=schemas.sql_models.Product, status_code=201)
def create_product(
    admin_id: int,
    name: str,
    description: str,
    price: float,
    image_file: UploadFile = File(...),
    db: Session = Depends(get_session)
):
    try:
        # Save uploaded image to a directory within the project
        upload_folder = "./static/uploads"
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, image_file.filename)
        with open(image_path, "wb") as image:
            image.write(image_file.file.read())

        # Create new product instance with provided data including admin_id
        db_product = schemas.sql_models.Product(
            name=name,
            description=description,
            price=price,
            image_path=image_path,
            admin_id=admin_id
        )

        # Add product to database
        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        # Return the product with image_path included in the response
        return db_product

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/allproducts", response_model=list[schemas.sql_models.Product])
def get_all_products(db: Session = Depends(get_session)):
    db_product = db.query(schemas.sql_models.Product).all()
    return db_product

@router.get("/{product_id}", response_model=schemas.sql_models.Product)
def read_product(product_id: int, db: Session = Depends(get_session)):
    db_product = db.query(schemas.sql_models.Product).filter(schemas.sql_models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product  # This will automatically serialize to schemas.Product


@router.get("/admins/{admin_id}/products/", response_model=list[schemas.sql_models.Product])
def get_products_by_seller(admin_id: int, db: Session = Depends(get_session)):
    try:
        # Query the database to retrieve all products associated with the specified admin_id
        db_products = (
            db.query(schemas.sql_models.Product)
            .filter(schemas.sql_models.Product.admin_id == admin_id)
            .all()
        )

        if not db_products:
            raise HTTPException(status_code=404, detail="Products not found for this seller")

        return db_products

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/products/{product_id}/admin/{admin_id}", response_model=schemas.sql_models.Product)
def delete_product(product_id: int, admin_id: int, db: Session = Depends(get_session)):
    db_product = db.query(schemas.sql_models.Product).filter(
        schemas.sql_models.Product.id == product_id,
        schemas.sql_models.Product.admin_id == admin_id
    ).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Create a copy of the product before deletion for response
    deleted_product = schemas.sql_models.Product.from_orm(db_product)

    # Delete the image file from the filesystem if it exists
    if db_product.image_path and os.path.exists(db_product.image_path):
        os.remove(db_product.image_path)

    # Delete the product from the database
    db.delete(db_product)
    db.commit()

    return deleted_product



@router.put("/products/{product_id}", response_model=schemas.sql_models.Product)
def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    image_file: UploadFile = File(None),
    db: Session = Depends(get_session)
):
    # Check if the product with the specified ID exists in the database
    db_product = db.query(schemas.sql_models.Product).filter(schemas.sql_models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update the product attributes based on the input data
    if name:
        db_product.name = name
    if description:
        db_product.description = description
    if price is not None:
        db_product.price = price

    # Handle image file update if provided
    if image_file:
        upload_folder = "./static/uploads"
        os.makedirs(upload_folder, exist_ok=True)
        image_path = os.path.join(upload_folder, image_file.filename)
        with open(image_path, "wb") as image:
            image.write(image_file.file.read())
        db_product.image_path = image_path

    # Commit the changes to the database
    db.commit()
    db.refresh(db_product)

    # Return the updated product
    return db_product



# route for analysis


@router.get("/admins/{admin_id}/product-sales", response_model=List[ProductSalesData])
def get_product_sales_data(admin_id: int, db: Session = Depends(get_session)):
    try:
        statement = (
            select(Product.name, func.sum(Order.quantity).label("total_quantity"))
            .join(Order, Product.id == Order.product_id)
            .where(Product.admin_id == admin_id)
            .group_by(Product.name)
        )
        results = db.exec(statement).all()

        if not results:
            raise HTTPException(status_code=404, detail="No sales data found for this seller")

        return [ProductSalesData(name=name, total_quantity=total_quantity) for name, total_quantity in results]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.get("/products/{product_id}/monthly-orders", response_model=dict)
# def get_monthly_orders_for_product(product_id: int, db: Session = Depends(get_session)):
#     try:
#         # Query the database to retrieve the monthly order count for the specified product
#         monthly_orders = (
#             db.query(
#                 func.strftime("%Y-%m", Order.order_date).label("month"),
#                 func.count(Order.id).label("order_count")
#             )
#             .join(Order.product)
#             .filter(Product.id == product_id)
#             .group_by("month")
#             .order_by("month")
#             .all()
#         )
#
#         if not monthly_orders:
#             raise HTTPException(status_code=404, detail="No orders found for this product")
#
#         # Convert the result to a dictionary
#         orders_by_month = {order.month: order.order_count for order in monthly_orders}
#
#         return orders_by_month
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#         return orders_by_month
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))




@router.get("/admins/{admin_id}/products/{year}/monthly-orders", response_model=dict)
def get_monthly_orders(admin_id: int, year: int, db: Session = Depends(get_session)):
    try:
        monthly_orders = (
            db.query(
                Product.id.label("product_id"),
                func.strftime("%m", Order.order_date).label("month"),
                func.count(Order.id).label("order_count")
            )
            .join(Order.product)
            .filter(extract('year', Order.order_date) == year)
            .group_by(Product.id, "month")
            .all()
        )

        if not monthly_orders:
            raise HTTPException(status_code=404, detail="No orders found for this year")

        # Organize the results by month
        orders_by_month = {month: {} for month in range(1, 13)}
        for order in monthly_orders:
            orders_by_month[int(order.month)][order.product_id] = order.order_count

        return orders_by_month

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admins/{admin_id}/years", response_model=list)
def get_years(admin_id: int, db: Session = Depends(get_session)):
    try:
        years = db.query(extract('year', Order.order_date).distinct().label("year")).all()
        return [year.year for year in years]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))