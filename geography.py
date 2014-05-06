#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import random

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.properties import ObjectProperty
from kivy.clock import Clock

try:
    import android
except ImportError:
    Window.size = [500, 600]


countries = {
    '001': ('China', (808, 258, 3580, 379)),
    '002': ('France', (524, 198, 2146, 311)),
    '003': ('Egypt', (624, 304, 143, 1)),
    '004': ('Mexico', (44, 330, 1, 1))
}


BOTTOM_BORDER = Window.height / 4


class Map(Image):

    def __init__(self):
        super(Map, self).__init__()

        # self.source = 'img/world_map.gif'
        # width, height = 4500, 2234
        # print self.width, self.height
        width, height = 1350, 670
        self.init_size = width, height
        self.init_pos = -width / 2, (-height / 2) + BOTTOM_BORDER

        self.pos = self.init_pos
        self.size = self.init_size
        self.move_to()
        self.keep_data = True

        # self.country = random.choice(countries.keys())
        # print countries[country]

        # print self.pos, self.size

    def move_to(self, x=0, y=0):

        self.country = random.choice(countries.keys())
        self.source = 'img/geography/%s.png' % self.country
        min_x, min_y, max_x, max_y = countries[self.country][1]
        x, y, = min_x, min_y

        x = -x
        y = - (self.height - y) + BOTTOM_BORDER
        # y = self.y - self.height - y

        animation = Animation(x=x, y=y)
        #& Animation(size=new_size, duration=2)
        # animation.bind(on_complete=self.move_to_starting_position)
        animation.bind(on_complete=self.move_to)
        animation.start(self)
        # print self.size

    def move_to_starting_position(self, *args):
        x, y = self.init_pos
        animation = Animation(x=x, y=y, size=self.init_size)
        animation.bind(on_complete=self.move_to)
        animation.start(self)

    def p(self, *args):
        print self.pos, self.size


class GeographyWindow(Widget):

    world_map = ObjectProperty()
    bottom_border = BOTTOM_BORDER

    def __init__(self):
        self.size = Window.size
        Window.clearcolor = (0.5, 0.7, 0.8, 1)
        super(GeographyWindow, self).__init__()
        self.world_map = Map()
        self.add_widget(self.world_map)
        # Clock.schedule_once(self.world_map.move_to, 2)
        # Clock.schedule_once(self.world_map.move_to_starting_position, 5)

    def on_touch_move(self, t):
        print t.x, t.y


class GeographyApp(App):

    def build(self):
        geography_window = GeographyWindow()
        return geography_window


if __name__ == '__main__':
    GeographyApp().run()
    # print dir(Map())
