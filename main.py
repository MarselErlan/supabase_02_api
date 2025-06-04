import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()
postgres_uri = os.getenv("POSTGRES_URI")


# SQLModel Engine
engine = create_engine(postgres_uri, echo=True)

# SQLModel Definition
class Item(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    price: float
    is_offer: bool = False

# Create Database and Tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Lifespan Event
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

# FastAPI App
app = FastAPI(
    title="Item Management API",
    description="A simple API to manage items in a Supabase PostgreSQL database.",
    version="1.0.0",
    lifespan=lifespan
)

# Dependency for Session Management
def get_session():
    with Session(engine) as session:
        yield session

# Endpoints
@app.post("/items", response_model=Item)
async def create_item(item: Item, session: Session = Depends(get_session)):
    try:
        session.add(item)
        session.commit()
        session.refresh(item)  # Refresh to get the database-generated ID
        return item
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create item: {str(e)}")

@app.get("/items", response_model=List[Item])
async def read_items(session: Session = Depends(get_session)):
    try:
        items = session.exec(select(Item)).all()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve items: {str(e)}")