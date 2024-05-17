import asynckivy
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDListItemTertiaryText, MDListItemSupportingText
from kivymd.uix.stacklayout import MDStackLayout
from typing import Callable


class SearchRoomManager:
	def __init__(self):
		self.rooms_box: MDStackLayout | None = None
		self.choice: Callable | None = None

	def post_start_init(self, rooms_box: MDStackLayout, choice: Callable):
		self.rooms_box = rooms_box
		self.choice = choice

	async def create_item(self, room_data: tuple[str, str | int, list[str]]):
		self.rooms_box.add_widget(self.item_template(room_data))

	async def set_rooms(self, data: dict[str: tuple[int, list[str]]]) -> None:
		self.rooms_box.clear_widgets()
		tuple(map(lambda room_data: asynckivy.start(self.create_item((room_data, *data[room_data]))), data))

	def item_template(self, room_data: tuple[str, str, list[str]], **kwargs) -> MDListItem:
		return MDListItem(
			MDListItemHeadlineText(text=room_data[0]),
			MDListItemSupportingText(text=f"{len(room_data[2])}/{room_data[1]}"),
			on_release=lambda *args: asynckivy.start(self.choice(room_data[0]))
		)


def get_text(self, element: MDFloatLayout):
	return element.children[0].text
