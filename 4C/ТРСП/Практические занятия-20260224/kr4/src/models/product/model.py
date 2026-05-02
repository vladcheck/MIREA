from typing import Any

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base: Any = declarative_base()

class Product(Base):
    __tablename__: str = "products"

    id: Column[int] = Column(Integer, primary_key=True, index=True)
    title: Column[str] = Column(String, index=True)
    price = Column(Float)
    count: Column[int] = Column(Integer)
    description: Column[str] = Column(String, nullable=False, server_default="No description")
