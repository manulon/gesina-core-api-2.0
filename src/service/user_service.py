from src.persistance import User
from src.persistance.session import get_session


def current_user():
    return None


def save(**kwargs):
    user = User(**kwargs)
    with get_session() as session:
        session.add(user)

    return user
