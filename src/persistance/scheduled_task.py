import enum
from datetime import datetime

from sqlalchemy import (
    Integer,
    Column,
    String,
    DateTime,
    JSON,
    Boolean,
    ForeignKey,
    Enum,
    PrimaryKeyConstraint,
    Numeric
)
from sqlalchemy.orm import (relationship, validates)

from src.persistance.session import Base
from src.service import file_storage_service


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
    initial_flows = relationship(
        "InitialFlow",
        lazy="joined",
        back_populates="scheduled_task",
        order_by="InitialFlow.id",
    )
    border_conditions = relationship(
        "BorderCondition",
        lazy="joined",
        back_populates="scheduled_task",
        order_by="BorderCondition.id",
    )
    plan_series_list = relationship(
        "PlanSeries",
        lazy="joined",
        back_populates="scheduled_task",
        order_by="PlanSeries.id",
    )
    calibration_id = Column(Integer)
    calibration_id_for_simulations = Column(Integer)

    def is_project_template_present(self):
        return file_storage_service.is_project_template_present(self.id)

    def is_plan_template_present(self):
        return file_storage_service.is_plan_template_present(self.id)

    def is_restart_file_present(self):
        return file_storage_service.is_restart_file_present(self.id)


class InitialFlow(Base):
    __tablename__ = "initial_flow"
    id = Column(Integer, primary_key=True)
    scheduled_task_id = Column(Integer, ForeignKey("scheduled_task.id"))
    scheduled_task = relationship("ScheduledTask", back_populates="initial_flows")
    river = Column(String)
    reach = Column(String)
    river_stat = Column(String)
    flow = Column(String)


class BorderConditionType(str, enum.Enum):
    STAGE_HYDROGRAPH = "Stage Hydrograph"
    FLOW_HYDROGRAPH = "Flow Hydrograph"
    LATERAL_INFLOW_HYDROGRAPH = "Lateral Inflow Hydrograph"

    @classmethod
    def choices(cls):
        return [(choice, str(choice)) for choice in cls]

    def __str__(self):
        return str(self.value)


class BorderCondition(Base):
    __tablename__ = "border_condition"
    id = Column(Integer, primary_key=True)
    scheduled_task_id = Column(Integer, ForeignKey("scheduled_task.id"))
    scheduled_task = relationship("ScheduledTask", back_populates="border_conditions")
    river = Column(String)
    reach = Column(String)
    river_stat = Column(String)
    interval = Column(String)
    type = Column(Enum(BorderConditionType))
    series_id = Column(Integer)


class PlanSeries(Base):
    __tablename__ = "plan_series"
    id = Column(Integer, primary_key=True)
    river = Column(String)
    reach = Column(String)
    river_stat = Column(String)
    stage_series_id = Column(Integer)
    flow_series_id = Column(Integer)
    scheduled_task = relationship("ScheduledTask", back_populates="plan_series_list")
    scheduled_task_id = Column(Integer, ForeignKey("scheduled_task.id"))
    stage_datum = Column(Numeric, default=None)


    @validates('stage_datum')
    def empty_string_to_null(self, key, value):
        if isinstance(value,str) and value == '':
            return None
        else:
            return value

class ExecutionPlanScheduleTaskMapping(Base):
    __tablename__ = "execution_plan_schedule_task_mapping"
    scheduled_task_id = Column(Integer, ForeignKey("scheduled_task.id"), primary_key=True)
    execution_id = Column(Integer, ForeignKey("execution_plan.id"), primary_key=True)
    __table_args__ = (
        PrimaryKeyConstraint('scheduled_task_id', 'execution_id'),
    )