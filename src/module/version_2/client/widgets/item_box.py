from typing import Callable, Any
import csv

import asynckivy

from icecream import ic
from kivy.properties import NumericProperty, ListProperty
from kivymd.uix.stacklayout import StackLayout

from src.module.version_2.client.widgets.player_item import PlayerListItem
from src.module.version_2.client.data import PlayerItem


# my exceptions
class ChildrenLimitExceededError(Exception):
    ...


class AllPlacesAreFilled(Exception):
    ...


class ItemBox(StackLayout):
    with open('../../../../data/player_item_data.csv', 'r', encoding='utf8') as pid_file:
        ICON_DATA, LOCATION_DATA = tuple(map(lambda u: dict(enumerate(u)), tuple(csv.reader(pid_file, delimiter=","))))

    widgets_limit = NumericProperty(0)
    window_size = ListProperty([])


    def __init__(self, *args, **kwargs):
        super(ItemBox, self).__init__(*args, **kwargs)

    # decorator
    def permission_check(self) -> bool:
        if self.children:
            return all(ch.status == 2 for ch in filter(lambda p: type(p) is PlayerListItem, self.children)) and len(self.children) == 2
        return False

    def error_catcher(function: Callable):
        def check(self, *args, **kwargs):
            try:
                function(self, *args, **kwargs)
            except ChildrenLimitExceededError:
                ic(f'Количество children : {self.widgets_quantity()} превысило лимит widgets_limit : {self.widgets_limit}')
            except AllPlacesAreFilled:
                ic(f'Количество children : {self.widgets_quantity()} достигло лимита widgets_limit : {self.widgets_limit}')
            except AssertionError as assert_error:
                ic(f'Предусмотренная ошибка - {assert_error}')
            except Exception as exception:
                ic(f'Непредусмотренная ошибка - {exception, exception.__traceback__}')
        return check

    # additional functions

    def widgets_quantity(self) -> int:
        return len(self.children)

    @error_catcher
    def get_permission(self) -> bool:
        if self.widgets_quantity() < self.widgets_limit:
            return False
        elif self.widgets_quantity() == self.widgets_limit:
            return self.permission_check()
        raise ChildrenLimitExceededError

    @error_catcher
    def add_player(self, player_item_data: StackLayout = None) -> None:
        if not player_item_data:
            player_item_data = PlayerItem.default()
        player_item_data.icon = self.ICON_DATA[player_item_data.status]
        player_item_data.location = self.LOCATION_DATA[player_item_data.status]
        self.add_widget(PlayerListItem().template(player_item_data))

    # class functions
    @error_catcher
    def add_widget(self, widget, *args, **kwargs):
        if self.widgets_quantity() < self.widgets_limit:
            super().add_widget(widget, *args, **kwargs)

    def do_layout(self, *largs):
        super().do_layout(*largs)
        self.pos = [self.window_size[0] / 2 - self.size[0] / 2, -170]
