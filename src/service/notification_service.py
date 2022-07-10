from src.persistance.session import get_session
from src.persistance.user_notification import UserNotification


def post_notification(execution_id, user_id):
    notification = UserNotification(user_id=user_id, execution_plan_id=execution_id)
    with get_session() as session:
        session.add(notification)
    return notification


def get_notifications_for_user(user_id):
    with get_session() as session:
        notifications = (
            session.query(UserNotification).filter_by(user_id=user_id, seen=False).all()
        )
    return notifications


def mark_notification_as_read(notification_id):
    with get_session() as session:
        notification = (
            session.query(UserNotification)
            .filter_by(id=notification_id)
            .one_or_none()
        )
        if not notification:
            return None
        notification.seen = True
        session.add(notification)
    return notification
