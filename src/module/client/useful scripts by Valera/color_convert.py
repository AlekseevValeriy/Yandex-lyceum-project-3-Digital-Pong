def convert(rgb: tuple[int, int, int, int] | int) -> tuple[float, float, float, float]:
	match rgb.__class__.__name__:
		case "int":
			return tuple(map(lambda a: a / 256, (rgb, rgb, rgb, 256)))
		case "tuple":
			return tuple(map(lambda a: a / 256, rgb))


if __name__ == "__main__":
	color = (204, 201, 209, 255)
	print(convert(color))
