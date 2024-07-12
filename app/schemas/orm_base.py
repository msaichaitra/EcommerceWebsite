from sqlmodel import SQLModel

class ORMBase(SQLModel):
    class Config:
        orm_mode = True