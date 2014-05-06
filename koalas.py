#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.uix.widget import Widget
from kivy.uix.image import Image

from kivy.vector import Vector
from kivy.properties import NumericProperty, StringProperty

import expression_generator as generator

try:
    import android
except ImportError:
    Window.size = [600, 800]

FPS = 1.0 / 60.0
# CHANGE_DIRECTION = 0.3
LEAF_SPEED = Window.height / 250

EASY = 1
MEDIUM = 2
HARD = 3
# COMBO_VALUE = 10
MAX_LIFE = 7

BORDER_HEIGHT = Window.height / 18
LEAF_SIZE = [Window.width / 2.5, Window.height / 8]
PANDA_SIZE = [LEAF_SIZE[0] / 1.5, LEAF_SIZE[1] / 1.5]
PANDA_SPEED = 8
INVITE_TEXT = '''Feed koalas with leafes.
But those are strange koalas.
They only want to eat leaf with Truth written on it.'''


class StartMenu(Widget):

    '''Menu with rules and difficulty'''

    text = StringProperty()

    def __init__(self, points=0):
        super(StartMenu, self).__init__()
        self.size = Window.size

        if points == 0:
            self.text = INVITE_TEXT
            return
        elif points >= 400:
            self.text = 'Did you really play this game so long?'
        elif points >= 300:
            self.text = 'Wow! They are really staffed!'
        elif points >= 200:
            self.text = 'Cool! Time for koalas to sleep.'
        elif points >= 100:
            self.text = 'Good! I think they are not hungry anymore'
        elif points < 100:
            self.text = "It's fine. But will they eat better next time?"
        self.text += '\n%s points.\nAgain?' % points

    def select_difficulty(self, difficulty):
        self.parent.start_game(difficulty)
        self.parent.remove_widget(self)

    def exit(self):
        try:
            self.parent.parent.remove_widget(self)
            self.parent.parent.display_menu()
        except AttributeError:
            pass


class KoalaPaw(Widget):

    '''Takes leaf. Needs leaf coords.
        For aesthetic purposes only'''

    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)

    def __init__(self, parent):

        super(KoalaPaw, self).__init__()
        self.size = PANDA_SIZE
        self.vel_y = parent.vel_y
        if parent.pos[0] < Window.size[0] // 2:
            self.pos = [-self.size[0], parent.pos[1]]
            self.vel_x = PANDA_SPEED
        else:
            self.pos = [Window.width, parent.pos[1]]
            self.vel_x = -PANDA_SPEED

        self.center[1] = parent.center[1]

        self.move()
        # Clock.schedule_once(self.change_direction, CHANGE_DIRECTION)

    def change_direction(self, timing=None):
        self.vel_x *= -1
        self.parent.vel_x = self.vel_x

    def move(self, timing=None):

        if self.x > Window.width or self.right < 0:
            self.parent.destroy(self)
            return

        if (self.x >= 0 and self.right < Window.width
           or self.right <= Window.width and self.x > 0):
            self.change_direction()

        self.pos = Vector(self.vel_x, self.vel_y) + self.pos
        Clock.schedule_once(self.move, FPS)


class Leaf(Widget):

    '''A single leaf with expression'''

    vel_x = NumericProperty(0)
    vel_y = NumericProperty(-LEAF_SPEED)
    expression = StringProperty()
    source = StringProperty('')

    def __init__(self, pos, size, difficulty):
        super(Leaf, self).__init__()

        self.pos = pos
        self.size = size
        self.truth = True
        self.difficulty = difficulty
        self.add_expression()
        self.taken = False

        if pos[0] < Window.width / 2:
            self.source = 'Leaf_1_02.png'
        else:
            self.source = 'Leaf_2_02.png'

        self.source = 'img/koalas/' + self.source

    def add_expression(self):
        '''Expression is taken from generator module.'''
        if random.random() <= 0.5:
            self.truth = True
        else:
            self.truth = False

        if random.random() <= 0.7:
            expression = generator.get_expression(self.truth, self.difficulty)
        else:
            expression = generator.get_bool_expression(self.truth, self.difficulty)

        self.expression = expression

    def move(self):
        '''If true reaches the bottom players loses life.'''
        if self.top < 0:
            if self.truth:
                self.parent.remove_life()
            else:
                self.parent.add_points()
            self.destroy()

        self.pos = Vector(self.vel_x, self.vel_y) + self.pos

    def move_after_game_ends(self):
        if self.top < 0:
            self.destroy()

        self.pos = Vector(self.vel_x, self.vel_y) + self.pos

    def eat_leaf(self):
        '''Remove leaf and if expresison is true add points.'''
        if self.truth:
            # pass

            self.parent.add_points()
            # self.parent.remove_widget(self)
        else:
            self.parent.remove_life()

        self.add_widget(KoalaPaw(self))

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y) and not self.taken:
            self.eat_leaf()
            self.taken = True

    def destroy(self, paw=None):

        try:
            self.remove_widget(paw)
            self.parent.remove_widget(self)
        except AttributeError:
            pass


