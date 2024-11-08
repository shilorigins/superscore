"""
`superscore ui` opens up the main application window
"""
import argparse
import sys
from typing import Optional

from qtpy.QtWidgets import QApplication

from superscore.client import Client
from superscore.widgets.window import Window

MAX_DEFAULT_WIDTH = 1400
MAX_DEFAULT_HEIGHT = 800


def build_arg_parser(argparser=None):
    if argparser is None:
        argparser = argparse.ArgumentParser()

    return argparser


def main(*args, client: Optional[Client] = None, **kwargs):
    app = QApplication(sys.argv)
    main_window = Window(client=client)

    primary_screen = app.screens()[0]
    screen_width = primary_screen.geometry().width()
    screen_height = primary_screen.geometry().height()
    width = min(int(screen_width*.5), MAX_DEFAULT_WIDTH)
    height = min(int(screen_height*.5), MAX_DEFAULT_HEIGHT)
    # move window rather creating a QRect because we want to include the frame geometry
    main_window.setGeometry(0, 0, width, height)
    center = primary_screen.geometry().center()
    delta = main_window.geometry().center()
    main_window.move(center - delta)
    main_window.show()
    app.exec()
