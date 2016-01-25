#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import random
import pickle

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.animation import Animation
from kivy.properties import StringProperty

try:
    import Image as Img
except ImportError:
    Img = None

try:
    import android
except ImportError:
    android = None
    Window.size = [600, 700]


MAP = 'img/geography/world_map.png'
COUNTRY = 'img/geography/working_image.png'
FONT = 'fonts/Billy.ttf'
FONT_SIZE = Window.height // 12 - 20
BOTTOM_BORDER = Window.height / 4

RED = (255, 0, 0)
GREEN = (0, 255, 0)

COLUMN_COUNT = 3
TIME = 3
QUANT = 1
LIFE = 5
INVITE_TEXT = '''Guess the right country name!
You've got %s attempts.
And time is limited!
You gotta be quick and''' % LIFE

ZONES = {'N. America': (-5, 320, 1),
         'C. America': (-5, 520, 1),
         'S. America': (100, 800, 1),
         'Europe': (730, 270, 3),
         'Greenland': (380, 300, 1),
         'MidEast': (920, 380, 1),
         'Australia': (1500, 970, 1),
         'Russia': (1060, 315, 1),
         'Anime': (1410, 480, 1),
         'N. Africa': (710, 610, 1),
         'C. Africa': (820, 800, 1),
         'S. Africa': (840, 815, 1),
         'FarEast': (1300, 640, 1),
         }


def select_decorator(function):
    selected_countries = list()
    max_random_values = 15

    def decorator(self):
        result = function(self)

        while result in selected_countries:
            result = function(self)
        selected_countries.append(result)

        if len(selected_countries) == max_random_values:
            del selected_countries[0]

        return result

    return decorator


class GMenu(Widget):

    text = StringProperty('Again?')

    def __init__(self, points=0):
        super(GMenu, self).__init__()
        self.size = Window.size
        if points == 0:
            self.text = INVITE_TEXT
            self.b_text = 'Start!'
            return
        elif points < 100:
            self.text = '''You play this game 5 minutes per day
and you will master the game!'''
        elif points < 200:
            self.text = 'Cool!'
        elif points < 300:
            self.text = 'Impressing.'
        elif points < 400:
            self.text = 'Wow. You suprised me.'
        elif points < 500:
            self.text = 'This is really big score.'
        elif points < 600:
            self.text = "I've teached you everything i know."
        elif points < 700:
            self.text = 'Did you really play this game so long?'

        self.text += '\n %s points.' % points
        self.sound = SoundLoader.load('sound/menu.ogg')
        self.sound.volume = 0.2
        self.sound.play()

    def start(self, difficulty):
        self.parent.start(difficulty)
        self.parent.remove_widget(self)

    def exit(self):
        try:
            self.parent.parent.display_menu()
            self.parent.sound.stop()
            self.parent.parent.remove_widget(self)
        except AttributeError:
            pass


class TopBorder(BoxLayout):

    def __init__(self):
        super(TopBorder, self).__init__()
        self.pos = 0, Window.height - Window.height // 17
        self.size = Window.width, Window.height // 17
        self.orientation = 'horizontal'
        self.padding, self.spacing = 2, 0
        self.index = 0
        self.life_list = []
        self.prepare()

    def prepare(self):
        for life in range(LIFE):
            image = Image(
                source=('img/life_%s.png' % (random.randint(1, 2))),
                mipmap=True,
                allow_stretch = True,
                size_hint=(.1, 1),
            )
            self.life_list.append(image)
            self.add_widget(image)
        self.display_points()

    def display_lifes(self, timing=None):
        if self.index == LIFE:
            Clock.schedule_once(self.display_points, 0.2)
            return False

        self.add_widget(self.life_list[self.index])
        self.index += 1

    def remove_life(self):
        self.remove_widget(self.life_list[-1])
        del self.life_list[-1]

    def set_points(self, points):
        self.points.text = str(points)

    def display_points(self, timing=None):
        print(- FONT_SIZE, self.right - FONT_SIZE)
        self.points = Label(text='0',
                            font_name=FONT,
                            font_size=FONT_SIZE + 10,
                            )
        self.add_widget(Label(text=''))
        self.add_widget(self.points)


