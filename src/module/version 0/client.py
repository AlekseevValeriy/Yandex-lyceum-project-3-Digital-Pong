import asynckivy
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.app import MDApp
from kivymd.uix.behaviors import RotateBehavior
from kivymd.uix.button import MDIconButton
from kivymd.uix.expansionpanel import MDExpansionPanel
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import MDListItemTrailingIcon, MDListItem, MDListItemLeadingIcon, MDListItemHeadlineText, \
    MDListItemSupportingText
from kivy.config import Config
from kivy.core.window import WindowBase
from kivy.core.window import Window
from kivymd.uix.chip import MDChip, MDChipText
from kivy.uix.label import Label
from random import random
from kivy.core.window import Window
import sys
import csv
from kivy.config import Config
from kivymd.uix.widget import MDWidget

class PlayerListItem(MDListItem):
    status = NumericProperty(0)
    ...


class BattleField(MDFloatLayout):
    childrens = {}

    def __init__(self, *args, **kwargs):
        super(BattleField, self).__init__(*args, **kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._distribution()

    def _distribution(self):
        def add_children(children_object):
            self.childrens[children_object.id] = children_object

        tuple(map(add_children, self.children))

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        match keycode[1]:
            case 'w':
                self.childrens['platform_left'].move('up')
            case 's':
                self.childrens['platform_left'].move('down')


class Platform(MDWidget):
    def __init__(self, *args, color='red', **kwargs):
        super(Platform, self).__init__(*args, **kwargs)

    def move(self, directions):
        match directions:
            case 'up':
                self.set_center_y(self.center_y + 10)
            case 'down':
                self.set_center_y(self.center_y - 10)


class DigitalPong(MDApp):
    STRUCTURE_FILE = '../../data/structure.kv'
    with open('../../data/theme_colors.csv', 'r', encoding='utf8') as tc_file:
        THEME_COLORS = tuple(csv.reader(tc_file, delimiter=","))[0]
    CURRENT_COLOR = 0
    PLAYER_STATUS = {0: ('account-outline', ' '), 1: ('account', 'На месте'), 2: ('account-check', 'Готов')}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server = None
        WindowBase.set_title(self, 'Digital Pong')
        Config.set('graphics', 'width', '200')
        Config.set('graphics', 'height', '200')
        Config.write()
        Window.bind(on_resize=self.test_action)

    def room_id_format(self, id_text: str):
        def cropping_text(text: str, length: int) -> str:
            return text[:length]

        def digital_text(text: str) -> str:
            if text and not text[-1].isdigit():
                return text[:-1]
            return text

        self.root.ids.room_field.text = cropping_text(text=digital_text(id_text), length=10)

        if self.server:
            self.root.ids.room_field.error = True if not self.server.id_confirm(id_text) else False

    def build(self):
        return Builder.load_file(self.STRUCTURE_FILE)

    def change_theme_color(self):
        self.CURRENT_COLOR = (self.CURRENT_COLOR + 1) % len(self.THEME_COLORS)
        self.theme_cls.primary_palette = self.THEME_COLORS[self.CURRENT_COLOR]

    def exit(self):
        sys.exit(0)

    async def add_player(self, player_data: dict = {}) -> None:
        try:
            assert len(self.root.ids['player_box'].children) < 2, 'Player storage is full'
            # Получаю дату с сервера о комнате, об игроке
            # player_data = player_data
            player_data = {"player_name": "Player_test",
                           "player_status": 2,
                           "player_data": 'data',
                           "chips_data": ("Побед: 10", "Поражения: 5", "Звание: Лидер")}
            player_icon, player_status = self.PLAYER_STATUS[player_data['player_status']]
            player_item = PlayerListItem(
                MDListItemLeadingIcon(
                    icon=player_icon),
                MDListItemHeadlineText(
                    text=player_data['player_name']
                ),
                MDListItemSupportingText(
                    text=player_status
                ),
                *tuple(
                    MDChip(
                        MDChipText(
                            text=data
                        ),
                        pos_hint={'center_y': .5},
                        md_bg_color='white',
                        theme_bg_color='Primary',
                        on_release=self.happy
                    )
                    for data in player_data['chips_data']),
                MDIconButton(
                    icon="skull-crossbones-outline",
                    style="filled",
                    pos_hint={'center_x': 0.5, 'center_y': 0.5},
                    on_release=self.remove_player
                ),
                status=player_data['player_status']
            )
            self.root.ids['player_box'].add_widget(player_item)
        except AssertionError as assert_error:
            print(assert_error)

    def happy(self, widget_class):
        match widget_class.__class__.__name__:
            case 'MDChip':
                widget_class.theme_bg_color = 'Custom'
                widget_class.md_bg_color = (random(), random(), random(), 1)

    def remove_player(self, player_button_class: MDIconButton) -> None:
        self.root.ids['player_box'].remove_widget(player_button_class.parent)

    def start_game(self):
        if len(widgets := self.root.ids['player_box'].children) == 2 and all(s.status == 2 for s in widgets):
            self.root.current = 'game_filed'
            self.add_battle_filed_elements()
        else:
            print('Не')

    def add_battle_filed_elements(self):
        battle_field = BattleField(
            Platform(
                id='platform_left',
                theme_bg_color='Custom',
                md_bg_color='red',
                size_hint=(None, None),
                size=(25, 125),
                pos=(self.root.size[0] * 0.05 - 25 // 2, self.root.size[1] * 0.5 - 125 // 2)
            ),
            Platform(
                id='platform_right',
                theme_bg_color='Custom',
                md_bg_color='blue',
                size_hint=(None, None),
                size=(25, 125),
                pos=(self.root.size[0] * 0.95 - 25 // 2, self.root.size[1] * 0.5 - 125 // 2)
            )
        )
        self.root.ids['battle_field'].add_widget(widget=battle_field)

    def test_action(self, *args, **kwargs):
        ...


if __name__ == '__main__':
    game_test = DigitalPong()
    game_test.run()
