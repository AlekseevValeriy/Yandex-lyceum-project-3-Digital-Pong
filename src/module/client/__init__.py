import logging

# DEBUG -> INFO -> WARNING -> ERROR -> CRITICAL
# loggin.debug(Any)
logging.basicConfig(level=logging.DEBUG)


class Main:
    def __init__(self, *args, **kwargs) -> None:
        ...

    def main(self, *args, **kwargs) -> None:
        ...


if __name__ == "__main__":
    main = Main()
    main.main()
