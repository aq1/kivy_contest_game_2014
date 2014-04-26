#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random

from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock

from kivy.uix.widget import Widget

from kivy.vector import Vector
from kivy.properties import NumericProperty, StringProperty

try:
    import android
except ImportError:
    Window.size = [500, 600]

EASY = 1
MEDIUM = 2
HARD = 3

COW_WIDTH = Window.width / 10
COW_HEIGHT = COW_WIDTH * 0.7
COW_SPEED = 0.001 * Window.width

UFO_WIDTH = COW_WIDTH * 1.5
UFO_HEIGHT = COW_HEIGHT
UFO_SPEED = COW_SPEED * 3

VELOCITY_UPDATE_TIME = 0.05
FPS = 1.0 / 40.0
GRAVITY = 10
MAX_COWS = 4
BOTTOM_BORDER = Window.height / 4.5
TOP_BORDER = 7 * Window.height / 8
TIMESLICE = 0.3


class StartMenu(Widget):

    '''Menu with rules and difficulty'''

    rules_text = StringProperty(
        'OMG UFO STEAL OUR COWS\n\n')

    def __init__(self):
        super(StartMenu, self).__init__()
        self.size = Window.size

    def select_difficulty(self, difficulty):
        self.parent.start(difficulty)
        self.parent.remove_widget(self)


class Cow(Widget):

    '''Walks across the field. Can be stolen by UFO'''

    alpha = NumericProperty(0)
    vel_x = NumericProperty(0)
    vel_y = NumericProperty(0)
    source = StringProperty('')
    r = NumericProperty()

    def __init__(self, x):
        super(Cow, self).__init__()

        y = random.randint(int(2 * BOTTOM_BORDER), Window.height - COW_HEIGHT)
        self.size = [COW_WIDTH, COW_HEIGHT]
        self.pos = [x, y]
        self.r = random.random()
        # I guess there is another word for stealing cows.
        # Maybe it's 'stealing?'
        # Anyway i put it this way ^_^
        self.is_flying = False
        self.direction = random.choice((-1, 1))

        # self.source = '/img/cartoon-cow-22.jpg'

        Clock.schedule_interval(
            self.__reduce_transparency, VELOCITY_UPDATE_TIME)

        self.fall()

    def __reduce_transparency(self, timing=None):
        if self.alpha >= 1:
            return False
        self.alpha += 0.05

    def decide_where_to_go(self, timing=None):
        if self.is_flying:
            return False

        decision = random.choice((
            self.change_direction, self.stop, self.stop, self.speed_up))
        decision()
        time = random.uniform(0, TIMESLICE)
        Clock.schedule_once(self.decide_where_to_go, time)

    def change_direction(self, timing=None):
        self.direction *= -1

    def speed_up(self):
        self.vel_x = COW_SPEED * self.direction

    def stop(self):
        self.vel_x = 0
        self.vel_y = 0
        self.y = BOTTOM_BORDER

    def fall(self, timing=None):
        # print self.y, BOTTOM_BORDER, self.y <= BOTTOM_BORDER
        if self.y <= BOTTOM_BORDER:
            # print 'NOOO'
            self.stop()
            self.is_flying = False
            Clock.schedule_once(self.decide_where_to_go, TIMESLICE)
            return False
        elif -GRAVITY < self.vel_y < GRAVITY:
            # print 'TES'
            self.vel_y -= 0.5

        Clock.schedule_once(self.fall, VELOCITY_UPDATE_TIME)

    def blast_off(self, timing=None):
        if self.y > Window.height:
            self.parent.lose_the_cow(self)
            return False
        elif -GRAVITY < self.vel_y < GRAVITY:
            self.vel_y += 0.2

        Clock.schedule_once(self.blast_off, 10 * VELOCITY_UPDATE_TIME)

    def move(self):
        # print self.vel_y
        if self.x <= 10:
            self.stop()
            self.x = 11
        if self.right >= Window.width - 10:
            self.stop()
            self.x = Window.width - 11

        self.pos = Vector(self.vel_x, self.vel_y) + self.pos

    def kidnap(self):
        # print self.parent
        self.is_flying = True
        self.vel_x = 0
        self.blast_off()

    # def get_stolen_by_UFO(self):
    #     self.parent.lose_the_cow()
        # self.parent.remove_widget(self)

    # def add_balloon(self):
    #     self.kidnap()
    #     print 'balloon added'
    #     pass

    def check_collision_with(self, another_cow):
        if self.x < another_cow.right and self.right >= another_cow.x:
            collision = True
            self.x -= 3
        elif self.x > another_cow.x and self.x <= another_cow.right:
            self.x += 3
            collision = True
        else:
            collision = False

        if collision:
            self.stop()
            # another_cow.change_direction()


