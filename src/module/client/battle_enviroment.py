from typing import Callable
from dataclasses import dataclass

import asynckivy
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.widget import Widget
from kivymd.uix.widget import MDWidget
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.graphics import Color


@dataclass
class Touch:
	touch_position = [0, 0]
	can = False

	def __call__(self, touch: list[int | float, int | float]) -> None:
		if self.can:
			self.touch_position = touch.pos

	def change_can(self, can: bool):
		self.can = can

	@property
	def x(self) -> int | float:
		return self.touch_position[0]

	@property
	def y(self) -> int | float:
		return self.touch_position[1]


class SizeConvertor:
	def __init__(self):
		type X = int
		type Y = int

		self.inner_size: tuple[X, Y] = (1000, 1000)
		self.outer_size: tuple[X, Y] | None = None

	def set_outer_size(self, outer_size: tuple[int, int]) -> None:
		self.outer_size = outer_size

	@property
	def coefficient_x(self) -> float:
		return self.inner_size[0] / self.outer_size[0]

	@property
	def coefficient_y(self) -> float:
		return self.inner_size[1] / self.outer_size[1]

	def convert_coordinates(self, coordinates: list[int | float, int | float]) -> list[float, float]:
		return [coordinates[0] * self.coefficient_x, coordinates[1] * self.coefficient_y]

	def convert_x_coordinate(self, x_coordinate: int | float) -> float:
		return x_coordinate * self.coefficient_x

	def convert_y_coordinate(self, y_coordinate: int | float) -> float:
		return y_coordinate * self.coefficient_y


class CustomBattleMDFloatLayout(MDFloatLayout):
	# offline ->								# online ->									0
	# def enter ->								# def enter ->								1
	# def create_objects ->						# def game_preparation ->					0
	# game start ->								# game start ->								1
	# def game_process ->						# def game_process ->						1 0
	# game end ->								# game end ->								1
	# def end  (play statistic) ->				# def end  (play statistic) ->				1
	# end back (set back action from MDApp)		# end back (set back action from MDApp)		1

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.my_name: str | None = None
		self.mode: str | None = None
		self.widgets_data: dict | None = {}
		self.exit_action: Callable | None = None
		self.window_size: list[int, int] | None = None
		self.children_d = {}
		self.touch = Touch()
		self.game_process = False

	def on_touch_down(self, touch):
		super().on_touch_down(touch)
		self.touch.change_can(True)

	def on_touch_up(self, touch):
		self.touch.change_can(False)

	def on_touch_move(self, touch):
		super().on_touch_move(touch)
		self.touch(touch)

	def pre_init(self, my_name: str, mode: str, widgets_data: dict, exit_action: Callable, window_size: tuple[int, int]) -> None:
		"""
		Используется перед `enter()` для постановки всех данный нужных коду - `mode`, `widgets_data`
		"""
		self.my_name = my_name
		self.mode = mode
		self.widgets_data = widgets_data
		self.exit_action = exit_action
		self.window_size = window_size

	@property
	def window_x(self) -> int:
		return self.window_size[0]

	@property
	def window_y(self) -> int:
		return self.window_size[1]

	def enter(self):
		"""
		Используется после перехода на этот макет. Выбрав режим, выполняет необходимые действия\n
		- при режиме `offline`, задаёт заранее записанные виджеты;
		- при режиме `online`, ждёт входа всех игроков на поле битвы, после задаёт виджеты
		"""
		self.clear_widgets()
		match self.mode:
			case "offline":
				self.offline_create_object()
			case "online":
				...

	def create_object(self, *data: tuple[str, str, bool] | tuple[str]) -> None:
		"""
		Создаёт объекты из принимаемых данных
		"""
		element: str
		for element in data:
			if type(element) is str:
				self.add_widget(self.ball_template(name=element))
			else:
				self.add_widget(self.platform_template(name=element[0], side=element[1], auto=element[2]))

	def offline_create_object(self):
		self.create_object(("b_1"), (self.my_name, "left", False), ("enemy", "right", True))
		self.set_positions()
		asynckivy.start(self.start_game())

	def online_create_object(self):
		...  # wait when all players are in place and then
		...  # set and create all objects
		self.set_positions()
		asynckivy.start(self.start_game())

	async def start_game(self):
		self.game_process = True
		match self.mode:
			case "offline":
				asynckivy.start(self.offline_game_process())
			case "online":
				asynckivy.start(self.online_game_process())

	async def offline_game_process(self):
		while self.game_process:
			def widget_action(widget: GameObject) -> None:
				print(widget.pos)
				match widget.type:
					case "platform":
						match widget.auto:
							case False:
								widget.move(self.touch.y)
							case True:
								widget.move(self.children_d["b_1"].center_y)
					case "ball":
						widget.move()

			tuple(map(widget_action, self.children))
			print('work')
			await asynckivy.sleep(1 / 60)

	async def online_game_process(self):
		...
		await asynckivy.sleep(1 / 60)

	def set_positions(self):
		balls = []
		left_platforms = []
		right_platforms = []

		element: GameObject
		for element in self.children:
			match element.side:
				case "left":
					left_platforms.append(element)
				case "center":
					balls.append(element)
				case "right":
					right_platforms.append(element)

		def set_y(group: list):
			for n, g in enumerate(group):
				g.set_center_y(self.window_y / (len(group) + 1))

		tuple(map(lambda game_object: game_object.set_outer_size(tuple(self.window_size)), self.children))

		set_y(balls)
		set_y(left_platforms)
		set_y(right_platforms)

		tuple(map(lambda ball: ball.set_center_x(self.window_x / 2), balls))
		tuple(map(lambda ball: ball.set_x(), left_platforms))
		tuple(map(lambda ball: ball.set_x(), right_platforms))

		for element in self.children:
			self.children_d[element.name] = element

		tuple(map(lambda element: element.set_color(), self.children))

	def ball_template(self, name: str = "") -> Widget:
		return Ball(
			name=name,
			# radius=self.widgets_data["ball_radius"],
			speed=self.widgets_data["ball_speed"],
			boost=self.widgets_data["ball_boost"]
		)

	def platform_template(self, name: str = "", side: str = "", auto: bool = False) -> Widget:
		return Platform(
			name=name,
			side=side,
			auto=auto,
			speed=self.widgets_data["platform_speed"],
			width=self.widgets_data["platform_width"],
			height=self.widgets_data["platform_height"]
		)


