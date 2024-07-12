from sqlmodel import SQLModel, create_engine, Session


#Define the database URL (SQLite in this case)
DATABASE_URL = "sqlite:///./app.db"

#Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

def create_database():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
