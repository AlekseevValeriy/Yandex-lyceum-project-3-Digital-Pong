from typing import Any

from icecream import ic
from kivymd.uix.widget import MDWidget
from kivy.properties import NumericProperty, ListProperty, StringProperty, Property


class Ball(MDWidget):
    widget_id = StringProperty('')
    window_size = ListProperty([])
    location = NumericProperty(0)
    move_interval = NumericProperty(10)
    speed_x = NumericProperty(0)
    speed_y = NumericProperty(0)
    batting_speed_top = NumericProperty(10)
    batting_speed_center = NumericProperty(5)
    batting_speed_bottom = NumericProperty(10)
    size_hint = (None, None)

    def __init__(self, *args, **kwargs) -> None:
        super(Ball, self).__init__(*args, **kwargs)
        ...

    def resize(self, window_size: tuple[int, int], re=False) -> None:
        if re:
            self.pos[0] = window_size[0] / 2 - self.radius[0]
        match self.location:
            case 1:
                self.pos[1] = window_size[1] * 3 / 4
            case 0:
                self.pos[1] = window_size[1] * 2 / 4
            case -1:
                self.pos[1] = window_size[1] / 4
            case None:
                self.pos[1] = window_size[1] * 2 / 4
        self.pos[0] = window_size[0] / 2 - self.radius[0]

        if not self.window_size:
            self.window_size = window_size
        self.direct(direction_x=True)

    def speed_reset(self):
        self.speed_x, self.speed_y = 0, 0

    def direct(self, direction_x: bool = False, direction_y: bool = False):
        if direction_x:
            if not self.speed_x:
                self.speed_x = self.move_interval
            self.speed_x *= -1
        if direction_y:
            if not self.speed_y:
                self.speed_y = self.move_interval
            self.speed_y *= -1

    def collide(self, *widgets: tuple[Any]) -> None:
        self.collide_widgets(*widgets)
        self.collide_walls()

    def collide_widgets(self, *widgets: tuple[Any]) -> None:
        for widget in widgets:
            self.collide_widget(widget)

    def collide_walls(self) -> False:
        # Стены - верх, низ
        if self.top >= self.window_size[1] or self.y < 0:
            self.direct(direction_y=True)
        # Стены - право, лево
        if self.right >= self.window_size[0] or self.x < 0:
            self.direct(direction_x=True)
            self.pos[0] = self.window_size[0] // 2 - self.radius[0]
            self.pos[1] = self.window_size[1] // 2 - self.radius[0]
            self.speed_y = 0
            # self.direct(direction_x=True)

    def collide_widget(self, wid: Any) -> None:
        def tearing_out_textures(widget: Any) -> bool:
            if widget.x <= self.x <= widget.right:
                self.x = widget.right + 1
                return True

            elif widget.x <= self.right <= widget.right:
                self.right = widget.x - 1
                return True
            return False

        if (wid.y - self.radius[0]) < (self.y + self.radius[0]) < (wid.top + self.radius[0]):
            if tearing_out_textures(wid):
                self.direct(direction_x=True)
                self.vertical_gap(wid)

            # TODO добааить коллизию на краю исходя из суммы радиусов
            """if ((self.width / 2 + ((wid.width / 2) ** 2 + (wid.height / 2) ** 2) ** 0.5)
                >=
                ((abs((self.x + self.width / 2) - (wid.x + wid.width / 2)) ** 2 +
                abs((self.y + self.height / 2) - (wid.y + wid.height / 2)) ** 2) ** 0.5)):
                    if self.right >= wid.x or self.x <= wid.right:
                        self.redirection(direction_x=True)
                        tearing_out_textures(wid)
                    if self.top <= wid.top or self.y >= wid.y:
                        self.redirection(direction_y=True)
                        tearing_out_textures(wid)"""

    def get_center(self) -> int:
        return self.y + self.radius[0]

    def vertical_gap(self, wid):
        full_height = wid.height + self.height

        target = abs((wid.y - self.radius[0]) - (self.y + self.radius[0]))

        if 0 < target < (full_height * 2 / 5):
            self.speed_y -= self.batting_speed_bottom
        elif (full_height * 2 / 5) <= target < (full_height * 3 / 5):
            if self.speed_y > 0:
                self.speed_y += self.batting_speed_center
            elif self.speed_y < 0:
                self.speed_y -= self.batting_speed_center
        elif (full_height * 3 / 5) <= target <= full_height:
            self.speed_y += self.batting_speed_top

        if self.speed_y > 20:
            self.speed_y = 20
        elif self.speed_y < -20:
            self.speed_y = -20

    def move(self):
        self.pos[0] += self.speed_x
        self.pos[1] += self.speed_y

    @staticmethod
    def template(location: int = None, color: str = "black", widget_id: str = 'b_', move: int = 20, radius: int = 15) -> MDWidget:
        return Ball(
            widget_id=widget_id,
            location=location,
            radius=radius,
            move_interval=move,
            theme_bg_color='Custom',
            md_bg_color=color,
            size=(radius * 2, radius * 2)
        )