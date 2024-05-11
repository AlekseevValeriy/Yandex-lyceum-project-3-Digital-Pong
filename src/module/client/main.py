from typing import Callable

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
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon, MDListItemSupportingText
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.widget import Widget
from kivymd.uix.dialog import (MDDialogIcon, MDDialogHeadlineText, MDDialogSupportingText,
							   MDDialogContentContainer, MDDialogButtonContainer)
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldMaxLengthText

from data_loader import download, upload, download_themes

from src.module.client.widgets.custommdcard import MDFloatCard, MDBoxCard
from src.module.client.widgets.custommddialog import CustomMDDialog
from dialog_manager import DialogManager


class DigitalPong(MDApp):
	# V------DATA------V #
	STRUCTURE = "../../../data/structure.kv"

	THEMES = download_themes()
	SETTINGS = download("settings")
	DATA = download("data")
	get_situation = lambda n: n.split('_')[-1]

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
		if not self.SETTINGS['situation']:
			# raise dialog situation choice
			...

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
					on_release=lambda item: asynckivy.start(self.choice_state_enter("offline", item))
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
					on_release=lambda item: asynckivy.start(self.choice_state_enter("online", item))

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
					# on_release=self.login
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
					# on_release=self.registration
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
						text="0123456789ABCDEF"
					),
					theme_bg_color="Custom",
					md_bg_color=self.theme_cls.transparentColor,
					# on_release=self.rename_confirm
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
					# on_release=self.delete_confirm
				),
				MDButton(
					MDButtonText(
						text="ВЫЙТИ ИЗ АККАУНТА"
					),
					style="text",
					# on_release=self.quit_confirm
				),
				spacing=dp(8)
			),
		)
		unseen_circumstances_alert = lambda **kwargs: CustomMDDialog(
			MDDialogHeadlineText(
				text="Непредвиденные обстоятельства"
			),
			MDDialogSupportingText(
				text=kwargs["message"],
				halign="left"
			),
			MDDialogButtonContainer(
				Widget(),
				MDButton(
					MDButtonText(text="ОК"),
					style="text"
					# on_release=lambda item: self.dismiss_dialog(item, progenitor=4)
				),
				spacing="8dp"
			),
		)
		self.DIALOG_MANAGER["login_alert"] = unseen_circumstances_alert(
			message="Пользователя с такими данными не существует. "
					"Пожалуйста, введите корректные данные, либо зарегистрируете новый аккаунт.")
		self.DIALOG_MANAGER["registration_alert"] = unseen_circumstances_alert(
			message="Пользователь с таким именем уже существует. "
					"Пожалуйста, введите другое имя.")

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
					# MDTextFieldHelperText(
					# 	text="Helper text",
					# 	mode="persistent"
					# ),
					MDTextFieldMaxLengthText(
						max_text_length=16) if kwargs['reg'] else None,
					mode="outlined"
				),
				MDTextField(
					MDTextFieldHintText(
						text="Пароль"
					),
					# MDTextFieldHelperText(
					# 	text="Helper text",
					# 	mode="persistent"
					# ),
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
					# on_release=self.back_to_user_log
				),
				MDButton(
					MDButtonText(text=kwargs["confirm_text"]),
					style="text",
					# on_release=kwargs["confirm_action"]
				),
				spacing="8dp",
			),
		)
		self.DIALOG_MANAGER["registration"] = data_input(
			icon="account-plus",
			confirm_text="ЗАРЕГЕСТРИРОВАТЬСЯ",
			# confirm_action=lambda item: self.log_reg_confirm(item, variant="registration"),
			reg=True)
		self.DIALOG_MANAGER["login"] = data_input(
			icon="account-badge",
			confirm_text="ВОЙТИ",
			# confirm_action=lambda item: self.log_reg_confirm(item, variant="login"),
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
					# on_release=lambda item: self.dismiss_dialog(item, progenitor=4)
				),
				MDButton(
					MDButtonText(text="ПОДТВЕРДИТЬ"),
					style="text",
					# on_release=kwargs['confirm_action']
				),
				spacing="8dp",
			),
		)
		self.DIALOG_MANAGER["rename_warning"] = confirm_alert(
			message="Вы точно желаете сменить имя своего аккаунта?",
			# confirm_action=self.rename
		)
		self.DIALOG_MANAGER["delete_account_warning"] = confirm_alert(
			message="Вы точно желаете удалить свой аккаунт навсегда?",
			# confirm_action=self.delete
		)
		self.DIALOG_MANAGER["exit_from_account_warning"] = confirm_alert(
			message="Вы точно желаете выйти из своего аккаунта?",
			# confirm_action=self.quit
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
					# MDTextFieldHelperText(
					# 	text="Helper text",
					# 	mode="persistent"
					# ),
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

	def open_menu(self, item: Widget, variant: str) -> None:
		def action(situation: str, offline: Callable, online: Callable) -> Callable:
			match situation:
				case "ofl":
					return offline
				case "onl":
					return online

		match variant:
			case "bots_can":
				variants = [True, False]
				widget = self.root.ids.bots_can
			case "users_quantity":
				variants = [*range(1, 7)]
				widget = self.root.ids.users_quantity
			case "platform_speed_ofl" | "platform_speed_onl":
				variants = [*range(1, 11)]
				widget = action(self.get_situation(variant),
								self.root.ids.platform_speed_ofl, self.root.ids.platform_speed_onl)
			case "ball_speed_ofl" | "ball_speed_onl":
				variants = [*range(1, 21)]
				widget = action(self.get_situation(variant),
								self.root.ids.ball_speed_ofl, self.root.ids.ball_speed_onl)
			case "ball_radius_ofl" | "ball_radius_onl":
				variants = [*range(1, 11)]
				widget = action(self.get_situation(variant),
								self.root.ids.ball_radius_ofl, self.root.ids.ball_radius_onl)
			case "platform_width_ofl" | "platform_width_onl":
				variants = [*range(5, 21)]
				widget = action(self.get_situation(variant),
								self.root.ids.platform_width_ofl, self.root.ids.platform_width_onl)
			case "platform_height_ofl" | "platform_height_onl":
				variants = [*range(40, 201)]
				widget = action(self.get_situation(variant),
								self.root.ids.platform_height_ofl, self.root.ids.platform_height_onl)
			case "ball_boos_ofl" | "ball_boos_onl":
				variants = [*map(lambda x: f"{x / 10:.1f}", range(10, 21))]
				widget = action(self.get_situation(variant),
								self.root.ids.ball_boos_ofl, self.root.ids.ball_boos_onl)
			case _:
				variants = [None]
				widget = None

		menu_items = [
			{
				"text": f"{i}",
				"on_release": lambda x=f"{i}": self.menu_callback(widget, x),
			} for i in variants
		]

		MDDropdownMenu(caller=item, items=menu_items, max_height=300).open()

	def menu_callback(self, widget: Widget, text_item: str) -> None:
		if widget:
			widget.text = text_item

	def create_room(self):
		match self.SETTINGS['situation']:
			case "offline":
				self.root.current = "offline_room_creation_menu"
			case "online":
				self.root.current = "online_room_creation_menu"

	# V------DIALOG ACTIONS------V #

	async def choice_state_enter(self, situation, *args):
		self.SETTINGS['situation'] = situation
		settings = download("settings")
		settings['situation'] = self.SETTINGS['situation']
		upload('settings', settings)
		asynckivy.start(self.set_icon('signal' if self.SETTINGS['situation'] == 'online' else "signal-off"))
		self.DIALOG_MANAGER("situation_choice")

	# V------ID ACTIONS------V #

	async def set_username(self, username: str = None) -> None:
		self.root.ids.user_name = username if username else self.DATA["username"]

	async def set_icon(self, icon: str) -> None:
		self.root.ids.situation_icon.icon = icon


if __name__ == "__main__":
	try:
		app = DigitalPong()
		app.run()
	finally:
		...
