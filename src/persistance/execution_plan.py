from sqlalchemy import (
    Integer,
    Column,
    ForeignKey,
    String,
    DateTime,
)
from sqlalchemy.orm import relationship
from src.persistance.session import Base


class ExecutionPlan(Base):
    __tablename__ = "execution_plan"
    id = Column(Integer, primary_key=True)
    geometry_id = Column(Integer, ForeignKey("geometry.id"))
    geometry = relationship("Geometry")
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User")
    flow_id = Column(Integer, ForeignKey("flow.id"))
    flow = relationship("Flow")
    start_datetime = Column(DateTime)
    end_datetime = Column(DateTime)
    status = Column(String)
