#!/usr/bin/env python
# -*- coding: UTF-8 -*-


'''
So. This is app made for kivy contest 2014.

It's orientated mostly on kids but i guess adults
can play it too.

Code by me.
Art by my friend.
Music and sounds are from
http://incompetech.com
and
https://www.freesound.org

Fonts also free.

Tested on:
Elementary OS (Ubuntu) with python 2 and kivy 1.8.0
Android 4.4 in QPython.

If you have anything to say to me:
game.code.die@gmail.com
I'll be glad if you tell me about bugs and suchlike.

Some notes:

Main menu color changes every time. - Good.
There one bug in geo app whe running on android. - Bad,
it gives wrong answer.
For this moment I don't know why it's happening. Don't get mad.
'''


import random
import math
import threading
import pickle
# import Queue

import kivy
kivy.require('1.7.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.core.audio import SoundLoader

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.animation import Animation

from kivy.uix.label import Label
from kivy.uix.button import Button

from kivy.properties import NumericProperty, ListProperty

import cows
import koalas
import geography


PLATFORM = kivy.platform()
FPS = 1.0 / 60.0
FONT = 'fonts/Cicle_Fina.ttf'
FONT_SIZE = Window.height // 12
QUANT = Window.width / 600

COWS = 'Cows'
KOALAS = 'Koalas'
GEOGRAPHY = 'Geography'
LOADING_TEXT = 'Some data is being loaded'

if not PLATFORM == 'android':
    Window.size = [600, 800]


class Circle(Widget):

    color = ListProperty([0, 0, 0])

    def __init__(self, x, y, max_width):
        super(Circle, self).__init__()

        self.size = [0, 0]
        self.color = [random.random()] + [
            random.uniform(0.7, 1) for _ in range(2)]
        self.max_width = max_width
        self.x_y = [x, y]
        self.pos = [x, y]
        Clock.schedule_interval(self.increase_size, FPS)

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
        self.geo_map = None
        self.colors_dict = None
        self.koalas_sound = None
        self.cows_sound = None
        self.geo_sound = None

        self.sound = SoundLoader.load('sound/main.ogg')
        self.sound.loop = True

        self.display_menu()

        for f in ('koalas.kv', 'cows.kv', 'geography.kv'):
            with open(f, 'r') as kv_file:
                Builder.load_string(kv_file.read())

        threading.Thread(target=self.__load_data).start()

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
        b_texts = ('Know the\nWorld', 'Feed Koalas', 'Save Cows')

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
                            border=(0, 0, 0, 0),
                            halign='center',
                            valign='middle'
                            )

            button.on_release = lambda a=app: self.start_application(a)
            self.add_widget(button)

        self.sound.play()
        self.add_circle()

        if self.colors_dict is not None:
            return
        self.loading_label = Label(text=LOADING_TEXT,
                                   center=(Window.width-self.buttons_offset - 30, self.buttons_offset / 2),
                                   halign='right',
                                   valign='middle',
                                   font_name=FONT,
                                   font_size=30,
                                   color=self.color,
                                   markup=True)
        self.add_widget(self.loading_label)
        Clock.schedule_interval(self.__add_point_to_loading_label, 0.5)

    # i'm doing this in big hurry. Don't be rush
    def __add_point_to_loading_label(self, *args):
        if self.colors_dict is not None:
            self.remove_widget(self.loading_label)
            return False
        if len(self.loading_label.text) >= len(LOADING_TEXT + '...'):
            self.loading_label.text = LOADING_TEXT
        self.loading_label.text += '.'

    def __load_data(self, *args):
        self.koalas_sound = SoundLoader.load('sound/koalas.ogg')
        self.cows_sound = SoundLoader.load('sound/cows.ogg')
        with open('colors_dict.pkl', 'rb') as c:
            self.colors_dict = pickle.load(c)

    def add_circle(self, timing=None):
        # print self.geo_map
        if len([c for c in self.children if isinstance(c, Circle)]) > 10:
            Clock.schedule_once(self.add_circle, 5)
            return

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

    def __load_cows_app(self, *args):
        if self.cows_sound is None:
            return True
        else:
            self.clear_widgets()
            self.add_widget(cows.CowsMainWidget(self.cows_sound))
            return False

    def __load_koalas_app(self, *args):
        if self.koalas_sound is None:
            return True
        else:
            self.clear_widgets()
            self.add_widget(koalas.KoalasMainWidget(self.koalas_sound))
            return False

    def __load_geo_app(self, *args):
        if self.colors_dict is None and self.geo_sound is None:
            return True
        else:
            self.clear_widgets()
            self.add_widget(geography.GeographyMainWindow(self.colors_dict, self.geo_sound))
            return False

    def run(self, application):
        # return
        self.unschedule_all()
        label = Label(text='Loading',
                      center=(self.center[0], 4 * self.buttons_offset),
                      halign='center',
                      valign='middle',
                      font_name=FONT,
                      font_size=FONT_SIZE,
                      color=self.color,
                      markup=True)
        self.add_widget(label)

        if application == KOALAS:
            f = self.__load_koalas_app
        elif application == COWS:
            f = self.__load_cows_app
        elif application == GEOGRAPHY:
            f = self.__load_geo_app
        else:
            pass
        Clock.schedule_interval(f, 0.1)
        self.sound.stop()

    def start_application(self, application):
        duration = 0.7
        for child in self.children:
            x = random.choice((-Window.width, Window.width))
            y = random.choice((-Window.height, Window.height))
            anim = Animation(x=x, y=y, d=duration)
            anim.start(child)
        Clock.schedule_once(lambda t: self.run(application), duration)

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
