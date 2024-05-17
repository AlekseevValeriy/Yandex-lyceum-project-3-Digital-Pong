from kivy.metrics import dp
from kivymd.uix.button import MDButton


class CustomMDButton(MDButton):
	radius = [dp(10), dp(10), dp(10), dp(10)]
	style = "elevated"
	theme_width = "Custom"

	def on_release(self, *args) -> None:
		if not self.disabled:
			super().on_release(*args)


