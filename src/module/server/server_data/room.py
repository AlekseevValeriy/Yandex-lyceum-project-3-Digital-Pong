from sqlalchemy import Column, String, Integer, Boolean
from .db_session import SqlAlchemyBase


class Room(SqlAlchemyBase):
	__tablename__ = 'room'
	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	user_limit = Column(Integer, nullable=False, default=1)
	user_ids = Column(String, nullable=True)
	user_divide_left = Column(String, nullable=True)
	user_divide_right = Column(String, nullable=True)
	# bots - 0; users_quantity - 1; ball_radius - 2; ball_speed - 3;
	# ball_boost - 4; platform_speed - 5; platform_height - 6; platform_width - 7
	parameters = Column(String, nullable=False, default="0:True;1:1;2:1;3:1;4:1.0;5:1;6:40;7:5")
	game_run = Column(Boolean, nullable=False, default=False)
	user_positions = Column(String, nullable=True)
	ball_positions = Column(String, nullable=True)
