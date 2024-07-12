from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session
from app.schemas.sql_models import  Admin
from app.schemas.admin_schema import AdminCreate, AdminBase, AdminResponse, AdminLogin
from app.database import get_session
from app.utils import hash_password, verify_password
from typing import List
from app import schemas

router = APIRouter(tags=["Admin"])


@router.post("/adminregister/", response_model=schemas.admin_schema.AdminResponse, status_code=status.HTTP_201_CREATED)
def register_admin(admin_create: AdminCreate, db: Session = Depends(get_session)):
    # Check if the admin already exists
    existing_admin = db.query(Admin).filter(Admin.adminname == admin_create.adminname).first()
    if existing_admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Admin already exists")

    # Hash the admin's password before storing it
    hashed_password = hash_password(admin_create.password)

    # Create a new admin instance
    new_admin = Admin(
        adminname=admin_create.adminname,
        email=admin_create.email,
        password=hashed_password
    )

    # Add the new admin to the database
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    # Return AdminResponse with the registered admin details
    return schemas.admin_schema.AdminResponse(
        id=new_admin.id,
        adminname=new_admin.adminname,
        email=new_admin.email
    )


@router.post("/adminlogin/", response_model=AdminResponse)
def login_admin(admin_login: AdminLogin, db: Session = Depends(get_session)):
    # Retrieve the admin by adminname
    db_admin = db.query(Admin).filter(Admin.adminname == admin_login.adminname).first()
    if not db_admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    # Verify the password
    if not verify_password(admin_login.password, db_admin.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    # Admin authenticated successfully, return admin details as AdminResponse
    return AdminResponse(id=db_admin.id, adminname=db_admin.adminname, email=db_admin.email)


@router.get("/admins/", response_model=List[AdminResponse])
def get_all_admins(db: Session = Depends(get_session)):
    # Retrieve all admins from the database
    admins = db.query(Admin).all()
    return admins


@router.get("/admins/{admin_id}", response_model=AdminResponse)
def read_admin(admin_id: int, db: Session = Depends(get_session)):
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return db_admin



@router.delete("/admins/{admin_id}", response_model=AdminResponse)
def delete_admin(admin_id: int, db: Session = Depends(get_session)):
    # Retrieve the admin from the database
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    # Delete the admin from the database
    db.delete(db_admin)
    db.commit()

    # Return the deleted admin details as AdminResponse
    return db_admin