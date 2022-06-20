from src.persistance.scheduled_task import ScheduledTask
from src.persistance.session import get_session


def update(_id, form):
    new_frequency = form.frequency.data
    new_enabled = form.schedule_config_enabled.data

    with get_session() as session:
        schedule_config = session.query(ScheduledTask).filter_by(id=_id).one_or_none()
        schedule_config.frequency = new_frequency
        schedule_config.enabled = new_enabled
        session.add(schedule_config)


def get_schedule_task_config():
    with get_session() as session:
        schedule_task_list = session.query(ScheduledTask).all()
        return schedule_task_list[0]
