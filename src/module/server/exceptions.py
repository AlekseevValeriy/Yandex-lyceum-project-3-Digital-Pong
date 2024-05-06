from traceback import format_exception
from functools import wraps
from flask import jsonify
import logging


def catch_error(function):
    @wraps(function)
    def data(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except ResponseException as error:
            logging.error(error.__class__.__name__)
            if issubclass(error.__class__, ResponseException):
                return jsonify(error.response)
            return jsonify({
                "status_code": 9999,
                "message": f'Неизвестная ошибка - {error.__class__.__name__};{format_exception(error)}'
            })

    return data


class ResponseException(Exception):
    status_code: int = 0
    message: str = ""

    def __init__(self, status_code: int = 0, message: str = "no problem") -> None:
        if (status_code != 0) or (not self.status_code):
            self.status_code = status_code
        if (message != "no problem") or (not self.message):
            self.message = message

    @property
    def response(self):
        return {
            "status_code": self.status_code,
            "message": self.message
        }


class UsernameException(ResponseException):
    status_code, message = 11, "Ошибка имени пользователя"


class UsernameLengthLimit(UsernameException):
    status_code, message = 111, "Неверный размер имени"


class UsernameInvalidCharacters(UsernameException):
    status_code, message = 112, "Неверные символы в имени"


class PasswordException(ResponseException):
    status_code, message = 12, "Ошибка в пароле пользователя"


class PasswordLengthLimit(PasswordException):
    status_code, message = 121, "Неверный размер пароля"


class PasswordInvalidCharacters(PasswordException):
    status_code, message = 122, "Неверные символы в пароле"


class UserException(ResponseException):
    status_code, message = 13, "Ошибка пользователя"


class UserExists(UserException):
    status_code, message = 131, "Пользователь уже существует"


class UserNotExists(UserException):
    status_code, message = 132, "Пользователь не существует"


class UserIsAlreadyInTheRoom(UserException):
    status_code, message = 133, "Пользователь уже находится в комнате"


class UserCanTQuitHisTeam(UserException):
    status_code, message = 133, "Нельзя покинуть команду если вы хост"


class RoomException(ResponseException):
    status_code, message = 14, "Ошибка комнаты"


class RoomExists(RoomException):
    status_code, message = 141, "Комната уже существует"


class RoomNotExists(RoomException):
    status_code, message = 142, "Комната не существует"


class RoomUsersLimit(RoomException):
    status_code, message = 143, "Количество пользователей достигло лимита"


class RoomUsersMiss(RoomException):
    status_code, message = 144, "Количество пользователей достигло нуля"


class RoomUserMiss(RoomException):
    status_code, message = 145, "Обратное наличие пользователя в комнате"


class RoomUserAvailable(RoomException):
    status_code, message = 146, "Пользователь уже имеется в комнате"


class RoomPreparationEnd(RoomException):
    status_code, message = 147, "Подготовка к игре в комнате закончилась"


class RoomPreparationContinue(RoomException):
    status_code, message = 147, "Подготовка к игре в комнате продолжается"


class RightsIssue(ResponseException):
    status_code, message = 15, "Недостаточно прав"
