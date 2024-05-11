from kivymd.uix.dialog import MDDialog


class CustomMDDialog(MDDialog):
	open_already = False

	def open(self) -> None:
		super().open()
		self.open_already = True

	def dismiss(self, *args) -> None:
		super().dismiss(*args)
		self.open_already = False

	def is_open(self) -> bool:
		return self.open_already
