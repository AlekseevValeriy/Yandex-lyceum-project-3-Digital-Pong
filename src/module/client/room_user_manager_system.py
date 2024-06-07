from kivymd.uix.floatlayout import MDFloatLayout

type layout_list = list[MDFloatLayout, MDFloatLayout, MDFloatLayout]


class UserManager:
	EMPTY = {"left": [], "right": []}

	def __init__(self):
		self.left_children: layout_list | None = None
		self.right_children: layout_list | None = None

		self.translate = None

	async def set_users(self, users: dict[str: tuple[str]]) -> None:
		for side in users:
			if users[side]:
				for user, child in zip(self.template(users[side]), self.translate[side]):
					if user != self.get_text(child):
						self.set_text(child, user)
					self.set_color(child)
			else:
				for child in self.translate[side]:
					self.set_text(child, "")
					self.set_color(child)

	def post_start_init(self, left_box: MDFloatLayout, right_box: MDFloatLayout):
		self.left_children = tuple(reversed(left_box.children))
		self.right_children = tuple(reversed(right_box.children))

		self.translate = {"left": self.left_children, "right": self.right_children}

	def template(self, users: tuple[str]) -> tuple:
		for _ in range(3 - len(users := list(users))):
			users.append("")
		return tuple(users)

	def get_text(self, element: MDFloatLayout):
		return element.children[0].text

	def set_text(self, element: MDFloatLayout, text: str) -> None:
		element.children[0].text = text

	def set_color(self, element: MDFloatLayout) -> None:
		if self.get_text(element):
			element.md_bg_color[-1] = 1.0
		else:
			element.md_bg_color[-1] = 0.0

	def clear(self):
		for side in self.translate:
			for child in self.translate[side]:
				self.set_text(child, "")
				self.set_color(child)
