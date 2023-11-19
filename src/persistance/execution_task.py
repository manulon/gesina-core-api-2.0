from sqlalchemy import Column, String, Integer
from src.persistance.session import Base

Base = declarative_base()

class ExecutionTask(Base):
    __tablename__ = 'execution_tasks'

    execution_id = Column(Integer, primary_key=True)
    task_id = Column(String, nullable=False)
