from sqlalchemy import (
    Integer,
    Column,
    create_engine,
    ForeignKey,
    String,
    DateTime,
    MetaData,
)
from sqlalchemy.orm import relationship, joinedload, subqueryload, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import os

Base = declarative_base(metadata=MetaData(schema="gesina"))

user = os.getenv("DATABASE_USER", "user")
password = os.getenv("DATABASE_PASSWORD", "password")
database_name = os.getenv("DATABASE_NAME", "main")
database_host = os.getenv("DATABASE_HOST", "localhost:5432")

engine = create_engine(f"postgresql://{user}:{password}@{database_host}/{database_name}")


@contextmanager
def get_session():
    session = Session(expire_on_commit=False)
    try:
        yield session
        session.commit()
        session.expunge_all()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# class Geometry(Base):
#     __tablename__ = "geometry"
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     description = Column(String)
#     created_at = Column(DateTime)
#     user_id = Column(Integer, ForeignKey('user.id'))
#     user = relationship("User")


class Flow(Base):
    __tablename__ = "flow"
    id = Column(Integer, primary_key=True)


if __name__ == "__main__":
    with get_session() as session:
        session.add(Flow())
