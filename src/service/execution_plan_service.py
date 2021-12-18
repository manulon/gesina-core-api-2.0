from sqlalchemy.orm import joinedload

from src.persistance.execution_plan import ExecutionPlan
from src.persistance.session import get_session


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
