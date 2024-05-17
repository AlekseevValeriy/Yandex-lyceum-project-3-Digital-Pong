from flask import Flask, Response

from server_data import db_session
from server_data.user import User
from server_data.room import Room
from server_data.token import Token
from exceptions import *
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
@app.route('/get_rooms/<string:open>/<string:names>/<int:user_limit>', methods=["GET"])
@catch_error
def get_rooms(open: str = " ", names: str = " ", user_limit: int = 0) -> Response:
	rooms = db_session_app.query(Room)

	# open - игра не начата, можно войти
	if open not in [" ", 'f'] and open == 't':
		rooms = rooms.filter(Room.game_run == 0)

	if user_limit:
		rooms = rooms.filter(Room.user_limit == user_limit)

	# names - получать никнеймы вместо идентификаторов
	if names not in [" ", "f"] and names == 't':
		return jsonify(dict(map(lambda robj: (robj.id, (robj.user_limit, tuple(
			map(lambda uid: db_session_app.query(User).filter(User.id == uid).first().username,
				robj.user_ids.split(';'))))), rooms)))

	return jsonify(dict(map(lambda robj: (robj.id, (robj.user_limit, robj.user_ids.split(';'))), rooms)))


@app.route('/search_room/<int:room_id>', methods=["GET"])
@catch_error
def search_room(room_id: int) -> Response:
	return jsonify(bool(db_session_app.query(Room).filter(Room.id == int(room_id)).first()))


@app.route('/room_users/<int:room_id>', methods=["GET"])
@catch_error
def get_room_users(room_id: int) -> Response:
	room = db_session_app.query(Room).filter(Room.id == room_id).first()
	if not room: raise RoomNotExists
	return jsonify(room.user_ids.split(';'))


@app.route('/room_users_divide/<int:room_id>', methods=["GET"])
@catch_error
def get_room_users_divide(room_id: int) -> Response:
	room = db_session_app.query(Room).filter(Room.id == room_id).first()
	if not room: raise RoomNotExists
	return jsonify({"left": room.user_divide_left.split(';') if room.user_divide_left else [],
				   "right": room.user_divide_right.split(';') if room.user_divide_right else []})


@app.route('/user_movement/<int:user_id>/<string:side>', methods=["PUT"])
@catch_error
def user_movement(user_id: int, side: str) -> Response:
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists
	if not user.in_room: raise UserIsAlreadyInTheRoom

	room = db_session_app.query(Room).filter(Room.id == user.room_id).first()
	if not room: raise RoomNotExists

	sides = {'left': room.user_divide_left.split(';') if room.user_divide_left else [],
			 'right': room.user_divide_right.split(';') if room.user_divide_right else []}

	sides['left'] = list(filter(lambda a: a != str(user_id), sides['left']))
	sides['right'] = list(filter(lambda a: a != str(user_id), sides['right']))

	sides[side].append(user_id)
	room.user_divide_left = ';'.join(map(str, sides['left'])) if sides['left'] else ""
	room.user_divide_right = ';'.join(map(str, sides['right'])) if sides['right'] else ""

	db_session_app.add(room)
	db_session_app.commit()
	return jsonify(0)

def user_plus(user_ids: str, user_id: str) -> str:
	return ';'.join((*user_ids.split(';'), user_id)) if user_ids else user_id


def user_minus(user_ids: str, user_id: str) -> str:
	user_ids = user_ids.split(';')
	user_ids.remove(user_id)
	return ';'.join(user_ids)


@app.route('/create_room/<int:user_id>/<int:user_limit>', methods=["POST", "PUT", "GET"])
@catch_error
def create_room(user_id: str, user_limit: str) -> Response:
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists
	if user.in_room: raise UserIsAlreadyInTheRoom
	user.in_room = True
	user.role = 'host'
	db_session_app.add(user)
	room = Room()
	room.user_limit = user_limit
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
		users = room.user_ids.split(';')
		if len(users) >= room.user_limit: raise RoomUsersLimit
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists

	if user.in_room: raise UserIsAlreadyInTheRoom
	if str(user.id) in users: raise RoomUserAvailable
	users.append(user_id)
	user.in_room = True
	user.room_id = room.id
	user.role = 'player'
	db_session_app.add(user)
	if len(users) == room.user_limit:
		room.game_run = True
	users = list(map(str, users))
	room.user_ids = ';'.join(users)
	db_session_app.add(room)
	db_session_app.commit()
	return jsonify(0)


@app.route('/field_enter/<int:room_id>/<int:user_id>', methods=["PUT"])
@catch_error
def field_enter(room_id: int, user_id: int) -> Response:
	room = db_session_app.query(Room).filter(Room.id == room_id).first()
	if not room: raise RoomNotExists
	if not room.game_run: raise RoomPreparationContinue
	users = room.user_ids.split(';') if room.user_ids else []
	user = db_session_app.query(User).filter(User.id == user_id).first()
	if not user: raise UserNotExists
	if str(user.id) not in users: raise RoomUserMiss
	room.user_positions = ';'.join(
		(*room.user_positions.split(';'), f"{user_id}:0")) if room.user_positions else f"{user_id}:0"
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
	if user.role == 'host': raise UserCanTQuitHisTeam
	room = db_session_app.query(Room).filter(Room.id == user.room_id).first()

	if ignore:
		if user.role == 'host':
			for user_id in room.user_ids.split(';'):
				try:
					db_session_app.add(room_quit(user_id, get=True))
				except UserNotExists:
					continue
			db_session_app.delete(room)
		else:
			user_ids = room.user_ids.split(';')
			user_ids.remove(str(user_id))
			left = room.user_divide_left.split(';')
			if str(user_id) in left:
				left.remove(str(user_id))
			right = room.user_divide_right.split(';')
			if str(user_id) in right:
				right.remove(str(user_id))
			room.user_divide_left = ';'.join(left)
			room.user_divide_right = ';'.join(right)
			room_quit(user_id)
			db_session_app.add(user)
			if not user_ids:
				db_session_app.delete(room)
			else:
				room.user_ids = ';'.join(user_ids)
				room.game_run = False
				db_session_app.add(room)
	else:
		if not room: raise RoomNotExists
		if not room.user_ids: raise RoomUsersMiss
		if room.game_run: raise RoomPreparationEnd

		user_ids = room.user_ids.split(';')
		if str(user_id) not in user_ids: raise RoomUserMiss
		user_ids.remove(str(user_id))
		room_quit(user_id)
		db_session_app.add(user)
		if not user_ids:
			db_session_app.delete(room)
		else:
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
	if len(room.user_positions.split(';')) != room.user_limit: raise RoomUsersMiss
	return jsonify(True)


@app.route('/move/<int:room_id>/<int:user_id>/<string:platform_position_y>', methods=["PUT"])
@catch_error
def move(room_id: int, user_id: int, platform_position_y: str) -> Response:
	room = db_session_app.query(Room).filter(Room.id == room_id).first()
	if not room: raise RoomNotExists
	users = dict(map(lambda a: a.split(':'), room.user_positions.split(';')))
	users[str(user_id)] = platform_position_y
	room.user_positions = ';'.join(map(lambda a: ':'.join((a, users[a])), users))
	db_session_app.add(room)
	db_session_app.commit()
	return jsonify(0)


@app.route('/testing', methods=["GET"])
@catch_error
def testing() -> Response:
	return jsonify(0)


if __name__ == '__main__':
	app.run(port=8080, host='127.0.0.1', debug=True)
	logging.basicConfig(level=logging.WARNING)
