from icecream import ic
from kivymd.uix.widget import MDWidget
from kivy.properties import StringProperty, NumericProperty, Property


class Platform(MDWidget):
    widget_id = StringProperty('')
    location = Property([0, 0])
    speed = NumericProperty(0)
    border_x = NumericProperty(200)
    window_height = NumericProperty(0)
    size_hint = (None, None)
    theme_bg_color = "Custom"
    half_size_x = 0
    half_size_y = 0

    def __init__(self, *args, **kwargs):
        super(Platform, self).__init__(*args, **kwargs)
        self.half_size_x = self.width / 2
        self.half_size_y = self.height / 2

    def resize(self, window_size: tuple[float | int, float | int],
               default_window_size: tuple[float | int, float | int] = [1000, 1000]) -> None:
        if type(self.location) is list:
            match self.location:
                case None:
                    print(None)
                    self.pos[1] = window_size[1] * 3 / 4 - self.half_size_y
                    match self.widget_id:
                        case 'p_l':
                            self.pos[0] = default_window_size[0] * self.border_x / window_size[0]
                        case _:
                            self.pos[0] = window_size[0] - (
                                        default_window_size[0] * self.border_x / window_size[0] + self.size[0])
                case [_, _]:
                    match self.location[1]:
                        case 0:
                            self.pos[1] = window_size[1] - self.half_size_y
                        case 1:
                            self.pos[1] = window_size[1] * 2 / 4 - self.half_size_y
                        case -1:
                            self.pos[1] = window_size[1] / 4 - self.half_size_y
                    match self.location[0]:
                        case -1:
                            self.pos[0] = default_window_size[0] * self.border_x / window_size[0]
                        case 1:
                            self.pos[0] = window_size[0] - (
                                        default_window_size[0] * self.border_x / window_size[0] + self.size[0])

    def move(self, touch_y: int = 0) -> None:
            if abs(self.pos[1] - touch_y) >= self.speed:
                if touch_y > self.y and self.top <= self.window_height:
                    self.pos[1] += self.speed
                elif touch_y < self.top and self.y > 0:
                    self.pos[1] -= self.speed
            else:
                self.pos[1] = touch_y

    @staticmethod
    def template(location: list = None, color: str = "black", widget_id: str = 'pl_', window_height=1920) -> MDWidget:
        return Platform(
            widget_id=widget_id,
            size=(20, 200),
            location=location,
            md_bg_color=color,
            speed=10,
            window_height=window_height
        )
