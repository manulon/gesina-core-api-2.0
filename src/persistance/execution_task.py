from sqlalchemy import (
    Integer,
    Column,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship
from src.persistance.session import Base

class ExecutionTask(Base):
    __tablename__ = 'execution_task'
    id = Column(Integer, primary_key=True)
    execution_id = Column(Integer, ForeignKey("execution_plan.id"))
    task_id = Column(String, nullable=False)