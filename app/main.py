import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_database

from sqlmodel import SQLModel, create_engine, Session

from app.routes import user, product, cart, order, admin

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount the static directory to serve files
app.mount("/static", StaticFiles(directory=os.path.join(os.getcwd(), "static")), name="static")


app.include_router(user.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(admin.router)


@app.on_event("startup")
def startup_event():
    create_database()