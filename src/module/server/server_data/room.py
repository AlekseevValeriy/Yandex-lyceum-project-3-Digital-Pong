from sqlalchemy import Column, String, Integer, Boolean
from .db_session import SqlAlchemyBase


class Room(SqlAlchemyBase):
    __tablename__ = 'room'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_limit = Column(Integer, nullable=False, default=1)
    user_ids = Column(String, nullable=True)
    game_run = Column(Boolean, nullable=False, default=False)
    user_positions = Column(String, nullable=True)
    ball_positions = Column(String, nullable=True)
