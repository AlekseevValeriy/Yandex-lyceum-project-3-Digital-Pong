from sqlalchemy import Column, String, Integer, Boolean
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    status = Column(Boolean, nullable=False, default=False)
    in_room = Column(Boolean, nullable=False, default=False)
