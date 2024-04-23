from dataclasses import dataclass

from icecream import ic


@dataclass
class PlayerItem:
    status: int
    nickname: str
    icon: str = "vector-point"
    location: str = " "
    data: str = ""
    chips: tuple = ()

    @staticmethod
    def default(status: int = 2):
        return PlayerItem(
            status=status,
            nickname="default_bot",
            location="location",
            data="data",
            chips=("chip_1", "chip_2", "chip_3")
        )


@dataclass
class BattleSettings:
    players_number: int = 2
    platform_size: tuple[int | float, int | float] = (20, 100)
    balls_number: int = 1
    ball_radius: float | int = 30
    default_screen: tuple[int | float, int | float] = (1000, 1000)

    @staticmethod
    def default():
        return BattleSettings()


if __name__ == '__main__':
    a = PlayerItem.default()
    print(a)
    a.icon = 'a'
    print(a)