class GameObject(MDWidget, SizeConvertor):
	type = StringProperty("game_object")
	name = StringProperty("")
	side = StringProperty("")
	size_hint = [None, None]
	pos_confines_x = [0, 0]
	pos_confines_y = [0, 0]
	color = StringProperty('0;0;0;0')

	def set_color(self):
		# self.md_bg_color = list(map(float, self.color.split(';')))
		self.md_bg_color = 'black'
	def move(self) -> None:
		...

	def collision(self) -> None:
		...

	@property
	def half_height(self) -> int | float:
		return self.height / 2

	@property
	def half_width(self) -> int | float:
		return self.width / 2

	@property
	def outer_position(self) -> list:
		return self.convert_coordinates([self.center_x, self.center_y])

	def set_outer_size(self, outer_size: tuple[int, int]) -> None:
		super().set_outer_size(outer_size)
		self.pos_confines_x[1] = outer_size[0]
		self.pos_confines_y[1] = outer_size[1]


class Ball(GameObject):
	type = StringProperty("ball")
	name = StringProperty("b_")
	side = StringProperty("center")
	# radius = NumericProperty(0)
	speed = NumericProperty(0)
	boost = NumericProperty(0)
	color = StringProperty("0.5;0.5;0.5;1")

	@property
	def float_boost(self) -> float:
		return self.boost / 10


class Platform(GameObject):
	type = StringProperty("platform")
	speed = NumericProperty(0)
	auto = BooleanProperty(False)
	color = StringProperty("0.5;0.5;0.5;1")

	def set_x(self):
		match self.side:
			case "left":
				self.set_center_x(50 / self.coefficient_x)
			case "right":
				self.set_center_x((1000 - 50) / self.coefficient_x)

	def collision(self) -> None:
		if self.top > self.pos_confines_y[1]:
			self.y = self.pos_confines_y[1] - self.height
		elif self.y < self.pos_confines_y[0]:
			self.y = 0

	def move(self, center_y: int | float) -> None:
		self.y = center_y - self.half_height
		self.collision()

	# def set_color(self):
	# 	self.canvas.before.clear() # clear the old color
	# 	self.canvas.before.add(Color(*map(float, self.color.split(';')))) # add the new color
	# 	print(self.width, self.height, self.pos)
	# 	self.canvas.before.add(Widget(width=self.width, height=self.height, pos=self.pos)) # redraw the widget
