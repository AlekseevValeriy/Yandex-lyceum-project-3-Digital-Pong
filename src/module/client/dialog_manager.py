from dataclasses import dataclass

from src.module.client.widgets.custommddialog import CustomMDDialog
from kivy.uix.widget import Widget


@dataclass
class DialogManager:
	dialogs = {}

	def __call__(self, name: str = None, item: Widget = None, **kwargs) -> None:
		match bool(name):
			case True:
				match self.dialogs[name].is_open():
					case True:
						self.dialogs[name].dismiss()
					case False:
						for tag in kwargs:
							try:
								match tag:
									case "header":
										self.dialogs[name].children[0].children[1].children[2].children[0].text = kwargs[tag]
									case "support_text":
										self.dialogs[name].children[0].children[1].children[1].children[0].text = kwargs[tag]
									case "username":
										self.dialogs[name].children[0].children[1].children[0].children[0].children[3].children[1].children[0].children[0].text = kwargs[tag]
									case "identifier":
										self.dialogs[name].children[0].children[1].children[0].children[0].children[1].children[1].children[0].children[0].text = str(kwargs[tag])
							except Exception as error:
								print(type(error).__name__, str(error))
						self.dialogs[name].open()
			case False:
				def recall(dialog: CustomMDDialog) -> None:
					if dialog.is_open():
						dialog.dismiss()
				tuple(map(recall, self.dialogs.values()))

	def __setitem__(self, key, value):
		try:
			assert type(key) is str, 'TypeError'
			assert type(value) is CustomMDDialog, 'TypeError'
			assert key not in self.dialogs, 'KeyError'
			self.dialogs[key] = value
		except AssertionError as error:
			match str(error):
				case "TypeError":
					raise TypeError
				case "KeyError":
					raise KeyError

	def __getitem__(self, item: str) -> CustomMDDialog:
		try:
			assert item in self.dialogs
			return self.dialogs[item]
		except AssertionError:
			raise KeyError

	def __str__(self):
		return str(self.dialogs)


if __name__ == '__main__':
	a = DialogManager()
	print(a)
