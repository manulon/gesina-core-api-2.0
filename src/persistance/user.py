import flask_login
from sqlalchemy import (
    Integer,
    Column,
    String,
)
from werkzeug.security import generate_password_hash, check_password_hash

from src.persistance.session import Base


class User(Base, flask_login.UserMixin):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    _password = Column("password", String)
    session_id = Column(String)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password_hash(self, password_to_validate):
        return check_password_hash(self.password, password_to_validate)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name
