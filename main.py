#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random
import PIL

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.vector import Vector
from kivy.clock import Clock
# from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.properties import NumericProperty, ReferenceListProperty, ListProperty
from kivy.core.image import ImageData

x, y = 100, 100
dx, dy = 50, 50


class Balloon(Widget):

    def __init__(self, x, y, dx, dy):
        super(Balloon, self).__init__()
        self.pos = [x, y]
        self.size = [dx, dy]
        # with self.canvas:
        #     Color(0.75, 1, 1, mode='hsv')
        #     Rectangle(pos=(x, y), size=(dx, dy))
            # Line(rectangle=[x, y, dx, 200])
        self.add_widget(Label(text='asdasd', center=self.center))

    def move(self):
        self.pos = Vector(0, self.parent.vel_y) + self.pos


class Cow(Widget):

    number_of_balls = NumericProperty(0)
    vel_y = NumericProperty(0)
    coords = ListProperty([_x for _x in (x - dx, x, x + dx)])

    def __init__(self):
        super(Cow, self).__init__()

        # with self.canvas:
        #     Color(1, 1, 0)
        # Line(rectangle=[x, y, dx, dy], fill=True)
        #     Rectangle(pos=(self.x, self.y), size=(dx, dy))
        Clock.schedule_interval(self.add_balloon, 1)

    def add_balloon(self, timing):
        if self.number_of_balls == 3:
            return False
        self.add_widget(
            Balloon(self.coords[self.number_of_balls], self.y + 2 * dy, dx, 2 * dy))
        self.number_of_balls += 1
        self.vel_y += 1

    def remove_balloon(self):
        self.remove_widget(self.children[self.number_of_balls])

    def move(self, timing=None):
        for child in self.children:
            try:
                child.move()
            except AttributeError:
                pass

        self.pos = Vector(0, self.vel_y) + self.pos
        # if self.number_of_balls == 0:
        #     return

        # self.y = self.y + 0.1
        # self.pos[1] = self.pos[1] + 10


class MainWindow(Widget):

    def __init__(self):
        super(MainWindow, self).__init__()

    def on_touch_down(self, touch):
        self.add_widget(Cow())
        # self.children[0].remove_balloon()

    def start(self):
        print ImageData._supported_fmts
        img = ImageData(width=50, height=100, fmt='rgb',
                        data=0, source=None, flip_vertical=True)
        # print(dir(img))

    def update(self, timing=None):
        for child in self.children:
            try:
                child.move()
            except AttributeError:
                pass


class MainApp(App):

    def build(self):
        main_window = MainWindow()
        main_window.start()
        # Clock.schedule_interval(main_window.update, 1.0 / 60.0)
        return main_window


if __name__ == '__main__':
    MainApp().run()
