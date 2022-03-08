from sqlalchemy import Integer, Column, String, DateTime, JSON, Boolean
from src.persistance.session import Base


class ScheduledTask(Base):
    __tablename__ = "scheduled_task"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    frequency = Column(Integer)  # in minutes
    created_at = Column(DateTime)
    start_datetime = Column(DateTime)
    _metadata = Column("metadata", JSON)
    enabled = Column(Boolean)