class KoalasMainWidget(Widget):

    '''I hope you don't need any comments here. It's simple.'''

    border_height = NumericProperty(BORDER_HEIGHT)
    liana_width = NumericProperty(0)
    liana_y = NumericProperty(Window.height)
    alpha = NumericProperty(0)
    points = NumericProperty(0)
    koala_heads_list = []
    index = 0

    def __init__(self):
        super(KoalasMainWidget, self).__init__()

        self.size = Window.size
        self.liana_width = self.width / 15
        self.start_menu = None
        self.points = 0
        self.__startup_animation()
        self.add_widget(StartMenu())

        # self.start_game()

    def start_game(self, difficulty):
        self.points = 0
        self.difficulty = difficulty
        if self.difficulty is EASY:
            self.life = 5
        elif self.difficulty is MEDIUM:
            self.life = 3
        else:
            self.life = 2

        # If it's not the first start:
        # self.liana_y = Window.height
        # self.alpha = 0

        self.create_lifes_list()
        # self.__startup_animation()

        # Clock.schedule_once(self.add_leaf, 2)
        self.add_leaf()
        Clock.schedule_interval(self.update, FPS)

    def __reduce_transparency(self, timing=None):
        if self.alpha >= 1:
            return False

        self.alpha += 0.05

    def __move_liana(self, timing):
        if self.liana_y <= 0:
            return False

        self.liana_y -= 10

    def __startup_animation(self):
        Clock.schedule_interval(self.__reduce_transparency, 0.05)
        Clock.schedule_interval(self.__move_liana, FPS)
        # self.add_leaf()

    def create_lifes_list(self):
        for child in self.koala_heads_list:
            self.remove_widget(child)

        self.koala_heads_list = []
        self.index = 0

        for life in range(self.life):
            image = Image(
                source=('img/koalas/koala_life.png'),
                x = life * BORDER_HEIGHT,
                y = self.height - 0.95 * BORDER_HEIGHT,
                size = (BORDER_HEIGHT - 5, BORDER_HEIGHT - 5),
                allow_stretch = True)
            self.koala_heads_list.append(image)

        Clock.schedule_interval(self.display_lifes, 0.15)

    def display_lifes(self, timing=None):

        if self.index == self.life:
            return False

        self.add_widget(self.koala_heads_list[self.index])
        self.index += 1

    def add_points(self):
        self.points += 10 * self.difficulty

    def remove_life(self):
        self.life -= 1
        if self.life == 0:
            self.game_over()

        self.remove_widget(self.koala_heads_list[-1])
        del self.koala_heads_list[-1]

    def add_leaf(self, timing=None):
        if random.random() < 0.5:
            pos = self.center[0] + self.liana_width / 3
        else:
            pos = self.center[0] - LEAF_SIZE[0]
        self.add_widget(
            Leaf(pos=[pos, self.height],
                 size=LEAF_SIZE,
                 difficulty=self.difficulty))

        Clock.schedule_once(self.add_leaf, 1)

    def update(self, timing):
        for child in self.children:
            try:
                child.move()
            except AttributeError:
                pass

    def end_animation(self, timing=None):
        leaf_moved = False
        for child in self.children:
            try:
                child.move_after_game_ends()
                leaf_moved = True
            except AttributeError:
                pass

        if not leaf_moved:
            self.start_menu = StartMenu(points=self.points)
            self.add_widget(self.start_menu)
            return False

    def game_over(self):
        Clock.unschedule(self.add_leaf)
        Clock.unschedule(self.update)

        for child in self.children:
            try:
                child.vel_y *= 10
            except AttributeError:
                pass

        Clock.schedule_interval(self.end_animation, FPS)

    def exit(self):
        try:
            self.parent.remove_widget(self)
        except AttributeError:
            # print self.app
            pass


class KoalasApp(App):

    def build(self):
        # Window.clearcolor = (1, 1, 1, 1)
        # Window.size = [500, 600]
        main_window = KoalasMainWidget()
        return main_window


if __name__ == '__main__':
    KoalasApp().run()
