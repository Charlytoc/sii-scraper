import sys

class Printer:
    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m",
    }

    @staticmethod
    def _print_with_color(color, *args, **kwargs):
        color_code = Printer.COLORS.get(color, Printer.COLORS["reset"])
        print(f"{color_code}", end="")
        print(*args, **kwargs)
        print(Printer.COLORS["reset"], end="")

    @classmethod
    def red(cls, *args, **kwargs):
        cls._print_with_color("red", *args, **kwargs)

    @classmethod
    def green(cls, *args, **kwargs):
        cls._print_with_color("green", *args, **kwargs)

    @classmethod
    def blue(cls, *args, **kwargs):
        cls._print_with_color("blue", *args, **kwargs)

    @classmethod
    def yellow(cls, *args, **kwargs):
        cls._print_with_color("yellow", *args, **kwargs)

    @classmethod
    def magenta(cls, *args, **kwargs):
        cls._print_with_color("magenta", *args, **kwargs)

    @classmethod
    def cyan(cls, *args, **kwargs):
        cls._print_with_color("cyan", *args, **kwargs)

    @classmethod
    def white(cls, *args, **kwargs):
        cls._print_with_color("white", *args, **kwargs)

    @classmethod
    def custom_color(cls, rgb, *args, **kwargs):
        """
        Print text using an RGB color.
        :param rgb: Tuple of integers (r, g, b) where 0 <= r, g, b <= 255
        """
        r, g, b = rgb
        color_code = f"\033[38;2;{r};{g};{b}m"
        print(f"{color_code}", end="")
        print(*args, **kwargs)
        print(Printer.COLORS["reset"], end="")

# Example Usage
if __name__ == "__main__":
    Printer.red("This is red text!")
    Printer.green("This is green text!")
    Printer.blue("This is blue text!")
    Printer.custom_color((255, 165, 0), "This is orange text!")
