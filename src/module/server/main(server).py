from json import load

from flask import Flask, Response
from waitress import serve

from server_data import db_session
from server_data.user import User
from server_data.room import Room
from server_data.token import Token
from exceptions import *
from src.module.server.server_data.db_session import SqlAlchemyBase
from token_work import TokenVerification, TokenCreate

app = Flask(__name__)
"""
http://127.0.0.1:8080
"""

db_session.global_init("../../../data/db/base.db")
db_session_app = db_session.create_session()


# token
def tokens() -> tuple:
	return tuple(map(lambda data: data.token, db_session_app.query(Token)))


@app.route('/get_tokens', methods=["GET"])
def get_tokens() -> Response:
	return jsonify(tokens())


# user
@app.route('/registration/<string:username>/<string:password>', methods=["POST"])
@catch_error
def registration(username: str, password: str) -> Response:
	if len(username) > 16: raise UsernameLengthLimit
	if not username.replace('_', "").isalpha(): raise UsernameInvalidCharacters
	if len(password) > 20: raise PasswordLengthLimit

	users = db_session_app.query(User).filter(User.username == username)
	if tuple(users):
		users = users.first()
		if users: raise UserExists

	user = User()
	user.password = password
	user.username = username
	db_session_app.add(user)

	token = Token()
	token.username = username
	token.token = TokenCreate.create('user', tokens())
	db_session_app.add(token)

	db_session_app.commit()
	return jsonify(0)


@app.route('/delete_user/<string:username>', methods=["DELETE"])
@catch_error
def delete_user(username: str) -> Response:
	user = db_session_app.query(User).filter(User.username == username).first()
	if not user: raise UserNotExists
	db_session_app.delete(user)
	token = db_session_app.query(Token).filter(Token.username == user.username).first()
	db_session_app.delete(token)
	db_session_app.commit()
	return jsonify(0)


@app.route('/log/<string:side>/<string:username>/<string:password>', methods=["GET", "POST"])
@catch_error
def log(side: str, username: str, password: str) -> Response:
	user = db_session_app.query(User).filter(User.username == username).first()
	if not user: raise UserNotExists
	if user.password != password: raise PasswordIncorrect
	match side:
		case 'in':
			side = True
			data = user.id
		case 'out':
			side = False
			data = 0
		case _:
			raise ValueError

	user.in_system = side
	db_session_app.add(user)
	db_session_app.commit()
	return jsonify(data)


def room_quit(user_id: int, commit: bool = False, get: bool = False) -> User | None:
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists
	user.in_room = False
	user.room_id = None
	user.role = None
	if commit:
		db_session_app.add(user)
		db_session_app.commit()
	if get:
		return user
	return None


# room
@app.route('/get_rooms/<string:open>/<string:names>/<int:user_limit>/<string:bots>', methods=["GET"])
@catch_error
def get_rooms(open: str = "f", names: str = "f", user_limit: int = 0, bots: str = 'f') -> Response:
	rooms = db_session_app.query(Room)

	# open - игра не начата, можно войти
	if open == 't':
		rooms = list(filter(lambda room: room.game_run == 0, rooms))

	if user_limit:
		rooms = list(filter(lambda room: room.users_quantity == user_limit, rooms))

	bots_status = True if bots == 't' else False
	rooms = list(filter(lambda room: room.bots == bots_status, rooms))

	def username(user_id: int):
		return db_session_app.query(User).filter(User.id == user_id).first().username

	# names - получать никнеймы вместо идентификаторов
	if names == 't':
		return jsonify(
			dict(map(lambda room: (room.id, (room.users_quantity, tuple(map(username, room.get_users)))), rooms)))
	else:
		return jsonify(dict(map(lambda room: (room.id, (room.users_quantity, room.get_users)), rooms)))


@app.route('/search_room/<int:room_id>', methods=["GET"])
@catch_error
def search_room(room_id: int) -> Response:
	return jsonify(bool(db_session_app.query(Room).filter(Room.id == room_id).first()))


@app.route('/room_users/<int:room_id>', methods=["GET"])
@catch_error
def get_room_users(room_id: int) -> Response:
	room = db_session_app.query(Room).filter(Room.id == room_id).first()
	if not room: raise RoomNotExists
	return jsonify(room.get_users)


def get_divide(room: Room) -> dict[str: list]:
	return {"left": room.get_divide('left'), "right": room.get_divide('right')}


@app.route('/room_users_divide/<int:room_id>', methods=["GET"])
@catch_error
def get_room_users_divide(room_id: int) -> Response:
	room = db_session_app.query(Room).filter(Room.id == room_id).first()
	if not room: raise RoomNotExists
	return jsonify(get_divide(room))


@app.route('/user_movement/<int:user_id>/<string:side>', methods=["PUT"])
@catch_error
def user_movement(user_id: int, side: str) -> Response:
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists
	if not user.in_room: raise UserIsAlreadyInTheRoom

	room = db_session_app.query(Room).filter(Room.id == user.room_id).first()
	if not room: raise RoomNotExists

	sides = get_divide(room)

	print(sides)

	sides['left'] = list(filter(lambda a: a != str(user_id) and a, sides['left']))
	sides['right'] = list(filter(lambda a: a != str(user_id) and a, sides['right']))
	print(sides)

	sides[side].append(user_id)

	print(sides)

	room.set_divide('left', sides['left'])
	room.set_divide('right', sides['right'])

	db_session_app.add(room)
	db_session_app.commit()
	return jsonify(0)


