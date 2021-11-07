from sqlalchemy import (
    Integer,
    Column,
)
from src.persistance.session import Base


class Flow(Base):
    __tablename__ = "flow"
    id = Column(Integer, primary_key=True)
