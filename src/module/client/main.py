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
		print(len(self.THEMES))
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
		print(self.situation)
		match self.situation:
			case "offline":
				self.root.current = "offline_room_creation_menu"
			case "online":
				...

	def change_theme_color(self, plus: bool = True, set: bool = True):
		if set:
			self.theme_cls.primary_palette = self.THEMES[self.SETTINGS["current_theme_color"]]
			if plus:
				self.SETTINGS["current_theme_color"] = (self.SETTINGS["current_theme_color"] + 1) % 146
				settings = download("settings")
				settings['current_theme_color'] = self.SETTINGS["current_theme_color"]
				upload('settings', settings)
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
			case "speed_platforms_vars":
				variants = [*range(1, 10)]
				widget = self.root.ids.speed_platforms
			case "speed_ball_vars":
				variants = [*range(2, 20)]
				widget = self.root.ids.speed_ball
			case "width_vars":
				variants = [*range(5, 20)]
				widget = self.root.ids.platforms_width
			case "height_vars":
				variants = [*range(40, 200)]
				widget = self.root.ids.platforms_height
			case "radius_ball_vars":
				variants = [*range(1, 50)]
				widget = self.root.ids.radius_ball
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
