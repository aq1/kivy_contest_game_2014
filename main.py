#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random
import math

import kivy
kivy.require('1.7.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.animation import Animation

from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.properties import NumericProperty, ListProperty

import cows
import koalas

try:
    import android
except ImportError:
    Window.size = [600, 800]


FPS = 1.0 / 60.0
FONT = 'fonts/Cicle_Fina.ttf'
FONT_SIZE = Window.height // 12
QUANT = Window.width / 600

COWS = 'Cows'
KOALAS = 'Koalas'
GEOGRAPHY = 'Geography'


class Circle(Widget):

    color = ListProperty([0, 0, 0])
    # color = NumericProperty()

    def __init__(self, x, y, max_width):
        super(Circle, self).__init__()

        self.size = [0, 0]
        self.color = [random.random()] + [
            random.uniform(0.7, 1) for _ in range(2)]
        # print self.color
        self.max_width = max_width
        self.x_y = [x, y]
        self.pos = [x, y]
        Clock.schedule_interval(self.increase_size, FPS)
        # print 'added', self.pos, self.size, self.color

    def increase_size(self, timing=None):
        if self.width >= self.max_width:
            Clock.schedule_once(self.decrease_size)
            return False

        self.width += QUANT
        self.center = self.x_y
        self.size = [self.width, self.width]

    def decrease_size(self, timing=None):
        self.width -= QUANT
        self.size = [self.width, self.width]
        self.center = self.x_y
        Clock.schedule_once(self.decrease_size, FPS)

        if self.width <= 0:
            try:
                self.parent.remove_widget(self)
            except AttributeError:
                del self
            return False

    def destroy(self):
        self.parent.remove_widget(self)


class MainWindow(Widget):

    buttons_offset = NumericProperty(Window.height / 6)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.size = Window.size
        self.direction = [0, 0]
        self.display_menu()

        for f in ('koalas.kv', 'cows.kv', 'geography.kv'):
            with open(f, 'r') as kv_file:
                Builder.load_string(kv_file.read())

    def display_menu(self):
        self.color = self.hsv_to_rgb(random.randint(0, 360)) + (1,)
        Window.clearcolor = self.color
        self.color = 1, 1, 1, 1
        self.clear_widgets()
        label = Label(text='Do you want to:',
                      center=(self.center[0], 5 * self.buttons_offset),
                      halign='center',
                      valign='middle',
                      font_name=FONT,
                      font_size=FONT_SIZE,
                      color=self.color,
                      markup=True)
        self.add_widget(label)

        apps = (GEOGRAPHY, KOALAS, COWS)
        b_texts = ('Learn Geography', 'Feed Koalas', 'Save Cows')

        for y, text, app in zip(range(1, len(b_texts) + 1), b_texts, apps):
            button = Button(text=text,
                            size=(self.width / 1.5, self.height / 7),
                            x=self.center[0] - self.width / 3,
                            y=y * self.buttons_offset,
                            font_name=FONT,
                            font_size=FONT_SIZE - 10,
                            color=self.color,
                            markup=True,
                            background_normal='img/buttons/button_01.png',
                            background_down='img/buttons/button_02.png',
                            halign='center',
                            )

            button.on_release = lambda a=app: self.start_application(a)
            self.add_widget(button)
        self.add_circle()

    def add_circle(self, timing=None):
        x = random.randint(0, self.width)
        y = random.randint(0, self.height)
        max_width = random.randint(self.height / 10, self.height / 2)

        self.add_widget(Circle(x, y, max_width), len(self.children))
        Clock.schedule_once(self.add_circle, random.uniform(0.2, 1.5))

    def unschedule_all(self, timing=None):
        Clock.unschedule(self.add_circle)
        for c in self.children:
            try:
                c.destroy()
            except AttributeError:
                pass
        self.clear_widgets()

    def run(self, application):
        # return
        self.unschedule_all()
        if application == KOALAS:
            self.add_widget(koalas.KoalasMainWidget())
        elif application == COWS:
            self.add_widget(cows.CowsMainWidget())
        else:
            pass

    def start_application(self, application):
        duration = 0.7
        for child in self.children:
            x = random.choice((-Window.width, Window.width))
            y = random.choice((-Window.height, Window.height))
            anim = Animation(x=x, y=y, d=duration)
            anim.start(child)
        Clock.schedule_once(lambda t: self.run(application), duration)

        # Clock.schedule_once(self.unschedule_all, 1)

    @staticmethod
    def hsv_to_rgb(h, s=100, v=100):
        h = float(h)
        h_i = math.floor(h / 60)
        v_min = ((100 - s) * v) / 100
        a = (v - v_min) * ((h % 60) / 60)
        v_inc = v_min + a
        v_dec = v - a

        if h_i == 0:
            r, g, b = v, v_inc, v_min
        elif h_i == 1:
            r, g, b = v_dec, v, v_min
        elif h_i == 2:
            r, g, b = v_min, v, v_inc
        elif h_i == 3:
            r, g, b = v_min, v_dec, v
        elif h_i == 4:
            r, g, b = v_inc, v_min, v
        elif h_i == 5:
            r, g, b = v, v_min, v_dec
        else:
            return 0, 0, 0

        r, g, b = [x / 100 for x in (r, g, b)]
        return r, g, b


class MainApp(App):

    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        main_window = MainWindow()
        return main_window


if __name__ == '__main__':
    MainApp().run()
