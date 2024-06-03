import sys
from typing import Callable, Any
from webbrowser import open
from traceback import extract_tb

from screeninfo import get_monitors
from requests import exceptions
import asynckivy
from kivy.metrics import dp
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.divider import MDDivider
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon, MDListItemSupportingText, MDListItemTertiaryText, \
	MDListItemTrailingCheckbox, MDListItemLeadingAvatar, MDListItemHeadlineText
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.widget import Widget
from kivymd.uix.dialog import (MDDialogIcon, MDDialogHeadlineText, MDDialogSupportingText, MDDialogContentContainer,
							   MDDialogButtonContainer)
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldMaxLengthText, MDTextFieldHelperText

from data_loader import download, upload, download_themes, download_menu
from src.module.client.widgets.custommdcard import *
from src.module.client.widgets.custommddialog import *
from src.module.client.widgets.custommdbutton import *
from src.module.client.battle_enviroment import CustomBattleMDFloatLayout
from dialog_manager import DialogManager
from room_user_manager_system import UserManager
from search_room_manager import SearchRoomManager
from server_requests import (user_log, user_registration, user_delete, testing, room_user_ids, room_user_ids_divine, \
							 room_all, room_enter, room_leave, user_side_change, room_search, room_create, room_delete,
							 room_get_settings, room_update_settings, room_can_enter)


class ResponseException(Exception):
	...


class TheRoomHasBeenDeleted(ResponseException):
	...


