import logging
import re


def red(text):
    return color_text(text, "RED")


def green(text):
    return color_text(text, "GREEN")


def yellow(text):
    return color_text(text, "YELLOW")


def blue(text):
    return color_text(text, "BLUE")


def magenta(text):
    return color_text(text, "MAGENTA")


def cyan(text):
    return color_text(text, "CYAN")


def white(text):
    return color_text(text, "WHITE")


COLORS = ("BLACK", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE")


def color_text(text, color_name, bold=False):
    if color_name in COLORS:
        return "\033[{0};{1}m{2}\033[0m".format(
            int(bold), COLORS.index(color_name.upper()) + 30, text
        )
    return text


def un_color_text(text):
    re_color_codes = re.compile(r"\033\[(\d;)?\d+m")
    return re_color_codes.sub("", text)


LEVELS = {
    "WARNING": color_text(" WARN", "RED"),
    "INFO": color_text(" INFO", "CYAN"),
    "DEBUG": color_text("DEBUG", "BLUE"),
    "CRITICAL": color_text(" CRIT", "MAGENTA"),
    "ERROR": color_text("ERROR", "RED"),
}

keywords = {
    "Traceback": "RED",
    "File": "MAGENTA",
}


class LogFormatter(logging.Formatter):
    def format(self, r, abort=False):
        """Given a LogRecord object r, return a formatted log message.

        """
        message = r.getMessage()

        s = "%(level)s %(file)s-%(func)s-%(line)s: " % {
            "level": LEVELS[getattr(r, "levelname")],
            "file": color_text(getattr(r, "filename"), "WHITE"),
            "func": color_text(getattr(r, "funcName"), "GREEN"),
            "line": color_text(getattr(r, "lineno"), "BLUE"),
        }

        # color keywords
        for word, color in keywords.items():
            message = message.replace(word, color_text(word, color))

        # Indent the message so it is aligned
        if "\n" in message:
            indent_length = len(un_color_text(s))
            message = message.replace("\n", "\n" + " " * indent_length)

        if r.exc_info:
            exc_text = self.formatException(r.exc_info)
            message = message + " : " + exc_text

        return s + message
