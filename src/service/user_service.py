from flask_login import current_user

from src.login_manager import login_manager
from src.persistance import User
from src.persistance.session import get_session


def get_current_user():
    return current_user


def get_updated_user():
    return get_user(current_user.id)


@login_manager.user_loader
def get_user(user_id):
    with get_session() as session:
        return session.query(User).filter(User.id == user_id).first()


def get_users(limit):
    with get_session() as session:
        return session.query(User).limit(limit).all()


def get_all_users():
    with get_session() as session:
        return session.query(User).order_by(User.id.desc()).all()


def save(email, first_name, last_name, password):
    user = User(
        email=email, first_name=first_name, last_name=last_name, password=password, admin_role=True, active=True
    )
    with get_session() as session:
        session.add(user)

    return user


def get_user_by_email_and_password(email, password):
    with get_session() as session:
        user = session.query(User).filter(User.email == email).first()

    if user and user.check_password_hash(password):
        return user


def get_admin_user():
    with get_session() as session:
        return (
            session.query(User)
            .filter(User.first_name == "Admin", User.last_name == "Ina")
            .one()
        )


def enable_disable_user(user_id):
    user = get_user(user_id)
    user.active = not user.active
    with get_session() as session:
        session.add(user)

    return user
