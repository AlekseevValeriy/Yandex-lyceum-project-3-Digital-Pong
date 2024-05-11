from json import load, dump
from csv import reader
from os.path import join

DATA = "../../../data"
USER_DATA = join(DATA, "user_data.json")
SETTINGS = join(DATA, "settings.json")
THEMES = join(DATA, "theme_colors.csv")
MENU_DATA = join(DATA, "room_settings.json")


def translate(file_name: str) -> str:
	match file_name:
		case "data":
			return USER_DATA
		case "settings":
			return SETTINGS
		case "menu":
			return MENU_DATA


def download(file: str) -> dict:
	with open(translate(file), 'r', encoding='utf-8') as file:
		return load(file)


def upload(file: str, data: dict) -> None:
	with open(translate(file), 'w', encoding='utf-8') as file:
		dump(data, file, ensure_ascii=False)


def download_themes() -> tuple:
	with open(THEMES, 'r', encoding='utf-8') as file:
		return tuple(reader(file, delimiter=","))[0]


def download_menu() -> dict[str: tuple]:
	with open(MENU_DATA, 'r', encoding='utf-8') as file:
		data = load(file)
		for value in data:
			match data[value]["interval"]:
				case False: data[value] = data[value]['data']
				case True: data[value] = [*range(data[value]['data'][0], data[value]['data'][1])]
			data[value] = tuple(data[value])
	return data
