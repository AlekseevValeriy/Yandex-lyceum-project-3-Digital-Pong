import asynckivy
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.utils import platform
from kivy.core.window import Window
from kivy.config import Config
from kivy.core.window import Window
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.widget import Widget

from data_loader import download, upload, download_themes

from src.module.client.widgets.mdfloatcard import MDFloatCard


class DigitalPong(MDApp):
	STRUCTURE = "../../../data/structure.kv"

	THEMES = download_themes()
	SETTINGS = download("settings")
	DATA = download("data")

	def __init__(self, **kwargs) -> None:
		super(DigitalPong, self).__init__(**kwargs)
		self.situation = self.SETTINGS["situation"] if self.SETTINGS["situation"] else None
		self.builder = Builder.load_file(self.STRUCTURE)

	def on_start(self):
		super().on_start()
		self.root.current = "game_start_menu" if self.situation else "game_state_selection_screen"
		self.change_theme_color(plus=False)
		self.change_theme(self.SETTINGS["current_theme"])

	def build(self) -> Builder:
		return self.builder

	def choice_state_enter(self, situation):
		self.root.current = "game_start_menu"
		self.situation = situation
		settings = download("settings")
		settings['situation'] = self.situation
		upload('settings', settings)

	def choice_create_room(self):
		# поменять окно на диалог, для красоты и уменьшения давления, скукоты, пустоты
		match self.situation:
			case "offline":
				self.root.current = "offline_room_creation_menu"
			case "online":
				self.root.current = "online_room_creation_menu"

	def change_theme_color(self, plus: bool = True, set: bool = True):
		if set:
			if plus:
				self.SETTINGS["current_theme_color"] = (self.SETTINGS["current_theme_color"] + 1) % 146
				settings = download("settings")
				settings['current_theme_color'] = self.SETTINGS["current_theme_color"]
				upload('settings', settings)
				self.theme_cls.primary_palette = self.THEMES[self.SETTINGS["current_theme_color"]]
			else:
				self.theme_cls.primary_palette = self.THEMES[self.SETTINGS["current_theme_color"]]
		else:
			self.theme_cls.primary_palette = self.THEMES[10]

	def change_theme(self, theme_style: int = None):
		if theme_style in (0, 1):
			self.theme_cls.theme_style = "Light" if theme_style == 1 else "Dark"
		else:
			self.theme_cls.switch_theme()
			settings = download("settings")
			settings['current_theme'] = 0 if self.theme_cls.theme_style == "Dark" else 1
			upload('settings', settings)

	def open_menu(self, item: Widget, variant: str) -> None:
		match variant:
			case "platform_speed_ofl":
				variants = [*range(1, 11)]
				widget = self.root.ids.platform_speed_ofl
			case "ball_speed_ofl":
				variants = [*range(2, 21)]
				widget = self.root.ids.ball_speed_ofl
			case "platform_width_ofl":
				variants = [*range(5, 21)]
				widget = self.root.ids.platform_width_ofl
			case "platform_height_ofl":
				variants = [*range(40, 201)]
				widget = self.root.ids.platform_height_ofl
			case "ball_radius_ofl":
				variants = [*range(1, 51)]
				widget = self.root.ids.ball_radius_ofl
			case "ball_boos_ofl":
				variants = [*map(lambda x: f"{x / 10:.1f}", range(10, 21))]
				widget = self.root.ids.ball_boos_ofl
			case "bots_can":
				variants = [True, False]
				widget = self.root.ids.bots_can
			case "users_quantity":
				variants = [*range(1, 7)]
				widget = self.root.ids.users_quantity
			case "ball_radius_onl":
				variants = [*range(1, 11)]
				widget = self.root.ids.ball_radius_onl
			case "ball_speed_onl":
				variants = [*range(1, 21)]
				widget = self.root.ids.ball_speed_onl
			case "ball_boos_onl":
				variants = [*map(lambda x: f"{x / 10:.1f}", range(10, 21))]
				widget = self.root.ids.ball_boos_onl
			case "platform_speed_onl":
				variants = [*range(1, 10)]
				widget = self.root.ids.platform_speed_onl
			case "platform_height_onl":
				variants = [*range(40, 201)]
				widget = self.root.ids.platform_height_onl
			case "platform_width_onl":
				variants = [*range(5, 21)]
				widget = self.root.ids.platform_width_onl
			case _:
				variants = [None]
				widget = None

		menu_items = [{
			"text": f"{i}",
			"on_release": lambda x=f"{i}": self.menu_callback(widget, x),
		} for i in variants]

		MDDropdownMenu(caller=item, items=menu_items, max_height=300).open()

	def menu_callback(self, widget: Widget, text_item: str) -> None:
		if widget:
			widget.text = text_item


if __name__ == "__main__":
	try:
		app = DigitalPong()
		app.run()
	finally:
		...
