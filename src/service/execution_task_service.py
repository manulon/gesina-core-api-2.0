from src.persistance.execution_task import ExecutionTask
from src.persistance.session import get_session
from sqlalchemy import and_

def save_task_id_in_database(execution_id, task_id):
    execution_task = ExecutionTask(execution_id=execution_id, task_id=task_id)
    with get_session() as session:
        session.add(execution_task)
        session.commit()

def get_task_id_by_execution_id(execution_id):
    with get_session() as session:
        execution_task = session.query(ExecutionTask).filter_by(execution_id=execution_id).first()

    return execution_task.task_id if execution_task else None