class Map(Image):

    source = StringProperty(MAP)

    def __init__(self):
        print('Loading image in class')
        super(Map, self).__init__()
        self.init_size = [2250, 1117]
        self.allow_stretch = True
        self.size = self.init_size
        self.init_pos = [- self.width / 2, BOTTOM_BORDER]
        self.pos = self.init_pos
        self.nocache = True
        print('Finished loading image in class')

    def ask_question(self, country, color, zone):
        x, y, scale = ZONES[zone]
        x = -x
        y = self.init_pos[1] - ((self.init_size[1] - y) - BOTTOM_BORDER)
        anim = Animation(x=x, y=y, d=0.5)
        anim.start(self)
        self.fill_country_with_color(country, RED)

    def s(self, *args):
        print(self.pos)

    def reset_source(self, *args):
        self.source = MAP

    @select_decorator
    def select_country(self):
        return random.choice(self.parent.countries.keys())

    def fill_country_with_color(self, country, color):
        raw_map = Img.open(MAP)
        raw_data = raw_map.load()
        country_color = self.parent.countries[country][0]
        for c in self.parent.colors_dict[country_color]:
            for x in range(c[1], c[2] + 1):
                raw_data[x, c[0]] = color
        raw_map.save(COUNTRY)
        self.reload()
        self.source = COUNTRY
        self.allow_stretch = True


class GControls(GridLayout):

    def __init__(self):
        super(GControls, self).__init__()
        self.pos = 0, 0
        self.size = Window.width, BOTTOM_BORDER
        self.cols = 2
        self.rows = 3
        self.padding = 10
        self.spacing = 2
        self.country = None
        self.zone = None

    def get_answers(self, count=5):
        countries = set()
        selection = [
            c for c, zone in self.parent.countries.items() if zone[1] == self.zone and c != self.country]
        if len(selection) < count:
            map(countries.add, selection)
            selection = [c for c, zone in self.parent.countries.items() if zone[
                         1] == 'Europe' and c != self.country]

        while len(countries) < count:
            countries.add(random.choice(selection))

        countries = list(countries) + [self.country]
        random.shuffle(countries)
        return countries

    def check_answer(self, pressed_button):
        self.unbind()
        try:
            guess = pressed_button.text
        except AttributeError:
            guess = None

        if guess and guess == self.country:
            self.parent.correct_answer()
            pressed_button.background_down = 'img/buttons/button_07.png'
            pressed_button.background_normal = 'img/buttons/button_07.png'
            return
        elif guess and guess != self.country:
            pressed_button.background_down = 'img/buttons/button_06.png'
            pressed_button.background_normal = 'img/buttons/button_06.png'
            button_number = '07'
        else:
            button_number = '06'

        self.parent.wrong_answer()
        for child in self.children:
            if child.text == self.country:
                child.background_down = 'img/buttons/button_%s.png' % button_number
                child.background_normal = 'img/buttons/button_%s.png' % button_number

    def display_buttons(self, country, zone):
        self.clear_widgets()
        self.country = country
        self.zone = zone
        answers = self.get_answers()

        for name in answers:
            button = Button(text=name,
                            background_normal='img/buttons/button_05.png',
                            background_down='img/buttons/button_04.png',
                            border=(0, 0, 0, 0),
                            halign='center',
                            valign='middle',
                            font_name=FONT,
                            font_size=FONT_SIZE,
                            )
            button.on_release = lambda b=button: self.check_answer(b)
            self.add_widget(button)

    def unbind(self):
        for child in self.children:
            child.on_release = lambda *args: None


