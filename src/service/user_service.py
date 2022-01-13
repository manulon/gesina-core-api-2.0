from src.login_manager import login_manager
from src.persistance import User
from src.persistance.session import get_session


def current_user():
    return get_user(1)


@login_manager.user_loader
def get_user(user_id):
    with get_session() as session:
        return session.query(User).filter(User.id == user_id).first()


def save(**kwargs):
    user = User(**kwargs)
    with get_session() as session:
        session.add(user)

    return user


def get_user_by_email_and_password(email, password):
    with get_session() as session:
        user = session.query(User).filter(User.email == email).first()

    if user and user.check_password_hash(password):
        return user
