from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: int
    email: EmailStr
    username: str
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str



class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr



class UserLogin(BaseModel):
    username: str
    password: str