class GeographyMainWindow(Widget):

    def __init__(self, colors_dict=None, sound=None):
        super(GeographyMainWindow, self).__init__()
        self.size = Window.size

        if not self.__is_correct_import():
            self.__add_excuse_menu()
            return

        Window.clearcolor = [x / 255.0 for x in (132, 180, 228)] + [1]
        self.points = 0
        self.life = LIFE
        self.time = 30 * TIME

        self.correct_sound = SoundLoader.load('sound/correct.ogg')
        self.wrong_sound = SoundLoader.load('sound/wrong.ogg')

        if colors_dict:
            print('GOT COLORS DICT!')
            self.colors_dict = colors_dict
        else:
            with open('colors_dict.pkl', 'rb') as c:
                self.colors_dict = pickle.load(c)

        self.countries = dict()
        with open('countries', 'r') as c:
            for line in c.readlines():
                key, val, zone = line.split(': ')
                v = [int(d) for d in val[1:-1].split(', ')]
                self.countries[key] = (tuple(v), zone[:-1])

        if sound:
            self.sound = sound
        else:
            self.sound = SoundLoader.load('sound/geo.ogg')

        self.sound.loop = True
        self.sound.volume = 0.5
        self.sound.play()
        self.map = Map()
        self.add_widget(self.map)
        self.add_widget(GMenu())

    def __is_correct_import(self):
        if Img is None:
            return False
        else:
            return True

    def __add_excuse_menu(self):
        def exit(*args):
            try:
                self.parent.display_menu()
                self.parent.remove_widget(self)
            except AttributeError:
                pass

        label = Label(
            text='Oh no!\nYou should have "Image" library installed.\nI thought it goes with kivy...',
            center=Window.center,
            halign='center',
            valign='middle',
            font_name=FONT,
            font_size=FONT_SIZE,
            markup=True)

        button = Button(
            text='Menu',
            size=(self.width / 1.5, self.height / 7),
            center=(Window.width / 2.0 - 150, Window.height - 200),
            font_name=FONT,
            font_size=FONT_SIZE,
            background_normal='img/buttons/button_01.png',
            background_down='img/buttons/button_02.png',
            border=(0, 0, 0, 0),
            on_press=exit)
        self.add_widget(label)
        self.add_widget(button)

    def start(self, difficulty):
        if difficulty == 1:
            self.play_zones = ['N. America',
                               'C. America',
                               'S. America',
                               'Europe',
                               'Greenland',
                               'Australia',
                               'Russia',
                               'Anime',
                               ]
        else:
            self.play_zones = [x for x in ZONES.keys()]

        self.points = 0
        self.life = LIFE
        self.controls = GControls()
        self.bar = ProgressBar(max=self.time, value=self.time)
        self.bar.pos = 20, BOTTOM_BORDER
        self.bar.size = Window.width - 40, (Window.height / 12.0)
        self.top_border = TopBorder()

        self.add_widget(self.controls)
        self.add_widget(self.bar)
        self.add_widget(self.top_border)
        self.select_country()

    @select_decorator
    def random_country(self):
        country = random.choice(self.countries.keys())
        while self.countries[country][1] not in self.play_zones:
            country = random.choice(self.countries.keys())
            print(country, self.countries[country][1])
        return country

    def start_countdown(self):
        self.bar.value = self.time
        Clock.schedule_interval(self.decrease_time, 1.0 / 30.0)

    def decrease_time(self, timing=None):
        self.bar.value -= QUANT
        if self.bar.value <= 0:
            self.controls.check_answer(None)
            # self.wrong_answer()
            self.controls.unbind()
            return False

    def select_country(self, *args):
        self.start_countdown()
        country = self.random_country()
        color, zone = self.countries[country]
        self.controls.display_buttons(country, zone)
        self.map.ask_question(country, color, zone)

    def correct_answer(self):
        Clock.unschedule(self.decrease_time)
        self.points += 10
        self.top_border.set_points(self.points)
        self.correct_sound.play()
        Clock.schedule_once(self.select_country, 1)

    def wrong_answer(self):
        Clock.unschedule(self.decrease_time)
        self.life -= 1
        self.top_border.remove_life()
        self.wrong_sound.play()

        if self.life == 0:
            Clock.schedule_once(self.game_over, 0.7)
            return

        Clock.schedule_once(self.select_country, 1)

    def game_over(self, timing):
        self.remove_widget(self.controls)
        self.remove_widget(self.bar)
        self.remove_widget(self.top_border)
        self.add_widget(GMenu(self.points))


class GeographyApp(App):

    def build(self):
        map_widget = GeographyMainWindow()
        return map_widget


def test():
    a = Map()
    for _ in range(1000):
        s = set([a.select_country() for x in range(6)])
        if len(s) != 6:
            print('not ok')
        print(s)


if __name__ == '__main__':
    GeographyApp().run()