def user_plus(user_ids: str, user_id: str) -> str:
	return ';'.join((*user_ids.split(';'), user_id)) if user_ids else user_id


def user_minus(user_ids: str, user_id: str) -> str:
	user_ids = user_ids.split(';')
	user_ids.remove(user_id)
	return ';'.join(user_ids)


@app.route(
	'/create_room/<int:user_id>/<string:bots>/<int:users_quantity>/<int:ball_radius>/<int:ball_speed>/<string:ball_boost>/<int:platform_speed>/<int:platform_height>/<int:platform_width>',
	methods=["POST", "PUT", "GET"])
@catch_error
def create_room(user_id: int, bots: str, users_quantity: int, ball_radius: int, ball_speed: int, ball_boost: str,
				platform_speed: int, platform_height: int, platform_width: int) -> Response:
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists
	if user.in_room: raise UserIsAlreadyInTheRoom
	user.in_room = True
	user.role = 'host'
	db_session_app.add(user)
	room = Room()

	with open("../../../data/room_settings.json") as file:
		room_settings = load(file)

	room.bots = True if bots == 't' else False
	room.users_quantity = users_quantity if 0 < users_quantity < room_settings["users_quantity"]["data"][1] else room_settings["users_quantity"]["data"][0]
	room.ball_radius = ball_radius if 0 < ball_radius < room_settings["ball_radius"]["data"][1] else room_settings["ball_radius"]["data"][0]
	room.ball_speed = ball_speed if 0 < ball_speed < room_settings["ball_speed"]["data"][1] else room_settings["ball_speed"]["data"][0]
	room.ball_boost = float(ball_boost) if 9 < float(ball_boost) < room_settings["ball_boost"]["data"][1] else room_settings["ball_boost"]["data"][0]
	room.platform_speed = platform_speed if 0 < platform_speed < room_settings["platform_speed"]["data"][1] else room_settings["platform_speed"]["data"][0]
	room.platform_height = platform_height if 39 < platform_height < room_settings["platform_height"]["data"][1] else room_settings["platform_height"]["data"][0]
	room.platform_width = platform_width if 4 < platform_width < room_settings["platform_width"]["data"][1] else room_settings["platform_width"]["data"][0]

	room.user_ids = user_plus(room.user_ids, str(user_id))
	db_session_app.add(room)
	db_session_app.commit()
	room = db_session_app.query(Room).filter(Room.user_ids == user_id).first()
	user.room_id = room.id
	db_session_app.add(user)
	db_session_app.commit()

	return jsonify(room.id)


@app.route('/delete_room/<int:room_id>', methods=["DELETE"])
@catch_error
def delete_room(room_id: int) -> Response:
	room = db_session_app.query(Room).filter(Room.id == room_id).first()
	if not room: raise RoomNotExists
	for user_id in room.user_ids.split(';'):
		try:
			db_session_app.add(room_quit(user_id, get=True))
		except UserNotExists:
			continue
	db_session_app.delete(room)
	db_session_app.commit()
	return jsonify(0)


@app.route('/enter_room/<int:room_id>/<int:user_id>', methods=["PUT"])
@catch_error
def enter_room(room_id: int, user_id: int) -> Response:
	room = db_session_app.query(Room).filter(Room.id == room_id).first()
	if not room: raise RoomNotExists
	if room.game_run: raise RoomPreparationEnd
	if not room.user_ids:
		users = []
	else:
		users = room.get_users
		if len(users) >= room.users_quantity: raise RoomUsersLimit
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists

	if user.in_room: raise UserIsAlreadyInTheRoom
	if str(user.id) in users: raise RoomUserAvailable
	users.append(user_id)
	user.in_room = True
	user.room_id = room.id
	user.role = 'player'
	db_session_app.add(user)
	if len(users) == room.users_quantity:
		room.game_run = True
	users = list(map(str, users))
	room.set_users(users)
	db_session_app.add(room)
	db_session_app.commit()
	return jsonify(0)


@app.route('/field_enter/<int:room_id>/<int:user_id>', methods=["PUT"])
@catch_error
def field_enter(room_id: int, user_id: int) -> Response:
	room = db_session_app.query(Room).filter(Room.id == room_id).first()
	if not room: raise RoomNotExists
	if not room.game_run: raise RoomPreparationContinue
	users = room.get_users
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists

	if not room.can_enter:
		if user.role == "host":
			room.can_enter = True
		elif user.role == "player":
			raise UserCanTFieldEnter

	if str(user.id) not in users: raise RoomUserMiss
	if room.positions:
		room.positions = ';'.join((*room.user_positions.split(';'), f"{user_id}:0"))
	else:
		room.positions = f"{user_id}:0"
	db_session_app.add(room)
	db_session_app.commit()
	return jsonify(0)


