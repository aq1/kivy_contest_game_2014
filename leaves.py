#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random
import pickle

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.uix.widget import Widget
from kivy.uix.image import Image

from kivy.vector import Vector
from kivy.properties import NumericProperty, StringProperty

import expression_generator as generator

Window.size = [500, 600]

FPS = 1.0 / 60.0
# CHANGE_DIRECTION = 0.3
LEAF_SPEED = Window.height / 250

EASY = 1
MEDIUM = 2
HARD = 3
COMBO_VALUE = 10
MAX_LIFE = 7

BORDER_HEIGHT = Window.height / 18
LEAF_SIZE = [Window.width / 2.5, Window.height / 8]
PANDA_SIZE = [LEAF_SIZE[0] / 1.5, LEAF_SIZE[1] / 1.5]
PANDA_SPEED = 8


class RestartMenu(Widget):

    label_text = StringProperty('')

    def __init__(self, score=None):
        super(RestartMenu, self).__init__()

        self.size = Window.size
        self.label_text = '''Well... That's ok.'''


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
        self.is_true = True
        self.difficulty = difficulty
        self.add_expression()

        if pos[0] < Window.width / 2:
            self.source = 'Leaf_1_02.png'
        else:
            self.source = 'Leaf_2_02.png'

        self.source = 'img/' + self.source

    def add_expression(self):
        '''Expression is taken from generator module.'''
        if random.random() <= 0.5:
            expression = generator.get_expression(True, self.difficulty)
        else:
            expression = generator.get_expression(False, self.difficulty)
            self.is_true = False

        self.expression = expression

    def move(self):
        '''If true reaches the bottom players loses life.'''
        if self.top < 0:
            if self.is_true:
                self.parent.remove_life()
            else:
                self.parent.increase_combo_points()
            self.destroy()

        self.pos = Vector(self.vel_x, self.vel_y) + self.pos

    def move_after_game_ends(self):
        if self.top < 0:
            self.destroy()

        self.pos = Vector(self.vel_x, self.vel_y) + self.pos

    def eat_leaf(self):
        '''Remove leaf and if expresison is true add points.'''
        if self.is_true:
            # pass

            self.parent.increase_combo_points()
            # self.parent.remove_widget(self)
        else:
            self.parent.remove_life()

        self.add_widget(KoalaPaw(self))

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.eat_leaf()

    def destroy(self, paw=None):

        try:
            self.remove_widget(paw)
            self.parent.remove_widget(self)
        except AttributeError:
            pass


class MainWindow(Widget):

    '''I hope you don't need any comments here. It's simple.'''

    combo_points = NumericProperty(0)
    border_height = NumericProperty(BORDER_HEIGHT)
    liana_width = NumericProperty(0)
    liana_y = NumericProperty(Window.height)
    alpha = NumericProperty(0)
    koala_heads_list = []
    index = 0

    def __init__(self, difficulty):
        super(MainWindow, self).__init__()

        self.size = Window.size
        self.difficulty = difficulty
        self.liana_width = self.width / 15
        self.restart_menu = None

        self.start_game()

    def start_game(self):
        if self.difficulty is EASY:
            self.life = 5
        elif self.difficulty is MEDIUM:
            self.life = 3
        else:
            self.life = 1

        # If it's not the first start:
        self.remove_widget(self.restart_menu)
        self.liana_y = Window.height
        self.alpha = 0

        self.create_lifes_list()
        self.startup_animation()

        Clock.schedule_once(self.add_leaf, 2)
        Clock.schedule_interval(self.update, FPS)

    def reduce_transparency(self, timing=None):
        if self.alpha >= 1:
            return False

        self.alpha += 0.05

    def move_liana(self, timing):
        if self.liana_y <= 0:
            return False

        self.liana_y -= 10

    def startup_animation(self):
        Clock.schedule_interval(self.reduce_transparency, 0.05)
        Clock.schedule_interval(self.move_liana, FPS)
        # self.add_leaf()

    def create_lifes_list(self):
        for child in self.koala_heads_list:
            self.remove_widget(child)

        self.koala_heads_list = []
        self.index = 0

        for life in range(self.life):
            image = Image(
                source=('img/koala_life.png'),
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

    def increase_combo_points(self):

        self.combo_points += 1
        if self.combo_points == COMBO_VALUE:
            self.reset_combo_points()
            self.add_life()

    def reset_combo_points(self):

        self.combo_points = 0

    def add_life(self):
        if self.life >= MAX_LIFE:
            return

        self.life += 1
        self.create_lifes_list()

    def remove_life(self):

        # return
        self.life -= 1
        if self.life == 0:
            self.game_over()

        self.remove_widget(self.koala_heads_list[-1])
        del self.koala_heads_list[-1]
        self.reset_combo_points()

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
            self.restart_menu = RestartMenu()
            self.add_widget(self.restart_menu)
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


class LeavesApp(App):

    def build(self):
        # Window.clearcolor = (1, 1, 1, 1)
        # Window.size = [500, 600]
        main_window = MainWindow(difficulty=HARD)
        return main_window


if __name__ == '__main__':
    LeavesApp().run()