class DigitalPong(MDApp):
	# V------DATA------V #
	STRUCTURE = "../../../data/structure.kv"

	THEMES = download_themes()
	SETTINGS = download("settings")
	DATA = download("data")
	MENU_DATA = download_menu()
	MENU_DATA["ball_boost"] = tuple(map(lambda x: f"{x / 10:.1f}", MENU_DATA["ball_boost"]))

	DIALOG_MANAGER = DialogManager()
	USER_MANAGER = UserManager()
	SEARCH_ROOM_MANAGER = SearchRoomManager()

	# /\------DATA------/\ #

	# V------START------V #

	def __init__(self, **kwargs) -> None:
		super(DigitalPong, self).__init__(**kwargs)
		self.builder = Builder.load_file(self.STRUCTURE)

	def on_start(self):
		super().on_start()
		self.USER_MANAGER.post_start_init(self.root.ids.left_users_box, self.root.ids.right_users_box)
		self.SEARCH_ROOM_MANAGER.post_start_init(self.root.ids.room_container, self.room_enter)
		self.set_dialogs()
		asynckivy.start(self.change_theme_color(plus=False))
		asynckivy.start(self.change_theme(self.SETTINGS["current_theme"]))
		self.set_state('not_room')

		if self.DATA["username"] and self.DATA["password"]:
			if self.testing_server_work():
				asynckivy.start(self.login(just=True))
			else:
				asynckivy.start(self.get_error_alert(exceptions.ConnectionError()))
			asynckivy.start(self.set_username(self.DATA["username"]))

		if not self.SETTINGS['situation']:
			self.DIALOG_MANAGER("situation_choice")
		else:
			asynckivy.start(self.set_icon('signal' if self.SETTINGS['situation'] == 'online' else "signal-off"))
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
					on_release=lambda item: asynckivy.start(self.choice_state_enter("offline"))
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
					on_release=lambda item: asynckivy.start(self.choice_state_enter("online"))

				),
				MDDivider(orientation="vertical"),
				orientation="horizontal"
			),
			on_dismiss=lambda item: self.DIALOG_MANAGER("situation_choice", only_status=True)
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
					on_release=lambda item: self.DIALOG_MANAGER("login")
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
					on_release=lambda item: self.DIALOG_MANAGER("registration")
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
					on_release=lambda item: self.DIALOG_MANAGER("delete_account_warning")
				),
				MDButton(
					MDButtonText(
						text="ВЫЙТИ ИЗ АККАУНТА"
					),
					style="text",
					on_release=lambda item: self.DIALOG_MANAGER("exit_from_account_warning")
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
			back_action=lambda item: self.DIALOG_MANAGER("registration"),
			confirm_action=lambda item: asynckivy.start(self.registration()),
			reg=True)
		self.DIALOG_MANAGER["login"] = data_input(
			icon="account-badge",
			confirm_text="ВОЙТИ",
			back_action=lambda item: self.DIALOG_MANAGER("login"),
			confirm_action=lambda item: asynckivy.start(self.login()),
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
			cancel_action=lambda item: self.DIALOG_MANAGER("rename_warning")
		)
		self.DIALOG_MANAGER["delete_account_warning"] = confirm_alert(
			message="Вы точно желаете удалить свой аккаунт навсегда?",
			confirm_action=lambda item: self.exit_for_account(forever=True, item=item),
			cancel_action=lambda item: self.DIALOG_MANAGER("delete_account_warning")
		)
		self.DIALOG_MANAGER["exit_from_account_warning"] = confirm_alert(
			message="Вы точно желаете выйти из своего аккаунта?",
			confirm_action=lambda item: self.exit_for_account(forever=False, item=item),
			cancel_action=lambda item: self.DIALOG_MANAGER("exit_from_account_warning")
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
					# on_release=lambda item: item
				),
				MDButton(
					MDButtonText(text="ПОДТВЕРДИТЬ"),
					style="text",
					# on_release=lambda item: item
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
					# MDListItemLeadingAvatar(
					# 	source="../../../data/image/developer_vua_rera.jpg",
					# 	size=(60, 60)
					# ),
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
					on_release=lambda item: asynckivy.start(self.open_git("https://github.com/AlekseevValeriy"))
				),
				MDListItem(
					MDListItemLeadingIcon(
						icon="application-edit-outline",
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
					on_release=lambda item: asynckivy.start(
						self.open_git("https://github.com/AlekseevValeriy/Yandex-lyceum-project-3-Digital-Pong"))
				),
				MDDivider(orientation="vertical"),
				orientation="vertical"
			),
			on_dismiss=lambda item: self.DIALOG_MANAGER("situation_choice", only_status=True)
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
					MDTextFieldHelperText(
						text="комната не найдена",
						mode="on_error"),
					mode="outlined",
				),
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
					on_release=lambda item: asynckivy.start(self.filter_search())
				),
				Widget()
			)
		)
		self.DIALOG_MANAGER["battle_statistic"] = CustomMDDialog(
			MDDialogHeadlineText(
				text=" "
			),
			MDDialogContentContainer(
				MDListItem(
					MDListItemLeadingIcon(
						icon="border-left-variant"
					),
					MDListItemHeadlineText(
						text="Левая сторона"
					),
					MDListItemSupportingText(
						text=" "
					),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor
				),
				MDListItem(
					MDListItemLeadingIcon(
						icon="border-right-variant"
					),
					MDListItemHeadlineText(
						text="Правая сторона"
					),
					MDListItemSupportingText(
						text=" "
					),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor
				),
				orientation='vertical'
			),
			MDDialogButtonContainer(
				Widget(),
				MDButton(
					MDButtonText(
						text="ВЫЙТИ"
					),
					style="text",
					on_release=lambda item: self.end_back()
				),
				Widget()
			)
		)

	# /\------START------/\ #

	# V------BUTTONS------V #

	async def change_theme_color(self, plus: bool = True, change: bool = True):
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

	async def change_theme(self, theme_style: int = None):
		if theme_style in (0, 1):
			self.theme_cls.theme_style = "Light" if theme_style == 1 else "Dark"
		else:
			self.theme_cls.switch_theme()
			settings = download("settings")
			settings['current_theme'] = 0 if self.theme_cls.theme_style == "Dark" else 1
			upload('settings', settings)

	async def open_menu(self, variant: str, item: Widget = None) -> None:
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
				elif not self.testing_server_work():
					asynckivy.start(self.get_error_alert(exceptions.ConnectionError()))

				else:
					self.root.current = "online_room_creation_menu"

	def is_login(self):
		if self.DATA['username'] and self.DATA['password']:
			self.DIALOG_MANAGER("user_profile_view", username=self.DATA["username"], identifier=self.DATA["id"])
		elif not self.DATA['username'] and not self.DATA['password']:
			self.DIALOG_MANAGER("user_enter_choice")

	# /\------BUTTONS------/\ #

	# V------DIALOG ACTIONS------V #

	def back(self):
		self.root.current = "offline_room_creation_menu"
		asynckivy.start(self.root.ids.battle_field.exit())

	def end_back(self):
		self.root.current = "offline_room_creation_menu"
		asynckivy.start(self.root.ids.battle_field.end_exit())

	async def enter_to_battle_filed(self):
		self.root.current = "battle_field"
		self.root.ids.battle_field.pre_init(
			str(self.DATA['id']),
			'offline',
			{
				"ball_radius": self.root.ids.ball_radius_ofl.text,
				"ball_speed": self.root.ids.ball_speed_ofl.text,
				"ball_boost": self.root.ids.platform_height_ofl.text,
				"platform_speed": self.root.ids.platform_speed_ofl.text,
				"platform_width": self.root.ids.platform_width_ofl.text,
				"platform_height": self.root.ids.platform_height_ofl.text
			},
			self.back,
			self.window_size,
			self.counter,
			self.DIALOG_MANAGER
		)
		asynckivy.start(self.root.ids.battle_field.enter())

	async def choice_state_enter(self, situation):
		self.SETTINGS['situation'] = situation
		settings = download("settings")
		settings['situation'] = self.SETTINGS['situation']
		upload('settings', settings)
		asynckivy.start(self.set_icon('signal' if self.SETTINGS['situation'] == 'online' else "signal-off"))
		self.DIALOG_MANAGER("situation_choice")
		if self.SETTINGS['situation'] == 'online' and not self.DATA['username'] and not self.DATA['password']:
			self.DIALOG_MANAGER("user_enter_choice")

	async def login(self, just: bool = False):
		try:
			if not just:
				username, password = self.get_data_from_field("login")
				response = user_log("in", username=username, password=password)
			else:
				response = user_log("in", username=self.DATA["username"], password=self.DATA["password"])
			if type(response) is dict:
				raise ResponseException(response)
			if not just:
				self.DIALOG_MANAGER()
				self.DATA["username"] = username
				self.DATA["password"] = password
				self.DATA["id"] = response
				data = download("data")
				data['username'] = self.DATA["username"]
				data['password'] = self.DATA["password"]
				data['id'] = self.DATA["id"]
				upload('data', data)
				asynckivy.start(self.set_username(self.DATA["username"]))
				self.DIALOG_MANAGER("user_profile_view", username=self.DATA["username"], identifier=self.DATA["id"])
		except Exception as exception:
			asynckivy.start(self.get_error_alert(exception))

	def get_data_from_field(self, dialog: str):
		text_fields_path = self.DIALOG_MANAGER[dialog].children[0].children[1].children[0].children[0].children
		for text_field in text_fields_path:
			match text_field.children[0].text:
				case "Пароль":
					password = text_field.text
				case "Имя пользователя":
					username = text_field.text
		return username, password

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
				asynckivy.start(self.set_username(self.DATA["username"]))
				self.DIALOG_MANAGER("user_profile_view", username=self.DATA["username"], identifier=self.DATA["id"])
			elif type(response_registration) is dict:
				raise ResponseException(response_registration)
			elif type(response_login) is dict:
				raise ResponseException(response_login)
		except Exception as exception:
			asynckivy.start(self.get_error_alert(exception))

	def exit_for_account(self, forever: bool = False, item: Widget = None):
		try:
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
				asynckivy.start(self.set_username(self.DATA["username"]))
				self.DIALOG_MANAGER()
			else:
				self.DIALOG_MANAGER("exit_from_account_warning")
				raise ResponseException(response)
		except Exception as exception:
			asynckivy.start(self.get_error_alert(exception))

	async def delete_room(self):
		try:
			response = room_delete(self.DATA['current_room_id'])
			if not response:
				self.set_state("not_room")
			else:
				raise ResponseException(response)
		except Exception as exception:
			asynckivy.start(self.get_error_alert(exception))

	# /\------DIALOG ACTIONS------/\ #

	# V------ID ACTIONS------V #

	async def set_username(self, username: str = None) -> None:
		self.root.ids.user_name.text = username if username else self.DATA["username"]

	async def set_icon(self, icon: str) -> None:
		self.root.ids.situation_icon.icon = icon

	# # V------INTERFACE BLOCKERS------V # #

	def button_translate(self, btn: str) -> MDButton:
		match btn:
			case "back":
				return self.root.ids.room_btn_back
			case "search":
				return self.root.ids.room_btn_search
			case "create":
				return self.root.ids.room_btn_create
			case "play":
				return self.root.ids.room_btn_play
			case "exit":
				return self.root.ids.room_btn_exit
			case "delete":
				return self.root.ids.room_btn_delete

	async def disable_btn(self, *btns: str) -> None:
		def disable(btn: MDButton) -> None:
			btn.disabled = True

		asynckivy.start(self.change_btn(disable, *btns))

	async def enable_btn(self, *btns: str) -> None:
		def enable(btn: MDButton) -> None:
			btn.disabled = False

		asynckivy.start(self.change_btn(enable, *btns))

	async def change_btn(self, func: Callable, *btns: str) -> None:
		tuple(map(func, map(self.button_translate, btns)))

	def set_state(self, state: str):
		match state:
			case "pre_create_room":
				asynckivy.start(self.disable_btn("back", "search", "create", "exit", "delete", "play"))
				asynckivy.start(self.enable_btn("create"))
				asynckivy.start(self.set_enter_block('all'))
				asynckivy.start(self.set_data_settings('min'))
				asynckivy.start(self.set_room_settings(False))
			case "create_room":
				asynckivy.start(self.disable_btn("back", "search", "create", "exit"))
				asynckivy.start(self.enable_btn("delete", "play"))
				asynckivy.start(self.set_enter_block('none'))
				asynckivy.start(self.set_room_settings(False))
			case "enter_room":
				asynckivy.start(self.disable_btn("back", "search", "create", "delete", "play"))
				asynckivy.start(self.enable_btn("exit"))
				asynckivy.start(self.set_enter_block('none'))
				asynckivy.start(self.set_room_settings(True))
			case "not_room":
				self.DATA["current_room_id"] = 0
				asynckivy.start(self.disable_btn("delete", "exit", "play"))
				asynckivy.start(self.enable_btn("back", "search", "create"))
				asynckivy.start(self.set_enter_block('all'))
				self.USER_MANAGER.clear()
				asynckivy.start(self.set_room_settings(True))
				asynckivy.start(self.set_data_settings('null'))
				self.DATA["room_role"] = ""

	@property
	def room_settings(self) -> list:
		return [self.root.ids.bots_can_box,
				self.root.ids.users_quantity_box,
				self.root.ids.ball_radius_onl_box,
				self.root.ids.ball_speed_onl_box,
				self.root.ids.ball_boost_onl_box,
				self.root.ids.platform_speed_onl_box,
				self.root.ids.platform_height_onl_box,
				self.root.ids.platform_width_onl_box]

	async def set_room_settings(self, state: bool):
		def set_status(item):
			item.disabled = state

		tuple(map(set_status, self.room_settings))

	async def set_enter_block(self, side):
		match side:
			case "left":
				self.root.ids.room_side_enter_right.disabled = False
				self.root.ids.room_side_enter_left.disabled = True
			case 'right':
				self.root.ids.room_side_enter_right.disabled = True
				self.root.ids.room_side_enter_left.disabled = False
			case "all":
				self.root.ids.room_side_enter_right.disabled = True
				self.root.ids.room_side_enter_left.disabled = True
			case "none":
				self.root.ids.room_side_enter_right.disabled = False
				self.root.ids.room_side_enter_left.disabled = False

	# # /\------INTERFACE BLOCKER------/\ # #

	async def set_data_settings(self, state: str):
		def set_null(item):
			item.children[1].text = ""

		match state:
			case "null":
				tuple(map(set_null, self.room_settings))
			case 'min':
				self.root.ids.bots_can_box.children[1].text = self.min_parameter("bots_can")
				self.root.ids.users_quantity_box.children[1].text = self.min_parameter("users_quantity")
				self.root.ids.ball_radius_onl_box.children[1].text = self.min_parameter("ball_radius")
				self.root.ids.ball_speed_onl_box.children[1].text = self.min_parameter("ball_speed")
				self.root.ids.ball_boost_onl_box.children[1].text = self.min_parameter("ball_boost")
				self.root.ids.platform_speed_onl_box.children[1].text = self.min_parameter("platform_speed")
				self.root.ids.platform_height_onl_box.children[1].text = self.min_parameter("platform_height")
				self.root.ids.platform_width_onl_box.children[1].text = self.min_parameter("platform_width")

	# /\------ID ACTIONS------/\ #

	# V------OTHER ACTIONS------V #

	def testing_server_work(self) -> bool:
		try:
			testing()
			return True
		except exceptions.ConnectionError:
			return False
		except Exception:
			return False

	def min_parameter(self, setting_name: str) -> str:
		return f"{self.MENU_DATA[setting_name][0]}"

	async def open_git(self, link: str) -> None:
		open(link)

	async def get_error_alert(self, exception: Exception):
		print(type(exception).__name__)
		match type(exception).__name__:
			case "ConnectionError":
				header = 'Проблемы с подключением'
				support_text = "На данный момент сервер отключен. "
				"Для устранения проблемы свяжитесь с gamedev`ом, "
				"либо подождите, пока сервер не запуститься вновь."
			case "ResponseException":
				if "status_code" in exception.args[0] and "message" in exception.args[0]:
					header = f'Проблема - {exception.args[0]["status_code"]}'
					support_text = f"{exception.args[0]["message"]}"
				else:
					header = 'Что - то'
					support_text = f"{exception} - {exception.args}"
			case "TheRoomHasBeenDeleted":
				header = 'Сообщение'
				support_text = "Комната была удалена хостом комнаты. Вы вышил из комнаты."
				asynckivy.start(self.exit_from_room())
			case _:
				header = f'Ошибка - {type(exception).__name__}'
				support_text = f"{str(exception)}\n{extract_tb(exception.__traceback__)}"

		self.DIALOG_MANAGER("alert", header=header, support_text=support_text)

	# /\------OTHER ACTIONS------/\ #

	# V------ROOM MANAGER------V #

	async def get_search_result(self, users_quantity: int = None, with_bots: bool = None, with_opens: bool = None):
		try:
			response = room_all(is_open=with_opens, names=True, user_limit=users_quantity, bots=with_bots)
			if "status_code" not in response:
				asynckivy.start(self.SEARCH_ROOM_MANAGER.set_rooms(response))
				return response
			else:
				raise ResponseException(response)
		except Exception as exception:
			self.root.current = "game_start_menu"
			asynckivy.start(self.get_error_alert(exception))

	async def search_rooms(self, **filters):
		if filters['users_quantity'].isdigit():
			filters['users_quantity'] = int(filters['users_quantity'])
			filters["users_quantity"] = filters['users_quantity'] if 0 < filters['users_quantity'] < 7 else 0
		else:
			filters['users_quantity'] = 0
		while self.root.current == "room_search_list":
			asynckivy.start(self.get_search_result(**filters))
			await asynckivy.sleep(5)

	async def filter_search(self):
		items = self.DIALOG_MANAGER["search_filter"].children[0].children[1].children[0].children[0].children
		field_id = items[-1].text
		field_user_quantity = items[-3].text
		checkbox_bots = items[-5].children[0].children[0].active
		checkbox_only_opens = items[-7].children[0].children[0].active
		self.DIALOG_MANAGER("search_filter")
		self.root.current = "room_search_list"
		asynckivy.start(self.search_rooms(
			users_quantity=field_user_quantity,
			with_bots=checkbox_bots,
			with_opens=checkbox_only_opens
		))

	async def room_enter(self, room_id: str):
		try:
			response = room_enter(int(room_id), int(self.DATA["id"]))
			if not response:
				self.root.current = "online_room_creation_menu"
				self.set_state("enter_room")
				asynckivy.start(self.enable_btn("exit"))
				self.DATA['current_room_id'] = room_id
				self.DATA["room_role"] = "user"
				asynckivy.start(self.update_current_users())
				asynckivy.start(self.update_current_room_settings_user())
			elif type(response) is dict:
				raise ResponseException(response)
		except Exception as exception:
			asynckivy.start(self.get_error_alert(exception))

	async def pre_room_create(self):
		if self.root.ids.bots_can_box.disabled == True:
			self.DIALOG_MANAGER('alert', header='Инструкция',
								support_text='Укажите нужные настройки в поле "Параметры комнаты"'
											 ' и нажимте на кнопку создания комнаты')
			self.set_state("pre_create_room")
		else:
			asynckivy.start(self.room_create())

	async def room_create(self):
		try:
			response = room_create(self.DATA['id'], *map(lambda item: item.children[1].text, self.room_settings))

			if type(response) is int:
				self.set_state("create_room")
				self.DATA['current_room_id'] = response
				self.DATA["room_role"] = "host"
				asynckivy.start(self.update_current_users())
				asynckivy.start(self.update_current_room_settings_host())
			elif type(response) is dict:
				raise ResponseException(response)
		except Exception as exception:
			asynckivy.start(self.get_error_alert(exception))

	async def update_current_users(self):
		while self.DATA['current_room_id']:
			try:
				asynckivy.start(self.get_users_in_room())
			except Exception as exception:
				print("update_current_users")
				asynckivy.start(self.get_error_alert(exception))
				break

			await asynckivy.sleep(2)  # 1 on release

	async def update_current_room_settings_user(self):
		while self.DATA['current_room_id']:
			try:
				asynckivy.start(self.get_room_settings())
				asynckivy.start(self.enter_possibility_check())
			except Exception as exception:
				print("update_current_room_settings_user")
				asynckivy.start(self.get_error_alert(exception))
				break

			await asynckivy.sleep(2)  # 1 on release

	async def get_room_settings(self):
		def active(b):
			b.disabled = False
		tuple(map(active, self.room_settings))
		try:
			response = room_get_settings(self.DATA['id'])
			if 'status_code' not in response:
				for name, box_name in zip(response, boxs := dict(zip((
						"bots",
						"users_quantity",
						"ball_radius",
						"ball_speed",
						"ball_boost",
						"platform_speed",
						"platform_height",
						"platform_width"
				), tuple(map(lambda s: s.children[1], self.room_settings))))):
					boxs[name].text = str(response[name])
			else:
				raise ResponseException(response)
		except Exception as exception:
			print("get_room_settings")
			asynckivy.start(self.get_error_alert(exception))

	async def update_current_room_settings_host(self):
		while self.DATA['current_room_id']:
			try:
				asynckivy.start(self.set_room_settings_box())
			except Exception as exception:
				print("update_current_room_settings_host")
				asynckivy.start(self.get_error_alert(exception))
				break

			await asynckivy.sleep(2)  # 1 on release

	async def enter_possibility_check(self):
		response = False
		while not response and self.DATA['current_room_id']:
			try:
				response = room_can_enter(self.DATA['id'])
				if type(response) is bool and response:
					self.root.ids.room_btn_play.disabled = False
					break
			except Exception as exception:
				print("enter_possibility_check")
				asynckivy.start(self.get_error_alert(exception))
				break

			await asynckivy.sleep(2)  # 1 on release

	async def set_room_settings_box(self):
		try:
			response = room_update_settings(
				self.DATA['current_room_id'],
				**dict(zip(("bots", "users_quantity", "ball_radius", "ball_speed", "ball_boost", "platform_speed",
							"platform_height", "platform_width"), tuple(map(lambda s: s.text, self.room_settings))))
			)
			if type(response) is dict:
				raise ResponseException(response)
		except Exception as exception:
			asynckivy.start(self.get_error_alert(exception))

	async def get_users_in_room(self):
		try:
			response = room_user_ids_divine(self.DATA['current_room_id'])
			if type(response) is int:
				pass
			elif "status_code" not in response:
				asynckivy.start(self.USER_MANAGER.set_users(response))
			elif response['status_code'] == 142:
				raise TheRoomHasBeenDeleted()
			else:
				raise ResponseException(response)
		except Exception as exception:
			asynckivy.start(self.get_error_alert(exception))

	async def exit_from_room(self):
		try:
			response = room_leave(int(self.DATA['id']), 'f')
			if not response:
				self.DATA["current_room_id"] = 0
				self.set_state("not_room")
			elif type(response) is dict:
				raise ResponseException(response)
		except Exception as exception:
			asynckivy.start(self.get_error_alert(exception))

	async def room_movement(self, side: str) -> None:
		try:
			response = user_side_change(self.DATA['id'], side)
			if not response:
				asynckivy.start(self.set_enter_block(side))
			else:
				raise ResponseException(response)
		except Exception as exception:
			asynckivy.start(self.get_error_alert(exception))

	@property
	def window_size(self) -> tuple[int, int]:
		monitor = tuple(filter(lambda m: m.is_primary, get_monitors()))[0]
		return monitor.width, monitor.height

	def counter(self, action: str) -> None | dict:
		match action:
			case "update":
				self.root.ids.left_counter.text = "0"
				self.root.ids.right_counter.text = "0"
			case "plus_left":
				self.root.ids.left_counter.text = str(int(self.root.ids.left_counter.text) + 1)
			case "plus_right":
				self.root.ids.right_counter.text = str(int(self.root.ids.right_counter.text) + 1)
			case "get":
				return {"left": int(self.root.ids.left_counter.text), "right": int(self.root.ids.right_counter.text)}


# /\------ROOM MANAGER------/\ #

if __name__ == "__main__":
	try:
		app = DigitalPong()
		app.run()
	finally:
		try:
			data = download("data")
			user_log('out', username=data["username"], password=data["password"])
			room_leave(data['id'], 't')
		except Exception as error:
			print("finally: ", type(error).__name__, str(error))
