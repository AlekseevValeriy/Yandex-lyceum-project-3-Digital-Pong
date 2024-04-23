import csv
import requests
import json

import asynckivy
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.utils import platform
from kivy.core.window import Window
from kivy.config import Config
from kivy.core.window import Window

from tkinter import Tk
from icecream import ic
from screeninfo import get_monitors

from src.module.version_2.client.data import PlayerItem, BattleSettings
from src.module.version_2.client.widgets.player_item import PlayerItem
from src.module.version_2.client.widgets.item_box import ItemBox
from src.module.version_2.client.widgets.battle_field_layout import BattleField
from src.module.version_2.client.widgets.platform import Platform
from src.module.version_2.client.widgets.ball import Ball
from src.module.version_2.client.widgets.search_room_field import SearchRoomField


# design time values
current_color = 0


class DigitalPong(MDApp):
    # api of the server
    API = "http://127.0.0.1:8080"
    with open('../../../../data/player_data.json') as user_data_file:
        USER_DATA = json.load(user_data_file)
    # path to the structure .kv file
    STRUCTURE = "../../../../data/structure_stable.kv"  # "../../../../data/structure.kv"

    # design data

    with open('../../../../data/theme_colors.csv', 'r', encoding='utf8') as tc_file:
        THEME_COLORS = tuple(csv.reader(tc_file, delimiter=","))[0]
    CURRENT_COLOR = current_color

    def __init__(self, **kwargs) -> None:
        super(DigitalPong, self).__init__(**kwargs)

        self.builder = Builder.load_file(self.STRUCTURE)

        self.window_size = self.screen_settings()

    def build(self) -> Builder:
        return self.builder

    def on_start(self):
        super().on_start()
        # self.test_on_start()
        # self.add_widgets()
        # self.action_bindings()
        print('start')
        self.root.ids['bf'].set_window_size(self.window_size)
        self.gate(1)
        self.set_username()

    # primary_functions
    def screen_settings(self) -> tuple[int, int]:
        match platform.lower():
            # case 'android' | 'ios':
            #     ...
            # case 'windows' | 'linux':
            #     ...
            case _:
                ic(platform)

        monitors = get_monitors()
        width = set(monitor.width for monitor in monitors)
        height = set(monitor.height for monitor in monitors)

        assert len(width) == 1 and len(height) == 1, 'Ошибка. Несколько мониторов с разными расширениями'

        width, height = *width, *height

        Window.set_title('Digital Pong')
        Config.set('graphics', 'resizable', '0')
        Config.set('graphics', 'fullscreen', 'True')
        Config.set('graphics', 'width', f'{width}')
        Config.set('graphics', 'height', f'{height}')

        Config.write()

        return width, height

    def arrange_widgets(self) -> None:
        self.root.ids['bf'].set_window_size(self.window_size)
        self.root.ids['bf'].arrange_battle_filed(BattleSettings())

    def set_bindings(self) -> None:
        ...

    # design

    def change_theme_color(self) -> None:
        self.CURRENT_COLOR = (self.CURRENT_COLOR + 1) % len(self.THEME_COLORS)
        self.theme_cls.primary_palette = self.THEME_COLORS[self.CURRENT_COLOR]


    # button click -> start game
    def can_enter(self):
        if self.root.ids['player_box'].permission_check():
            self.rc_to_gf()

    # change current room

    def ss_to_rc(self):
        self.root.ids['player_box'].clear_widgets()
        app.root.current = 'room_choice'

    def rc_to_ss(self):
        app.root.current = 'start_screen'

    def rc_to_gf(self):
        self.root.ids['bf'].focus_on_layout_enable()
        self.root.current = 'game_field'

    def gf_to_rc(self):
        self.root.ids['bf'].focus_on_layout_disable()
        app.root.current = 'room_choice'

    # testing functions
    def test_print(self, *args, **kwargs):
        ic(*args, **kwargs)

    # def test_data_print(self, *args, **kwargs):
    #     ic(*args, **kwargs)
    #
    def test_on_start(self):
        self.root.ids['player_box'].add_player()
        # asynckivy.start(self.root.ids['player_box'].add_player())

    def gate(self, where: int) -> None:
        if self.USER_DATA['status']:
            requests.get(f"{self.API}/gate/{self.USER_DATA['user_id']}/{where}")

    def load_data(self, action: str) -> None:
        if action == 'exit':
            self.gate(0)
            self.USER_DATA['status'] = False
            self.USER_DATA['username'] = ""
            self.USER_DATA['password'] = ""
            self.USER_DATA['user_id'] = 0
            with open('../../../../data/player_data.json', 'w') as user_data_file:
                json.dump(self.USER_DATA, user_data_file)
            app.root.current = 'start_screen'
        else:
            if not self.USER_DATA['status']:
                response = requests.get(f"{self.API}/{action}/{self.root.ids['username_field'].text}/{self.root.ids['password_field'].text}")
                id = response.json()
                if type(id) is int:
                    self.USER_DATA['status'] = True
                    self.USER_DATA['username'] = self.root.ids['username_field'].text
                    self.USER_DATA['password'] = self.root.ids['password_field'].text
                    self.USER_DATA['user_id'] = id
                    with open('../../../../data/player_data.json', 'w') as user_data_file:
                        json.dump(self.USER_DATA, user_data_file)
                    self.gate(1)
                    app.root.current = 'start_screen'
        self.set_username()

    def set_username(self) -> None:
        self.root.ids['username_label'].text = self.USER_DATA['username'] if self.USER_DATA['status'] else ""


if __name__ == "__main__":
    try:
        app = DigitalPong()
        app.run()
    finally:
        with open('../../../../data/player_data.json') as user_data_file:
            USER_DATA = json.load(user_data_file)
            requests.get(f"http://127.0.0.1:8080/gate/{USER_DATA['user_id']}/0")
