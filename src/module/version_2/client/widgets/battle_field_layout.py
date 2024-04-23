from typing import Any

from icecream import ic
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import DictProperty, ListProperty, NumericProperty, BooleanProperty, StringProperty
import asynckivy
from random import randint

from src.module.version_2.client.data import BattleSettings
from src.module.version_2.client.widgets.platform import Platform
from src.module.version_2.client.widgets.ball import Ball

my_platform_name = 'p_l'


class BattleField(RelativeLayout):
    _ids = DictProperty({})
    window_size = ListProperty([])
    touch = NumericProperty(0)
    is_battle = BooleanProperty(False)
    my_platform = StringProperty(my_platform_name)
    frame_rate = NumericProperty(60)
    points = ListProperty([0, 0])

    def __init__(self, *args, **kwargs):
        super(BattleField, self).__init__(*args, **kwargs)

    @staticmethod
    def template(window_size: list[int, int]) -> Any:
        return BattleField(
            id='bf',
            window_size=window_size
        )

    async def move_cycle(self):
        while self.is_battle:
            tuple(map(self.separation_movements, self._ids))
            await asynckivy.sleep(1 / self.frame_rate)

    def focus_on_layout_enable(self, battle_setting: BattleSettings = None):  # battle start
        if not battle_setting:
            battle_setting = BattleSettings.default()
        self.arrange_battle_filed(battle_setting)
        self.resize()
        self.is_battle = True
        asynckivy.start(self.move_cycle())

    def focus_on_layout_disable(self):  # Battle end
        self.is_battle = False
        self.clear_widgets(self.get_tools())
        self._ids = {}

    def separation_movements(self, widget: Any) -> None:
        if self._ids[widget].__class__.__name__ == 'Platform':
            match self._ids[widget].widget_id:
                case self.my_platform:
                    self._ids[widget].move(self.touch)
                case _:
                    #TODO менять положение ракетки от api
                    self._ids[widget].move(self._ids['b_'].get_center() - self._ids[widget].height / 2)
        elif self._ids[widget].__class__.__name__ == 'Ball':
            self._ids[widget].collide(self._ids[self.my_platform], self._ids['pl_'])
            self._ids[widget].move()

    def arrange_battle_filed(self, battle_setting: BattleSettings):
        for _ in range(battle_setting.players_number // 2):
            self.add_widget(Platform.template([-1, 1], color='blue', widget_id=self.my_platform, window_height=self.window_size[1]))
            self.add_widget(Platform.template([1, 1], color='red', window_height=self.window_size[1]))

        for _ in range(battle_setting.balls_number):
            self.add_widget(Ball.template(location=0, radius=battle_setting.ball_radius))

        self.assign__ids()

    def resize(self):
        for child in filter(lambda ch: ch != 'back_to_start_menu', self._ids):
            self._ids[child].resize(self.window_size)

    def assign__ids(self) -> None:
        def add_id(widget: Any) -> None:
            self._ids[widget.widget_id] = widget

        tuple(map(add_id, self.children))

    def set_window_size(self, window_size: tuple[float | int, float | int]):
        self.window_size = window_size

    # class functions
    def do_layout(self, *args):
        super().do_layout(*args)
        # self.resize_platforms()

    def on_touch_move(self, touch):
        self.touch = touch.y - self._ids[self.my_platform].height // 2

    # def on_touch_up(self, touch):
    #     self.touch = self._ids[self.my_platform].y

    def get_tools(self):
        tools = []
        for ch in filter(lambda ch: self._ids[ch].__class__.__name__ in ['Ball', 'Platform'], self._ids):
            tools.append(self._ids[ch])
        return tools

    def check_points(self):
        if [self._ids['counter_left'],  self._ids['counter_right']] != self.points:
            self.points = [self._ids['counter_left'],  self._ids['counter_right']]
if __name__ == '__main__':
    bf = BattleField()
