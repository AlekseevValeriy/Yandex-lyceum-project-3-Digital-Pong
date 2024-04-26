import logging
from io import StringIO
import csv

from flask import Flask, jsonify, Response
from functools import wraps

from data import db_session
from data.user import User
from data.room import Room
from exceptions import *

app = Flask(__name__)

db_session.global_init("db/base.db")
db_session_app = db_session.create_session()


# decorator
def catch_error(function):
    @wraps(function)
    def data(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as error:
            logging.error(error.__class__.__name__)
            if issubclass(error.__class__, ResponseException):
                return jsonify(error.response)
            return jsonify({
                "status_code": 9999,
                "message": f'Неизвестная ошибка - {error.__class__.__name__};{format_exception(error)}'
            })

    return data


# user
@app.route('/registration/<string:username>/<string:password>')
@catch_error
def registration(username: str, password: str) -> Response:
    users = db_session_app.query(User).filter(User.username == username).first()
    if users: raise UserExists
    new_user = User()
    new_user.password = password
    new_user.username = username
    db_session_app.add(new_user)
    db_session_app.commit()
    return jsonify(0)


@app.route('/delete_user/<string:username>/<string:password>')
@catch_error
def delete_user(username: str, password: str) -> Response:
    user = db_session_app.query(User).filter(User.username == username, User.password == password).first()
    if not user: raise UserNotExists
    db_session_app.delete(user)
    return jsonify(0)


@app.route('/')
@app.route('/login/<string:username>/<string:password>')
@catch_error
def login(username: str, password: str) -> Response:
    user = db_session_app.query(User).filter(User.username == username, User.password == password).first()
    if not user: raise UserNotExists
    user.status = True
    db_session_app.add(user)
    db_session_app.commit()
    return jsonify(user.id)


@app.route('/gate/<int:user_id>/<int:where>')
@catch_error
def gate(user_id: int, where: int) -> Response:
    # TODO добавить отдельный ключ для каждого аккаунта
    user = db_session_app.query(User).filter(User.id == user_id).first()
    if not user: raise UserNotExists
    print(user.username)
    user.status = bool(where)
    db_session_app.add(user)
    db_session_app.commit()
    return jsonify(0)


# room
@app.route('/get_rooms')
@catch_error
def get_rooms() -> Response:
    return jsonify(
        dict(map(lambda r: (r.id, tuple(map(lambda u: db_session_app.query(User).filter(User.id == int(u.split(':')[0])
                                                                                        ).first().username,
                                            r.users.split(';') if r.users else ''))), db_session_app.query(Room))))


@app.route('/get_room_users/<int:room_id>')
@catch_error
def get_room_users(room_id: int) -> Response:
    room = db_session_app.query(Room).filter(Room.id == room_id).first()
    if not room: raise RoomNotExists
    return jsonify(room.users)


@app.route('/create_room/<int:user_id>/<int:user_limit>')
@catch_error
def create_room(user_id: int, user_limit: int) -> Response:
    user = db_session_app.query(User).filter(User.id == user_id).first()
    if not user: raise UserNotExists
    if user.in_room: raise UserIsAlreadyInTheRoom
    user.in_room = True
    db_session_app.add(user)
    room = Room()
    room.user_limit = user_limit
    room.game_run = False
    room.users = f"{user_id}:{0}"
    db_session_app.add(room)
    db_session_app.commit()
    room = db_session_app.query(Room).filter(Room.users == f"{user_id}:{0}").first()

    return jsonify(room.id)


@app.route('/delete_room/<int:room_id>')
@catch_error
def delete_room(room_id: int) -> Response:
    room = db_session_app.query(User).filter(Room.id == room_id).first()
    if not room: raise RoomNotExists
    for user_id in list(map(lambda u: u.split(':')[0], tuple(csv.reader(StringIO(room.users), delimiter=';'))[0])):
        try:
            user = db_session_app.query(User).filter(User.id == user_id).first()
            if not user: raise UserNotExists
            user.in_room = False
            db_session_app.add(user)
        except UserNotExists:
            continue
    db_session_app.delete(room)
    db_session_app.commit()
    return jsonify(0)


@app.route('/enter_room/<int:room_id>/<int:user_id>')
@catch_error
def enter_room(room_id: int, user_id: int) -> Response:
    room = db_session_app.query(Room).filter(Room.id == room_id).first()
    if not room: raise RoomNotExists
    if room.game_run: raise RoomPreparationEnd
    if not room.users:
        users = []
    else:
        users = tuple(csv.reader(StringIO(room.users), delimiter=';'))[0]
        if len(users) >= room.user_limit: raise RoomUsersLimit
    user = db_session_app.query(User).filter(User.id == user_id).first()
    if not user: raise UserNotExists

    if user.in_room: raise UserIsAlreadyInTheRoom
    if str(user.id) in users: raise RoomUserAvailable
    users.append(f"{user.id}:{0}")
    user.in_room = True
    db_session_app.add(user)
    if len(users) == room.user_limit:
        room.game_run = True
    users = tuple(dict(map(lambda i: (i, None), users)))
    room.users = ';'.join(users)
    db_session_app.add(room)
    db_session_app.commit()
    return jsonify(0)


@app.route('/leave_room/<int:room_id>/<int:user_id>')
@catch_error
def leave_room(room_id: int, user_id: int) -> Response:
    room = db_session_app.query(Room).filter(Room.id == room_id).first()
    if not room: raise RoomNotExists
    if not room.users: raise RoomUsersMiss
    users = tuple(csv.reader(StringIO(room.users), delimiter=';'))[0]
    users_id = list(map(lambda u: u.split(':')[0], users))
    if f"{user_id}:0" not in users_id: raise RoomUserMiss
    user_index = users_id.index(f"{user_id}:0")
    users.pop(user_index)
    user = db_session_app.query(User).filter(User.id == user_id).first()
    if not user: raise UserNotExists
    user.in_room = False
    db_session_app.add(user)
    if not users:
        db_session_app.delete(room)
    else:
        room.users = ';'.join(users)
        db_session_app.add(room)
    db_session_app.commit()
    return jsonify(0)


@app.route('/can_enter/<int:room_id>/<int:user_id>')
@catch_error
def can_enter(room_id: int, user_id: int) -> Response:
    room = db_session_app.query(Room).filter(Room.id == room_id).first()
    if not room: raise RoomNotExists
    if not room.users: raise RoomUsersMiss
    users = list(map(lambda u: u.split(':')[0], tuple(csv.reader(StringIO(room.users), delimiter=';'))[0]))
    if str(user_id) not in users: raise RoomUserMiss
    if len(users) != room.user_limit: raise RoomUsersMiss
    if not room.game_run:
        room.game_run = True
        db_session_app.add(room)
        db_session_app.commit()
    return jsonify(0)


@app.route('/can_move/<int:room_id>')
@catch_error
def can_move(room_id: int) -> Response:
    room = db_session_app.query(Room).filter(Room.id == room_id).first()
    if not room: raise RoomNotExists
    if not room.game_run: raise RoomPreparationContinue
    return jsonify(0)


@app.route('/move/<int:room_id>/<int:user_id>/<string:platform_position_y>')
@catch_error
def move(room_id: int, user_id: int, platform_position_y: str) -> Response:
    room = db_session_app.query(Room).filter(Room.id == room_id).first()
    if not room: raise RoomNotExists
    users = tuple(csv.reader(StringIO(room.users), delimiter=';'))[0]
    users_id = list(map(lambda u: u.split(':')[0], users))
    if str(user_id) not in users_id: raise RoomUserMiss
    users[users_id.index(str(user_id))] = ':'.join((str(user_id), platform_position_y))
    room.users = ';'.join(users)
    db_session_app.add(room)
    db_session_app.commit()
    return jsonify(0)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
    logging.basicConfig(level=logging.WARNING)
