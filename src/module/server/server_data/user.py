from sqlalchemy import Column, String, Integer, Boolean
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    in_system = Column(Boolean, nullable=False, default=False)
    in_room = Column(Boolean, nullable=False, default=False)
    room_id = Column(Integer, nullable=True)
    role = Column(String, nullable=True)
