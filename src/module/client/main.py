import sys
from typing import Callable, Any
from webbrowser import open

from kivymd.uix.slider import MDSlider, MDSliderHandle, MDSliderValueLabel
from requests import exceptions

import asynckivy
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.utils import platform
from kivy.core.window import Window
from kivy.config import Config
from kivy.core.window import Window
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.divider import MDDivider
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon, MDListItemSupportingText, MDListItemTertiaryText, \
	MDListItemTrailingCheckbox
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.widget import Widget
from kivymd.uix.dialog import (MDDialogIcon, MDDialogHeadlineText, MDDialogSupportingText,
							   MDDialogContentContainer, MDDialogButtonContainer)
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldMaxLengthText, MDTextFieldHelperText

from data_loader import download, upload, download_themes, download_menu

from src.module.client.widgets.custommdcard import MDFloatCard, MDBoxCard
from src.module.client.widgets.custommddialog import CustomMDDialog
from dialog_manager import DialogManager
from server_requests import user_log, user_registration, user_delete


class DigitalPong(MDApp):
	# V------DATA------V #
	STRUCTURE = "../../../data/structure.kv"

	THEMES = download_themes()
	SETTINGS = download("settings")
	DATA = download("data")
	MENU_DATA = download_menu()
	MENU_DATA["ball_boost"] = tuple(map(lambda x: f"{x / 10:.1f}", MENU_DATA["ball_boost"]))

	DIALOG_MANAGER = DialogManager()

	# V------START------V #

	def __init__(self, **kwargs) -> None:
		super(DigitalPong, self).__init__(**kwargs)
		self.builder = Builder.load_file(self.STRUCTURE)

	def on_start(self):
		super().on_start()
		self.set_dialogs()
		self.change_theme_color(plus=False)
		self.change_theme(self.SETTINGS["current_theme"])

		if self.DATA["username"] and self.DATA["password"]:
			response = user_log("in", username=self.DATA["username"], password=self.DATA["password"])
			if type(response) is dict:
				self.DIALOG_MANAGER("alert", header=f'Проблема - {response["status_code"]}',
									support_text=f"{response["message"]}")
			self.start(self.set_username, self.DATA["username"])

		if not self.SETTINGS['situation']:
			self.DIALOG_MANAGER("situation_choice")
		else:
			self.start(self.set_icon, 'signal' if self.SETTINGS['situation'] == 'online' else "signal-off")
			if self.SETTINGS['situation'] == 'online' and not self.DATA['username'] and not self.DATA['password']:
				self.DIALOG_MANAGER("user_enter_choice")

	def build(self) -> Builder:
		return self.builder

	def set_dialogs(self) -> None:
		self.DIALOG_MANAGER["situation_choice"] = CustomMDDialog(
			MDDialogHeadlineText(
				text="Выберите режим"
			),
			MDDialogContentContainer(
				MDDivider(orientation="vertical"),
				MDListItem(
					MDListItemLeadingIcon(
						icon="signal-off"
					),
					MDListItemSupportingText(
						text="Оффлайн"
					),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor,
					on_release=lambda item: self.start(self.choice_state_enter, "offline", item)
				),
				MDDivider(orientation="vertical"),
				MDListItem(
					MDListItemLeadingIcon(
						icon="signal"
					),
					MDListItemSupportingText(
						text="Онлайн"
					),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor,
					on_release=lambda item: self.start(self.choice_state_enter, "online", item)

				),
				MDDivider(orientation="vertical"),
				orientation="horizontal"
			),
			on_dismiss=lambda item: self.DIALOG_MANAGER("situation_choice", only_status=True, item=item)
		)
		self.DIALOG_MANAGER["user_enter_choice"] = CustomMDDialog(
			MDDialogHeadlineText(
				text="Вход"
			),
			MDDialogSupportingText(
				text="Выберите способ входа:"
			),
			MDDialogContentContainer(
				MDDivider(),
				MDListItem(
					MDListItemLeadingIcon(
						icon="account-badge"
					),
					MDListItemSupportingText(
						text="Вход"
					),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor,
					on_release=lambda item: self.DIALOG_MANAGER("login", item)
				),
				MDListItem(
					MDListItemLeadingIcon(
						icon="account-cancel"
					),
					MDListItemSupportingText(
						text="Регистрация"
					),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor,
					on_release=lambda item: self.DIALOG_MANAGER("registration", item)
				),
				MDDivider(),
				orientation="vertical"
			)
		)
		self.DIALOG_MANAGER["user_profile_view"] = CustomMDDialog(
			MDDialogIcon(
				icon='account'
			),
			MDDialogHeadlineText(
				text="Профиль"
			),
			MDDialogContentContainer(
				MDDivider(),
				MDListItem(
					MDListItemLeadingIcon(
						icon="badge-account-horizontal"
					),
					MDListItemSupportingText(
						text=""
					),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor,
					# on_release=self.rename_confirm
				),
				MDDivider(),
				MDListItem(
					MDListItemLeadingIcon(
						icon="identifier"
					),
					MDListItemSupportingText(
						text=""
					),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor,
				),
				MDDivider(),
				orientation="vertical",
			),
			MDDialogButtonContainer(
				Widget(),
				MDButton(
					MDButtonText(
						text="УДАЛИТЬ"
					),
					style="text",
					on_release=lambda item: self.DIALOG_MANAGER("delete_account_warning", item)
				),
				MDButton(
					MDButtonText(
						text="ВЫЙТИ ИЗ АККАУНТА"
					),
					style="text",
					on_release=lambda item: self.DIALOG_MANAGER("exit_from_account_warning", item)
				),
				spacing=dp(8)
			),
		)
		alert = lambda **kwargs: CustomMDDialog(
			MDDialogHeadlineText(
				text=" "
			),
			MDDialogSupportingText(
				text=" ",
				halign="left"
			),
			MDDialogButtonContainer(
				Widget(),
				MDButton(
					MDButtonText(text="ОК"),
					style="text",
					on_release=kwargs["ok_action"]
				),
				spacing="8dp"
			),
		)
		self.DIALOG_MANAGER["alert"] = alert(ok_action=lambda item: self.DIALOG_MANAGER("alert"))
		# message="Пользователя с такими данными не существует. "
		# 		"Пожалуйста, введите корректные данные, либо зарегистрируете новый аккаунт.",
		# message="Пользователь с таким именем уже существует. "
		# 		"Пожалуйста, введите другое имя.",

		data_input = lambda **kwargs: CustomMDDialog(
			MDDialogIcon(
				icon=kwargs["icon"]
			),
			MDDialogHeadlineText(
				text="Введите данные"
			),
			MDDialogContentContainer(
				MDTextField(
					MDTextFieldHintText(
						text="Имя пользователя"
					),
					MDTextFieldMaxLengthText(
						max_text_length=16) if kwargs['reg'] else None,
					mode="outlined"
				),
				MDTextField(
					MDTextFieldHintText(
						text="Пароль"
					),
					MDTextFieldMaxLengthText(
						max_text_length=20) if kwargs['reg'] else None,
					mode="outlined"),
				orientation="vertical",
				spacing=dp(20)
			),
			MDDialogButtonContainer(
				Widget(),
				MDButton(
					MDButtonText(
						text="НАЗАД"
					),
					style="text",
					on_release=kwargs['back_action']
				),
				MDButton(
					MDButtonText(text=kwargs["confirm_text"]),
					style="text",
					on_release=kwargs["confirm_action"]
				),
				spacing="8dp",
			),
		)
		self.DIALOG_MANAGER["registration"] = data_input(
			icon="account-plus",
			confirm_text="ЗАРЕГЕСТРИРОВАТЬСЯ",
			back_action=lambda item: self.DIALOG_MANAGER("registration", item),
			confirm_action=lambda item: self.start(self.registration),
			reg=True)
		self.DIALOG_MANAGER["login"] = data_input(
			icon="account-badge",
			confirm_text="ВОЙТИ",
			back_action=lambda item: self.DIALOG_MANAGER("login", item),
			confirm_action=lambda item: self.start(self.login),
			reg=False)
		confirm_alert = lambda **kwargs: CustomMDDialog(
			MDDialogHeadlineText(
				text="Предупреждение"
			),
			MDDialogSupportingText(
				text=kwargs['message'],
				halign="left"
			),
			MDDialogButtonContainer(
				Widget(),
				MDButton(
					MDButtonText(text="ОТМЕНА"),
					style="text",
					on_release=kwargs["cancel_action"]
				),
				MDButton(
					MDButtonText(text="ПОДТВЕРДИТЬ"),
					style="text",
					on_release=kwargs['confirm_action']
				),
				spacing="8dp",
			),
		)
		self.DIALOG_MANAGER["rename_warning"] = confirm_alert(
			message="Вы точно желаете сменить имя своего аккаунта?",
			confirm_action=print,
			cancel_action=lambda item: self.DIALOG_MANAGER("rename_warning", item)
		)
		self.DIALOG_MANAGER["delete_account_warning"] = confirm_alert(
			message="Вы точно желаете удалить свой аккаунт навсегда?",
			confirm_action=lambda item: self.exit_for_account(forever=True, item=item),
			cancel_action=lambda item: self.DIALOG_MANAGER("delete_account_warning", item)
		)
		self.DIALOG_MANAGER["exit_from_account_warning"] = confirm_alert(
			message="Вы точно желаете выйти из своего аккаунта?",
			confirm_action=lambda item: self.exit_for_account(forever=False, item=item),
			cancel_action=lambda item: self.DIALOG_MANAGER("exit_from_account_warning", item)
		)
		self.DIALOG_MANAGER['rename'] = CustomMDDialog(
			MDDialogHeadlineText(
				text="Введите новое имя"
			),
			MDDialogContentContainer(
				MDTextField(
					MDTextFieldHintText(
						text="Имя пользователя"
					),
					MDTextFieldMaxLengthText(max_text_length=16),
					mode="outlined"),
				orientation="vertical"
			),
			MDDialogButtonContainer(
				Widget(),
				MDButton(
					MDButtonText(
						text="ОТМЕНА"
					),
					style="text",
					# on_release=lambda item: self.dismiss_dialog(item, progenitor=4)
				),
				MDButton(
					MDButtonText(text="ПОДТВЕРДИТЬ"),
					style="text",
					# on_release=lambda item: self.dismiss_dialog(item, progenitor=4)
				),
				spacing="8dp"
			),
		)
		self.DIALOG_MANAGER["project_info"] = CustomMDDialog(
			MDDialogHeadlineText(
				text="Проект"
			),
			MDDialogContentContainer(
				MDListItem(
					MDListItemLeadingIcon(
						icon="dev-to",
					),
					MDListItemSupportingText(
						text="Алексеев  Валерий  Евгеньевич"
					),
					MDListItemSupportingText(
						text="программист  ×  интерфейсный  дизайнер  ×  продюсер"

					),
					MDListItemTertiaryText(
						text="студент  ВСПК  -  первого  курса  09.02.07"
					),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor,
					on_release=lambda item: self.start(self.open_git, "https://github.com/AlekseevValeriy")
				),
				MDListItem(
					MDListItemLeadingIcon(
						icon="application-edit-outline"
					),
					MDListItemSupportingText(
						text="Digital  Pong"
					),
					MDListItemSupportingText(
						text="интерфейс  -  Kivy  ×  KivyMD"
					),
					MDListItemTertiaryText(
						text="сервер  -  Flask  ×  SQLAlchemy"
					),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor,
					on_release=lambda item: self.start(self.open_git,
													   "https://github.com/AlekseevValeriy/Yandex-lyceum-project-3-Digital-Pong")
				),
				MDDivider(orientation="vertical"),
				orientation="vertical"
			),
			on_dismiss=lambda item: self.DIALOG_MANAGER("situation_choice", only_status=True, item=item)
		)
		self.DIALOG_MANAGER["search_filter"] = CustomMDDialog(
			MDDialogHeadlineText(
				text="Установите фильтры"
			),
			MDDialogContentContainer(
				MDTextField(
					MDTextFieldHintText(
						text="ID комнаты"
					),
					mode="outlined"),
				MDDivider(),
				MDTextField(
					MDTextFieldHintText(
						text="Лимит пользователей"
					),
					MDTextFieldHelperText(
						text="максимальный лимит 6",
						mode="on_focus"),
					mode="outlined"),
				MDDivider(),
				MDListItem(
					MDListItemSupportingText(
						text="Наличие в комнате ботов"
					),
					MDListItemTrailingCheckbox(),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor,
				),
				MDDivider(),
				MDListItem(
					MDListItemSupportingText(
						text="Только открытые"
					),
					MDListItemTrailingCheckbox(),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor,
				),
				orientation="vertical",
				spacing=dp(20)
			),
			MDDialogButtonContainer(
				Widget(),
				MDButton(
					MDButtonText(
						text="ИСКАТЬ"
					),
					style="text",
					# on_release=lambda item: self.dismiss_dialog(item, progenitor=4)
				),
				Widget()
			)
		)

	# V------BUTTONS------V #

	def change_theme_color(self, plus: bool = True, change: bool = True):
		if change:
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

	def open_menu(self, variant: str, item: Widget = None) -> None:
		def action(situation: str, offline: Callable, online: Callable) -> Callable:
			match situation.split('_')[-1]:
				case "ofl":
					return offline
				case "onl":
					return online

		def add_item(element: Any) -> dict:
			return {"text": f"{element}", "on_release": lambda: self.menu_callback(widget, f"{element}")}

		match variant:
			case "bots_can":
				variation = self.MENU_DATA["bots_can"]
				widget = self.root.ids.bots_can
			case "users_quantity":
				variation = self.MENU_DATA["users_quantity"]
				widget = self.root.ids.users_quantity
			case "platform_speed_ofl" | "platform_speed_onl":
				variation = self.MENU_DATA["platform_speed"]
				widget = action(variant, self.root.ids.platform_speed_ofl, self.root.ids.platform_speed_onl)
			case "ball_speed_ofl" | "ball_speed_onl":
				variation = self.MENU_DATA["ball_speed"]
				widget = action(variant, self.root.ids.ball_speed_ofl, self.root.ids.ball_speed_onl)
			case "ball_radius_ofl" | "ball_radius_onl":
				variation = self.MENU_DATA["ball_radius"]
				widget = action(variant, self.root.ids.ball_radius_ofl, self.root.ids.ball_radius_onl)
			case "platform_width_ofl" | "platform_width_onl":
				variation = self.MENU_DATA["platform_width"]
				widget = action(variant, self.root.ids.platform_width_ofl, self.root.ids.platform_width_onl)
			case "platform_height_ofl" | "platform_height_onl":
				variation = self.MENU_DATA["platform_height"]
				widget = action(variant, self.root.ids.platform_height_ofl, self.root.ids.platform_height_onl)
			case "ball_boost_ofl" | "ball_boost_onl":
				variation = self.MENU_DATA["ball_boost"]
				widget = action(variant, self.root.ids.ball_boost_ofl, self.root.ids.ball_boost_onl)
			case _:
				variation = [None]
				widget = None
		print(variant)
		MDDropdownMenu(
			caller=widget,
			items=[*map(add_item, variation)],
			border_margin=dp(60),
			max_height=200,
			ver_growth="down" if variant in (
				"bots_can",
				"users_quantity",
				"ball_radius_onl",
				"ball_speed_onl",
				"ball_radius_ofl",
				"ball_speed_ofl",
				"ball_boost_ofl"
			) else "up"
		).open()

	def menu_callback(self, widget: Widget, text_item: str) -> None:
		if widget:
			widget.text = text_item

	def create_room(self):
		match self.SETTINGS['situation']:
			case "offline":
				self.root.current = "offline_room_creation_menu"
			case "online":
				if not self.DATA['username'] and not self.DATA['password']:
					self.DIALOG_MANAGER("user_enter_choice")
				else:
					self.root.current = "online_room_creation_menu"

	def is_login(self):
		if self.DATA['username'] and self.DATA['password']:
			self.DIALOG_MANAGER("user_profile_view", username=self.DATA["username"], identifier=self.DATA["id"])
		elif not self.DATA['username'] and not self.DATA['password']:
			self.DIALOG_MANAGER("user_enter_choice")

	# V------DIALOG ACTIONS------V #

	async def choice_state_enter(self, situation, *args):
		self.SETTINGS['situation'] = situation
		settings = download("settings")
		settings['situation'] = self.SETTINGS['situation']
		upload('settings', settings)
		self.start(self.set_icon, 'signal' if self.SETTINGS['situation'] == 'online' else "signal-off")
		self.DIALOG_MANAGER("situation_choice")
		if self.SETTINGS['situation'] == 'online' and not self.DATA['username'] and not self.DATA['password']:
			self.DIALOG_MANAGER("user_enter_choice")

	async def login(self):
		try:
			username, password = self.get_data_from_field("login")
			response = user_log("in", username=username, password=password)
			if type(response) is int:
				self.DIALOG_MANAGER()
				self.DATA["username"] = username
				self.DATA["password"] = password
				self.DATA["id"] = response
				data = download("data")
				data['username'] = self.DATA["username"]
				data['password'] = self.DATA["password"]
				data['id'] = self.DATA["id"]
				upload('data', data)
				self.start(self.set_username, self.DATA["username"])
				self.DIALOG_MANAGER("user_profile_view", username=self.DATA["username"], identifier=self.DATA["id"])
			elif type(response) is dict:
				self.DIALOG_MANAGER("alert", header=f'Проблема - {response["status_code"]}',
									support_text=f"{response["message"]}")
		except exceptions.ConnectionError:
			self.DIALOG_MANAGER("alert", header=f'Проблемы с подключением',
								support_text="На данный момент сервер отключен. "
											 "Для устранения проблемы свяжитесь с gamedev`ом, "
											 "либо подождите, пока сервер не запуститься вновь.")
		except Exception as error:
			print(type(error), str(error))

	def get_data_from_field(self, dialog: str):
		try:
			text_fields_path = self.DIALOG_MANAGER[dialog].children[0].children[1].children[0].children[0].children
			for text_field in text_fields_path:
				match text_field.children[0].text:
					case "Пароль":
						password = text_field.text
					case "Имя пользователя":
						username = text_field.text
			return username, password
		except Exception as error:
			print(type(error).__name__, str(error))

	async def registration(self):
		try:
			username, password = self.get_data_from_field("registration")
			response_registration = user_registration(username=username, password=password)
			response_login = user_log('in', username=username, password=password)
			if not response_registration and type(response_login) is int:
				self.DIALOG_MANAGER()
				self.DATA["username"] = username
				self.DATA["password"] = password
				self.DATA['id'] = response_login
				data = download("data")
				data['username'] = self.DATA["username"]
				data['password'] = self.DATA["password"]
				data['id'] = self.DATA["id"]
				upload('data', data)
				self.start(self.set_username, self.DATA["username"])
				self.DIALOG_MANAGER("user_profile_view", username=self.DATA["username"], identifier=self.DATA["id"])
			elif type(response_registration) is dict:
				self.DIALOG_MANAGER("alert", header=f'Проблема - {response_registration["status_code"]}',
									support_text=f"{response_registration["message"]}")
			elif type(response_login) is dict:
				self.DIALOG_MANAGER("alert", header=f'Проблема - {response_login["status_code"]}',
									support_text=f"{response_login["message"]}")
		except Exception as error:
			print(type(error).__name__, str(error))

	def exit_for_account(self, forever: bool = False, item: Widget = None):
		if not forever:
			response = user_log('out', username=self.DATA["username"], password=self.DATA["password"])
		else:
			response = user_delete(username=self.DATA["username"])
		if not response:
			self.DATA["username"] = ""
			self.DATA["password"] = ""
			self.DATA["id"] = ""
			data = download("data")
			data['username'] = self.DATA["username"]
			data['password'] = self.DATA["password"]
			data['id'] = self.DATA["id"]
			upload('data', data)
			self.start(self.set_username, self.DATA["username"])
			self.DIALOG_MANAGER()
		else:
			self.DIALOG_MANAGER("exit_from_account_warning")
			self.DIALOG_MANAGER("alert", header=f'Проблема - {response["status_code"]}',
								support_text=f"{response["message"]}")

	# V------ID ACTIONS------V #

	async def set_username(self, username: str = None) -> None:
		self.root.ids.user_name.text = username if username else self.DATA["username"]

	async def set_icon(self, icon: str) -> None:
		self.root.ids.situation_icon.icon = icon

	# V------OTHER ACTIONS------V #

	def start(self, func: Callable, *args, **kwargs):
		asynckivy.start(func(*args, **kwargs))

	def min_parameter(self, setting_name: str) -> str:
		return f"{self.MENU_DATA[setting_name][0]}"

	async def open_git(self, link: str) -> None:
		open(link)


if __name__ == "__main__":
	try:
		app = DigitalPong()
		app.run()
	finally:
		data = download("data")
		user_log('out', username=data["username"], password=data["password"])
