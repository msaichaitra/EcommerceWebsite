from pydantic import BaseModel, EmailStr


class AdminBase(BaseModel):
    id: int
    email: EmailStr
    adminname: str
    password: str

class AdminCreate(BaseModel):
    email: EmailStr
    adminname: str
    password: str



class AdminResponse(BaseModel):
    id: int
    adminname: str
    email: EmailStr



class AdminLogin(BaseModel):
    adminname: str
    password: str