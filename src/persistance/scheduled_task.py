from datetime import datetime

from sqlalchemy import (
    Integer,
    Column,
    String,
    DateTime,
    JSON,
    Boolean,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import relationship

from src.persistance.session import Base


class ScheduledTask(Base):
    __tablename__ = "scheduled_task"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    frequency = Column(Integer)  # in minutes
    created_at = Column(DateTime, default=datetime.now)
    start_datetime = Column(DateTime)
    _metadata = Column("metadata", JSON)
    enabled = Column(Boolean)
    geometry_id = Column(Integer, ForeignKey("geometry.id"))
    geometry = relationship("Geometry", lazy="joined")
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", lazy="joined")
    start_condition_type = Column(String)
    observation_days = Column(Integer)
    forecast_days = Column(Integer)


class InitialFlow(Base):
    __tablename__ = "initial_flow"
    id = Column(Integer, primary_key=True)
    scheduled_task_id = Column(Integer, ForeignKey("scheduled_task.id"))
    scheduled_task = relationship("ScheduledTask", lazy="joined")
    river = Column(String)
    reach = Column(String)
    river_stat = Column(Float)
    flow = Column(Float)