class UFO(Widget):

    '''Flying, stealing cows'''
    source = StringProperty('')
    alpha = NumericProperty(1)

    def __init__(self, cows, difficulty):

        super(UFO, self).__init__()
        self.size = [UFO_WIDTH, UFO_HEIGHT]
        self.pos = [Window.center[0], Window.height]

        self.cows = cows
        self.victim = None
        self.difficulty = difficulty
        self.think_time = 3.5 - difficulty

        self.all_engines_start()

        self.__move_to_start_position()

        Clock.schedule_once(self.chose_victim, 0.5)

    def all_engines_start(self):
        if self.difficulty is EASY:
            self.speed = UFO_SPEED
        elif self.difficulty is MEDIUM:
            self.speed = 1.5 * UFO_SPEED
        else:
            self.speed = 2 * UFO_SPEED

    def __move_to_start_position(self, timing=None):
        if self.y <= TOP_BORDER:
            return False

        self.pos = [self.x, self.y - 2 * self.speed]
        Clock.schedule_once(self.__move_to_start_position, FPS)

    def shoot(self):
        self.victim.kidnap()
        self.vel_x = 0
        time = random.uniform(self.think_time - self.difficulty, self.think_time)
        print time
        Clock.schedule_once(self.chose_victim, time)

    def move(self):
        if (self.center[0] >= self.victim.center[0] - 2 and
            self.center[0] <= self.victim.center[0] + 2 and not
                self.victim.is_flying):

            self.shoot()

        self.pos = [self.x + self.vel_x, self.y]

    def chose_victim(self, timing=None):
        free_cows = [cow for cow in self.cows if not cow.is_flying]
        try:
            cow = random.choice(free_cows)
        except IndexError:
            self.vel_x = 0
            cow = None

        if cow:
            # Should be -1 or 1
            self.victim = cow
            direction = (cow.center[0] - self.center[0]) / \
                abs(cow.center[0] - self.center[0])
            self.vel_x = direction * self.speed


class MainWindow(Widget):

    '''Docstring kek'''

    difficulty = NumericProperty(0)

    def __init__(self):
        super(MainWindow, self).__init__()
        self.size = Window.size
        self.cows = list()

        self.prepare()

    def prepare(self):
        for x in range(MAX_COWS):
            x_coord = 2 * COW_WIDTH * x + \
                random.randint(Window.width / 20, Window.width / 10)
            self.add_cow(x_coord)

        self.add_widget(StartMenu())

    def add_cow(self, x):
        cow = Cow(x)
        self.add_widget(cow)
        self.cows.append(cow)

    def update(self, timing=None):
        # Screw it. Just checking all of them.

        for i, cow in enumerate(self.cows):
            for another_cow in self.cows[:i] + self.cows[i + 1:]:
                cow.check_collision_with(another_cow)

        for child in self.children:
            try:
                child.move()
            except AttributeError:
                pass

    def start(self, difficulty):
        self.difficulty = difficulty
        self.add_widget(UFO(self.cows, self.difficulty))

    def lose_the_cow(self, cow):
        self.remove_widget(cow)
        pass


class CowApp(App):

    def build(self):
        main_window = MainWindow()
        Clock.schedule_interval(main_window.update, FPS)
        return main_window


if __name__ == '__main__':
    CowApp().run()
    print COW_SPEED
