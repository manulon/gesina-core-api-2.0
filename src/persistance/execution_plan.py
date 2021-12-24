from sqlalchemy import (
    Integer,
    Column,
    ForeignKey,
    Enum,
    DateTime, String,
)
import enum
from sqlalchemy.orm import relationship
from src.persistance.session import Base


class ExecutionPlanStatus(enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    CANCELED = "CANCELED"
    ERROR = "ERROR"


class ExecutionPlan(Base):
    __tablename__ = "execution_plan"
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_name = Column(String)
    geometry_id = Column(Integer, ForeignKey("geometry.id"))
    geometry = relationship("Geometry")
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User")
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    created_at = Column(DateTime)
    status = Column(Enum(ExecutionPlanStatus))
