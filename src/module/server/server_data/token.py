from sqlalchemy import Column, String
from .db_session import SqlAlchemyBase


class Token(SqlAlchemyBase):
    __tablename__ = 'token'
    username = Column(String, primary_key=True, nullable=False)
    token = Column(String, nullable=False)
