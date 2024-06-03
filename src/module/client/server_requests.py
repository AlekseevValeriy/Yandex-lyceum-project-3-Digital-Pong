from typing import Any

from requests import get, post, put, delete

URL = "http://127.0.0.1:8080"  # API


def template(request: str) -> str:
	return f"{URL}/{request}"


def simplification(response: Any) -> Any:
	return response if response != 0 else None


def token_all() -> list[str] | dict[str: str, str: int]:
	return get(template("get_tokens")).json()


def user_registration(username: str, password: str) -> dict[str: str, str: int] | None:
	return simplification(post(template(f"registration/{username}/{password}")).json())


def user_log(side: str, username: str, password: str) -> int | dict[str: str, str: int] | None:
	return simplification(post(template(f"log/{side}/{username}/{password}")).json())


def user_delete(username: str) -> dict[str: str, str: int] | None:
	return simplification(delete(template(f"delete_user/{username}")).json())


def room_all(is_open: bool, names: bool, user_limit: int, bots: bool) -> dict[str: list[int, list[str]]] | dict[str: str, str: int]:
	return get(template(f"get_rooms/{str(is_open)[0].lower()}/{str(names)[0].lower()}/{user_limit}/{str(bots)[0].lower()}")).json()


def room_create(user_id: str, bots: str, users_quantity: int, ball_radius: int, ball_speed: int, ball_boost: str,
				platform_speed: int, platform_height: int, platform_width: int) -> int | dict[str: str, str: int]:
	return post(template(f"/create_room/{user_id}/{bots}/{users_quantity}/{ball_radius}/{ball_speed}/{ball_boost}/{platform_speed}/{platform_height}/{platform_width}")).json()


def room_search(room_id: int) -> bool | dict[str: str, str: int]:
	return get(template(f"search_room/{room_id}")).json()


def room_user_ids(room_id: int) -> list[str] | dict[str: str, str: int]:
	return get(template(f"room_users/{room_id}")).json()


def room_user_ids_divine(room_id: int) -> dict[str: list[str]] | dict[str: str, str: int]:
	return get(template(f"room_users_divide/{room_id}")).json()


def room_delete(room_id: int) -> int | dict[str: str, str: int]:
	return simplification(delete(template(f"delete_room/{room_id}")).json())


def room_enter(room_id: int, user_id: int) -> dict[str: str, str: int] | None:
	return simplification(put(template(f"enter_room/{room_id}/{user_id}")).json())


def room_enter_field(room_id: int, user_id: int) -> dict[str: str, str: int] | None:
	return simplification(put(template(f"field_enter/{room_id}/{user_id}")).json())


def room_leave(user_id: int, ignore: str) -> dict[str: str, str: int] | None:
	return simplification(put(template(f"leave_room/{user_id}/{ignore}")).json())


def room_can_move(room_id: int) -> bool | dict[str: str, str: int]:
	return get(template(f"can_move/{room_id}")).json()


def room_move(room_id: int, user_id: int, platform_position_y: int) -> dict[str: str, str: int] | None:
	return simplification(put(template(f"move/{room_id}/{user_id}/{platform_position_y}")).json())


def testing() -> None:
	return simplification(get(template("testing")).json())


def user_side_change(user_id: int, side: str) -> dict[str: str, str: int] | None:
	return simplification(put(template(f"user_movement/{user_id}/{side}")).json())


def room_update_settings(user_id: int, bots: str, users_quantity: int, ball_radius: int, ball_speed: int, ball_boost: str, platform_speed: int, platform_height: int, platform_width: int) -> dict[str: str, str: int] | None:
	return simplification(put(template(f"set_room_settings/{user_id}/{bots}/{users_quantity}/{ball_radius}/{ball_speed}/{ball_boost}/{platform_speed}/{platform_height}/{platform_width}")).json())


def room_get_settings(user_id: int) -> dict[str: int | bool]:
	return get(template(f"get_room_settings/{user_id}")).json()


def room_can_enter(user_id: int) -> dict[str: str, str: int] | bool:
	return get(template(f"can_enter/{user_id}")).json()
