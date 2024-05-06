from kivymd.uix.behaviors import HoverBehavior
from kivymd.uix.floatlayout import MDFloatLayout


class MDFloatCard(MDFloatLayout, HoverBehavior):
	BG_COLOR = (0.890625, 0.87890625, 0.91015625, 0.99609375)  # 228, 225, 233
	BG_COLOR_MOTION = (0.828125, 0.81640625, 0.84765625, 0.99609375)  # 212, 209, 217
	BG_COLOR_CLICK = (0.796875, 0.78515625, 0.81640625, 0.99609375)  # 204, 201, 209

	def on_enter(self, *args):
		self.md_bg_color = self.BG_COLOR_MOTION

	def on_leave(self):
		self.md_bg_color = self.BG_COLOR

	def on_touch_down(self, touch):
		if self.collide_point(*touch.pos):
			self.md_bg_color = self.BG_COLOR_CLICK

	def on_touch_up(self, touch):
		if self.collide_point(*touch.pos):
			self.md_bg_color = self.BG_COLOR_MOTION