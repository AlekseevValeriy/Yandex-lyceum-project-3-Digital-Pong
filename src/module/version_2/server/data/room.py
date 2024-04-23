from sqlalchemy import Column, String, Integer, Boolean
from .db_session import SqlAlchemyBase


class Room(SqlAlchemyBase):
    __tablename__ = 'room'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    game_run = Column(Boolean, nullable=False, default=False)
    user_limit = Column(Integer, nullable=False, default=1)
    users = Column(String, nullable=True)
    balls = Column(String, nullable=True)