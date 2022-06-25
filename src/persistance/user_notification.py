from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.persistance.session import Base


class UserNotification(Base):
    __tablename__ = "user_notification"
    id = Column(Integer, primary_key=True)
    seen = Column(Boolean, nullable=False, default=False)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User")

    execution_plan_id = Column(Integer, ForeignKey("execution_plan.id"))
    execution_plan = relationship("ExecutionPlan")
