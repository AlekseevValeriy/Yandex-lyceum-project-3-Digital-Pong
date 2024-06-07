from sqlalchemy import Column, String, Integer, Boolean, Float
from .db_session import SqlAlchemyBase


# class Room(SqlAlchemyBase):
# 	__tablename__ = 'room'
# 	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
# 	user_limit = Column(Integer, nullable=False, default=1)
# 	user_ids = Column(String, nullable=True)
# 	user_divide_left = Column(String, nullable=True)
# 	user_divide_right = Column(String, nullable=True)
#
# 	# bots - 0; users_quantity - 1; ball_radius - 2; ball_speed - 3;
# 	# ball_boost - 4; platform_speed - 5; platform_height - 6; platform_width - 7
# 	parameters = Column(String, nullable=False, default="0:True;1:1;2:1;3:1;4:1.0;5:1;6:40;7:5")
# 	game_run = Column(Boolean, nullable=False, default=False)
# 	user_positions = Column(String, nullable=True)
# 	ball_positions = Column(String, nullable=True)


class Room(SqlAlchemyBase):
	__tablename__ = 'room'
	id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
	user_ids = Column(String, nullable=True)
	user_divide_left = Column(String, nullable=True)
	user_divide_right = Column(String, nullable=True)
	bots = Column(Boolean, nullable=False, default=False)
	users_quantity = Column(Integer, nullable=False, default=1)
	ball_radius = Column(Integer, nullable=False, default=1)
	ball_speed = Column(Integer, nullable=False, default=1)
	ball_boost = Column(Float, nullable=False, default=1.0)
	platform_speed = Column(Integer, nullable=False, default=1)
	platform_height = Column(Integer, nullable=False, default=40)
	platform_width = Column(Integer, nullable=False, default=5)
	game_run = Column(Boolean, nullable=False, default=False)
	can_enter = Column(Boolean, nullable=False, default=False)
	positions = Column(String, nullable=True)
	score = Column(String, nullable=False, default="0;0")

	def get_divide(self, side: str) -> list:
		match side:
			case "left":
				return self.user_divide_left.split(';') if self.user_divide_left else []
			case "right":
				return self.user_divide_right.split(';') if self.user_divide_right else []

	def set_divide(self, side: str, users: list[str | int]) -> None:
		match side:
			case "left":
				self.user_divide_left = ";".join(map(str, users)) if users else ""
			case "right":
				self.user_divide_right = ";".join(map(str, users)) if users else ""

	@property
	def get_users(self) -> list[str]:
		return self.user_ids.split(';') if self.user_ids else []

	def set_users(self, users: list[str | int]) -> None:
		self.user_ids = ";".join(map(str, users)) if users else ""

	@property
	def string_parameters(self) -> str:
		return ";".join(map(str, self.list_parameters))

	@property
	def list_parameters(self) -> list[int | bool]:
		return [self.bots,
				self.users_quantity,
				self.ball_radius,
				self.ball_speed,
				self.ball_boost,
				self.platform_speed,
				self.platform_height,
				self.platform_width]

	@property
	def dict_parameters(self) -> dict[str: int | bool]:
		return dict(zip(["bots",
						 "users_quantity",
						 "ball_radius",
						 "ball_speed",
						 "ball_boost",
						 "platform_speed",
						 "platform_height",
						 "platform_width"
						 ], self.list_parameters))

	@property
	def user_positions_quantity(self) -> int:
		return len(tuple(filter(lambda obj: not obj.startswith('b_'), self.positions.split(';')))) if self.positions else 0

	@property
	def dict_score(self) -> dict[str: str]:
		return dict(zip(('left', 'right'), self.score.split(';')))

	def set_score(self, left_score: int | str, right_score: int | str) -> None:
		self.score = f"{left_score};{right_score}"
