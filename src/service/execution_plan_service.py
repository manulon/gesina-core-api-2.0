from datetime import datetime

from sqlalchemy.orm import joinedload

from src.persistance.execution_plan import ExecutionPlan
from src.persistance.session import get_session
from src.service import file_storage_service


def create(request):
    flow_file = request.files["file"]
    flow_id = flow_file.filename
    form = request.form
    geometry_id = form["geometryOption"]
    user_id = 1  # hardcode
    execution_datetime = datetime.now()
    start_datetime = form["startDate"]
    end_datetime = form["endDate"]

    with get_session() as session:
        file_storage_service.save_flow(flow_file)
        # flow = Flow(id=flow_id)
        # session.add(flow)
        execution_plan = ExecutionPlan(
            flow_id=flow_id,
            geometry_id=geometry_id,
            user_id=user_id,
            execution_datetime=execution_datetime,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        session.add(execution_plan)
        return execution_plan


def get_execution_plans():
    execution_plans = []
    with get_session() as session:
        data = (
            session.query(ExecutionPlan)
            .options(joinedload(ExecutionPlan.user))
            .options(joinedload(ExecutionPlan.geometry))
            .all()
        )
        if data:
            execution_plans = data

    return execution_plans


def get_execution_plan(execution_plan_id):
    with get_session() as session:
        result = (
            session.query(ExecutionPlan)
            .options(joinedload(ExecutionPlan.user))
            .options(joinedload(ExecutionPlan.geometry))
            .get(execution_plan_id)
        )
        return result