@app.route('/leave_room/<int:user_id>/<string:ignore>', methods=["PUT"])
@catch_error
def leave_room(user_id: int, ignore: str) -> Response:
	if ignore not in ('t', 'f'): raise ValueError
	ignore = True if ignore == 't' else False
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists
	if not user.room_id: raise UserNotInTheRoom
	room = db_session_app.query(Room).filter(Room.id == user.room_id).first()

	if ignore:
		if user.host:
			for user_id in room.get_users:
				try:
					db_session_app.add(room_quit(user_id, get=True))
				except UserNotExists:
					continue
			db_session_app.delete(room)
		else:
			user_ids = room.get_users
			user_ids.remove(str(user_id))
			if not user_ids:
				db_session_app.delete(room)
			else:
				left = room.get_divide('left')
				if str(user_id) in left:
					left.remove(str(user_id))
				right = room.get_divide('right')
				if str(user_id) in right:
					right.remove(str(user_id))
				room.set_divide('left', left)
				room.set_divide('right', right)
				room_quit(user_id)
				db_session_app.add(user)
				room.set_users(user_ids)
				room.game_run = False
				positions = ';'.join(filter(lambda a: a.split(':')[0] != str(user_id), room.positions.split(';'))) if room.positions else ""
				room.positions = positions
				db_session_app.add(room)
	else:
		if not room: raise RoomNotExists
		if not room.user_ids: raise RoomUsersMiss
		if user.host: raise UserCanTQuitHisTeam
		if room.game_run: raise RoomPreparationEnd

		user_ids = room.get_users
		if str(user_id) not in user_ids: raise RoomUserMiss
		user_ids.remove(str(user_id))
		room_quit(user_id)
		db_session_app.add(user)
		if not user_ids:
			db_session_app.delete(room)
		else:
			room.set_users(user_ids)
			room.user_ids = ';'.join(user_ids)
			db_session_app.add(room)
	db_session_app.commit()
	return jsonify(0)


@app.route('/can_move/<int:room_id>', methods=["GET"])
@catch_error
def can_move(room_id: int) -> Response:
	room = db_session_app.query(Room).filter(Room.id == room_id).first()
	if not room: raise RoomNotExists
	if not room.game_run: raise RoomPreparationContinue
	if room.user_positions_quantity != room.users_quantity: raise RoomUsersMiss
	return jsonify(True)


@app.route('/can_enter/<int:user_id>', methods=["GET"])
@catch_error
def can_enter(user_id: int) -> Response:
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists
	room = db_session_app.query(Room).filter(Room.id == user.room_id).first()
	if not room: raise RoomNotExists
	return jsonify(room.can_enter)


@app.route('/move/<int:room_id>/<int:user_id>/<string:platform_position_y>', methods=["PUT"])
@catch_error
def move(room_id: int, user_id: int, platform_position_y: str) -> Response:
	room = db_session_app.query(Room).filter(Room.id == room_id).first()
	if not room: raise RoomNotExists
	users = dict(map(lambda a: a.split(':'), room.positions.split(';')))
	users[str(user_id)] = platform_position_y
	room.positions = ';'.join(map(lambda a: ':'.join((a, users[a])), users))
	db_session_app.add(room)
	db_session_app.commit()
	return jsonify(0)


@app.route('/get_room_settings/<int:user_id>', methods=["GET"])
@catch_error
def get_room_settings(user_id: int) -> Response:
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists
	room = db_session_app.query(Room).filter(Room.id == user.room_id).first()
	if not room: raise RoomNotExists
	return jsonify({
		"bots": room.bots,
		"users_quantity": room.users_quantity,
		"ball_radius": room.ball_radius,
		"ball_speed": room.ball_speed,
		"ball_boost": room.ball_boost,
		"platform_speed": room.platform_speed,
		"platform_height": room.platform_height,
		"platform_width": room.platform_width
	})


@app.route('/set_room_settings/<int:user_id>/<string:bots>/<int:users_quantity>/<int:ball_radius>/<int:ball_speed>/<string:ball_boost>/<int:platform_speed>/<int:platform_height>/<int:platform_width>', methods=["PUT"])
@catch_error
def set_room_settings(user_id: int, bots: str, users_quantity: int, ball_radius: int, ball_speed: int, ball_boost: str,
					  platform_speed: int, platform_height: int, platform_width: int) -> Response:
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists
	room = db_session_app.query(Room).filter(Room.id == user.room_id).first()
	if not room: raise RoomNotExists
	room.bots = bots
	room.users_quantity = users_quantity
	room.ball_radius = ball_radius
	room.ball_speed = ball_speed
	room.ball_boost = ball_boost
	room.platform_speed = platform_speed
	room.platform_height = platform_height
	room.platform_width = platform_width
	db_session_app.add(room)
	db_session_app.commit()
	return jsonify(0)


@app.route('/testing', methods=["GET"])
@catch_error
def testing() -> Response:
	return jsonify(0)


if __name__ == '__main__':
	serve(app, port=8080, host='127.0.0.1')
	logging.basicConfig(level=logging.WARNING)
