from datetime import datetime

from sqlalchemy import (
    Integer,
    Column,
    ForeignKey,
    Enum,
    DateTime,
    String,
)
import enum
from sqlalchemy.orm import relationship
from src.persistance.session import Base


class ExecutionPlanStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    CANCELED = "CANCELED"
    ERROR = "ERROR"


class ExecutionPlan(Base):
    __tablename__ = "execution_plan"
    id = Column(Integer, primary_key=True)
    plan_name = Column(String)
    geometry_id = Column(Integer, ForeignKey("geometry.id"))
    geometry = relationship("Geometry", lazy="joined")
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", lazy="joined")
    start_datetime = Column(DateTime, default=datetime.now)
    end_datetime = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(Enum(ExecutionPlanStatus), default=ExecutionPlanStatus.PENDING)
    execution_plan_output_list = relationship(
        "ExecutionPlanOutput", lazy="joined", back_populates="execution_plan", cascade="all, delete, delete-orphan"
    )

    def get_geometry_file_url(self):
        # TODO recuperar desde la carpeta del exe_plan
        if self.id:
            return ""
        return ""

    def get_flow_file_url(self):
        # TODO recuperar desde la carpeta del exe_plan
        if self.id:
            return ""
        return ""

    def to_dict(self):
        # Create a dictionary containing the object's attributes

        execution_output_list = [{"river": i.river,
                                  "river_stat": i.river_stat,
                                  "reach": i.reach}
                                 for i in self.execution_plan_output_list
                                 ]

        attributes = {
            "id": self.id,
            "plan_name": self.plan_name,
            "geometry_id": self.geometry_id,
            "geometry": str(self.geometry),
            "user_id": self.user_id,
            "start_datetime": str(self.start_datetime),
            "end_datetime": str(self.end_datetime),
            "created_at": str(self.created_at),
            "status": self.status.value if self.status else None,
            "execution_output_list": execution_output_list
            # Include other attributes as needed
        }

        return attributes

class ExecutionPlanOutput(Base):
    __tablename__ = "execution_plan_output"
    river = Column(String, primary_key=True)
    reach = Column(String, primary_key=True)
    river_stat = Column(String, primary_key=True)
    execution_plan_id = Column(
        Integer, ForeignKey("execution_plan.id"), primary_key=True
    )
    execution_plan = relationship(
        "ExecutionPlan", back_populates="execution_plan_output_list"
    )
    stage_series_id = Column(Integer)
    flow_series_id = Column(Integer)
