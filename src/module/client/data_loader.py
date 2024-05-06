from json import load, dump
from csv import reader
from os.path import join

DATA = "../../../data"
USER_DATA = join(DATA, "user_data.json")
SETTINGS = join(DATA, "settings.json")
THEMES = join(DATA, "theme_colors.csv")


def translate(file_name: str) -> str:
    match file_name:
        case "data":
            return USER_DATA
        case "settings":
            return SETTINGS


def download(file: str) -> dict:
    with open(translate(file), 'r', encoding='utf-8') as file:
        return load(file)


def upload(file: str, data: dict) -> None:
    with open(translate(file), 'w', encoding='utf-8') as file:
        dump(data, file, ensure_ascii=False)


def download_themes() -> tuple:
    with open(THEMES, 'r', encoding='utf-8') as file:
        return tuple(reader(file, delimiter=","))[0]
