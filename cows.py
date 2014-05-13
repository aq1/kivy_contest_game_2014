#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import random
import re

from kivy.app import App
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock

from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.image import Image

from kivy.animation import Animation
# from kivy.vector import Vector
from kivy.properties import NumericProperty, StringProperty, ObjectProperty

import expression_generator as generator

try:
    import android
    android.vibrate(0.05)
except ImportError:
    android = None
    Window.size = [600, 800]

EASY = 1
MEDIUM = 2
HARD = 3
LIFE = 5

COW_WIDTH = Window.width // 10
COW_HEIGHT = COW_WIDTH * 0.7
COW_SPEED = 0.001 * Window.width

UFO_WIDTH = COW_WIDTH * 1.5
UFO_HEIGHT = COW_HEIGHT
UFO_SPEED = COW_SPEED * 4

BALLOON_WIDTH = COW_WIDTH * 1.1
BALLOON_HEIGHT = COW_HEIGHT * 3
FLYING_TIME = 5

VELOCITY_UPDATE_TIME = 0.05
FPS = 1.0 / 40.0
GRAVITY = 10
MAX_COWS = 4
BOTTOM_BORDER = Window.height // 4.5
TOP_BORDER = Window.height - 5 * UFO_HEIGHT
TIMESLICE = 0.3
LABEL_WIDTH = 5
INVITE_TEXT = '''Oh no! UFO steal our COWS!
Please help them \nby solving arithmetic examples!\n'''

if not android:
    INVITE_TEXT += '''On PC: Use keyboard digits to write,
backspace to remove one symbol,
and spacebar to clear'''


class CowStartMenu(Widget):

    '''Menu with rules and difficulty'''

    text = StringProperty()

    def __init__(self, points=0):
        super(CowStartMenu, self).__init__()
        self.size = Window.size

        if points == 0:
            self.text = INVITE_TEXT
            return
        elif points >= 600:
            self.text = 'Cows really love you.'
        elif points >= 500:
            self.text = 'Did you really play this game so long?'
        elif points >= 400:
            self.text = 'Impressing.'
        elif points >= 300:
            self.text = 'Great!'
        elif points >= 200:
            self.text = 'Good!'
        elif points >= 100:
            self.text = 'Nice!'
        elif points < 100:
            self.text = "It's okay."

        self.sound = SoundLoader.load('sound/menu.ogg')
        self.sound.volume = 0.2
        self.sound.play()

        self.text += ' %s points.\nAgain?' % points

    def select_difficulty(self, difficulty):
        self.parent.start(difficulty)
        self.parent.remove_widget(self)

    def exit(self):
        try:
            self.parent.parent.display_menu()
            self.parent.sound.stop()
            self.parent.parent.remove_widget(self)
        except AttributeError:
            pass


class Balloon(Widget):

    '''Such docstring'''

    vel_y = NumericProperty(0)
    source = StringProperty('')
    expression = StringProperty()

    def __init__(self):
        super(Balloon, self).__init__()

    def inflate(self):
        self.size = BALLOON_WIDTH, BALLOON_HEIGHT
        self.center[0] = self.parent.center[0]
        self.y = self.parent.top + COW_WIDTH // 2

        # Is there a better way? parent.parent huh?
        exp = generator.get_expression(
            True, EASY)
        # I'm ok with this:
        exp, self.answer = exp.split('=')
        while int(self.answer) < 0:
            exp = generator.get_expression(
                True, EASY)
            exp, self.answer = exp.split('=')

        l, r = re.search(r'[+-/*]', exp).span()
        # print expression[:operator[0]]

        exp = [exp[:l]] + [exp[l].replace('/', '%')] + [exp[r:]]
        # print exp
        # print expr
        # print [symbol for symbol in exp]
        self.expression = '\n'.join(exp)
        # print

        y = self.y + Window.height - BOTTOM_BORDER
        anim = Animation(x=self.x, y=y, d=FLYING_TIME, t='in_quad')
        anim.start(self)

    def move(self):
        self.pos = [self.x, self.y + abs(self.vel_y)]

    def set_velocity(self, value):
        self.vel_y = value


class Cow(Image):

    alpha = NumericProperty(0)
    source = StringProperty('')

    def __init__(self, x, index, on_horizon=False):
        super(Cow, self).__init__()

        self.size = [COW_WIDTH, COW_HEIGHT]
        self.direction = random.choice((-1, 1))
        self.file = 'img/cows/cow_0{0}/'.format(random.randint(1, 2))
        self.balloon = None
        self.index = index
        self.expression = None
        # self.answer = None
        self.is_flying = False

        if on_horizon:
            y = BOTTOM_BORDER
            self.source = self.file + '{0}.png'.format(self.direction)
            self.pos = [x, y]
            self.__move()
        else:
            y = random.randint(
                int(2 * BOTTOM_BORDER), int(Window.height - COW_HEIGHT))
            # print int(2 * BOTTOM_BORDER), Window.height - COW_HEIGHT, 'sdsd'
            self.pos = [x, y]
            self.fall()

        # I guess there is another word for stealing cows.
        # Maybe it's 'stealing?'
        # Anyway i put it this way ^_^
        # self.horizon = horizon

        Clock.schedule_interval(
            self.__reduce_transparency, VELOCITY_UPDATE_TIME)

    def __reduce_transparency(self, timing=None):
        # print 'alpha', self.alpha
        if self.alpha >= 1:
            return False
        self.alpha += 0.05

    def fall(self, *args):
        try:
            self.fly_anim.cancel(self)
            # self.remove_widget(self.balloon)
        except AttributeError:
            pass

        self.source = self.file + 'fall_{0}.png'.format(self.direction)

        duration = 0.6 if self.center[1] <= Window.height / 2 else 1.3
        anim = Animation(x=self.x, y=BOTTOM_BORDER, d=duration)
        anim.bind(on_complete=lambda *args: self.__move())
        anim.start(self)

    def __fly(self, *args):
        # self.is_flying = True

        self.source = self.file + '{0}.png'.format(self.direction)
        self.fly_anim = Animation(
            x=self.x, y=Window.height, d=FLYING_TIME, t='in_quad')
        # self.fly_anim.bind(on_complete=lambda *args: self.fall())
        self.fly_anim.bind(on_progress=self.__check_if_flew_away)
        self.fly_anim.start(self)

    def __move(self, *args):
        self.is_flying = False
        if random.random() <= 0.8:
            self.direction = random.choice((-1, 1))
            self.source = self.file + '{0}.zip'.format(self.direction)
            self.anim_delay = 0.1

            dx = self.direction * \
                random.randint(0.3 * COW_WIDTH, 0.9 * COW_WIDTH)
            x = int(self.x + dx)
            self.move_anim = Animation(x=x, y=BOTTOM_BORDER)
            self.move_anim.bind(on_complete=self.__move)
            self.move_anim.start(self)
        else:
            self.stop()

    def __check_if_flew_away(self, *args):
        if self.y >= Window.height:
            try:
                self.fly_anim.cancel(self)
                self.parent.lose_the_cow(self)
                # print 'flew away'
            except AttributeError:
                pass
            return

    def check_collision_with(self, another_cow=None):
        if self.is_flying:
            return
        # or another_cow.is_flying:
                # print self.parent
                # print self.index
                # self.parent.lose_the_cow(self)
                # del self
                # self.parent.lose_the_cow(self)

        # if self.x <= another_cow.right and self.right >= another_cow.x:
        #     collision = True, True
        #     self.x -= 3
        # elif self.x >= another_cow.x and self.x <= another_cow.right:
        #     self.x += 3
        #     collision = True, True
        # else:
        #     collision = False, False

        collision = False
        if self.x <= 0:
            self.x = 3
            collision = True
        elif self.right >= Window.width:
            self.x -= 3
            collision = True

        if collision:
            self.stop()

    def stop(self):
        try:
            self.move_anim.cancel(self)
        except AttributeError:
            pass
        self.source = self.file + '{0}.png'.format(self.direction)
        Clock.schedule_once(self.__move, random.uniform(0.5, 1.5))

    def get_kidnapped(self):
        self.is_flying = True
        try:
            self.move_anim.cancel(self)
        except AttributeError:
            pass

        if self.balloon:
            return

        Clock.unschedule(self.__move)
        self.balloon = Balloon()
        self.balloon.center = self.center[0], self.top + COW_WIDTH / 2
        self.add_widget(self.balloon)
        # self.balloons.append(balloon)
        self.balloon.inflate()
        self.__fly()

    def check_answer(self, value):
        if self.balloon and self.balloon.answer == value:
            self.remove_widget(self.balloon)
            self.balloon = None
            self.fall()
            return True

        return False

    def collide_point(self, x, y=None):
        if (not self.is_flying and x >= self.x - COW_WIDTH
                and x <= self.right + 10):
            # print self.x, x
            return True
        else:
            return False

    def game_over(self):
        self.remove_widget(self.balloon)
        self.balloon = None
        self.fall()


class UFO(Image):

    source = StringProperty('')
    # alpha = NumericProperty(1)

    def __init__(self, cows, difficulty, e_sound, s_sound):

        super(UFO, self).__init__()
        self.size = [UFO_WIDTH, UFO_HEIGHT]
        self.pos = [Window.center[0], Window.height]
        # self.engine_sound = SoundLoader.load('sound/ufo_engine.ogg')
        # self.shot_sound = SoundLoader.load('sound/ufo_shot.ogg')
        self.engine_sound = e_sound
        self.shot_sound = s_sound
        self.engine_sound.volume = 0.5
        self.engine_sound.loop = True
        self.source = 'img/cows/ufo_03.png'

        self.cows = cows
  #      self.victim = None
        self.difficulty = difficulty
        self.think_time = 3.5 - difficulty

        self.__all_engines_start()

        # self.__move_to_start_position()
        self.__chose_victim()
        anim = Animation(x=self.x, y=TOP_BORDER, d=0.5)

        _f = Clock.schedule_interval
        anim.bind(on_complete=lambda *args: _f(self.__move, FPS))
        anim.start(self)
        # Clock.schedule_once(self.__chose_victim, 0.6)

    def __closest_cow(self, cow):
        return (self.x - cow.x)

    def __all_engines_start(self):
        if self.difficulty is EASY:
            self.speed = UFO_SPEED
        elif self.difficulty is MEDIUM:
            self.speed = 1.5 * UFO_SPEED
        else:
            self.speed = 3 * UFO_SPEED
        self.engine_sound.play()

        # self.speed = UFO_SPEED

    def __chose_victim(self, timing=None):
        # print 'UFO', self.parent
        free_cows = [cow for cow in self.cows if cow and not cow.is_flying]
        try:
            cow = min(free_cows, key=self.__closest_cow)
        except (IndexError, ValueError):
            cow = None

        if cow:
            # Should be -1 or 1
            self.victim = cow
            self.direction = (cow.center[0] - self.center[0]) / \
                abs(cow.center[0] - self.center[0])
            speed = self.speed
        else:
            self.direction = random.choice((-1, 1))
            Clock.schedule_once(self.__chose_victim, self.think_time)
            speed = self.speed / 3
        self.vel_x = self.direction * speed

    def __move(self, *args):
        offset = Window.width / 120

        if self.x <= -self.width:
            self.x = 3
            self.__chose_victim()
            # self.direction *= -1

        if self.right >= Window.width + self.width:
            self.right = Window.width - 3
            self.__chose_victim()
            # self.direction *= -1

        if (self.center[0] >= self.victim.center[0] - offset and
            self.center[0] <= self.victim.center[0] + offset and not
                self.victim.is_flying):

            self.shoot()

        self.pos = [self.x + self.vel_x, self.y]

    def shoot(self):
        self.shot_sound.play()
        self.victim.get_kidnapped()
        self.vel_x = 0
        # time = random.uniform(
        #     self.think_time - self.difficulty, self.think_time)
        # print time
        # Clock.schedule_once(self.__chose_victim, time)
        self.__chose_victim()

    def game_over(self):
        self.engine_sound.stop()
        Clock.unschedule(self.__move)
        Clock.unschedule(self.__chose_victim)


class Controls(Widget):

    '''Custom keyboard with digits,
       Label with value, remove and clear button'''

    value = StringProperty()
    button_size = NumericProperty(0)

    def __init__(self):
        super(Controls, self).__init__()

        self.size = [Window.width, BOTTOM_BORDER]
        self.pos = [0, 0]
        self.button_size = COW_WIDTH // 1.5

        for i, x in enumerate(range(10, Window.width, Window.width // 10), 1):
            button = Button(text=str(i % 10),
                            pos=[x, self.center[1] - self.button_size],
                            size=[self.button_size, self.button_size],
                            font_name='fonts/Billy.ttf',
                            font_size=self.height / 6,
                            background_normal='img/buttons/button_03.png',
                            background_down='img/buttons/button_04.png')
            button.bind(on_release=self.button_press)
            self.add_widget(button)

    def button_press(self, obj):
        if obj == 'backspace':
            self.remove_symbol()
            return
        elif obj == 'spacebar':
            self.clear()
            return

        if len(self.value) >= LABEL_WIDTH:
            return

        try:
            self.value += obj.text
        except AttributeError:
            self.value += obj
        self.parent.check_answer(self.value)

    def remove_symbol(self):
        self.value = self.value[:-1]

    def clear(self):
        self.value = ''

    def game_over(self):
        self.parent.remove_widget(self)


class CowsMainWidget(Widget):

    '''Docstring kek'''

    difficulty = NumericProperty(0)
    background = ObjectProperty(None)
    points = NumericProperty(0)

    # def on_touch_move(self, touch):
    #     for cow in self.cows:
    #         cow.start_falling()

    def __init__(self, sound=None):
        super(CowsMainWidget, self).__init__()

        self.engine_sound = SoundLoader.load('sound/ufo_engine.ogg')
        self.shot_sound = SoundLoader.load('sound/ufo_shot.ogg')
        self.pop_sound = SoundLoader.load('sound/pop.ogg')

        if sound:
            self.sound = sound
        else:
            self.sound = SoundLoader.load('sound/cows.ogg')

        self.sound.loop = True
        self.sound.play()
        self.size = Window.size
        self.cows = [None for _ in range(4)]
        self.life = LIFE
        Window.clearcolor = (0.2, 0.7, 0.8, 1)

        self.prepare()
        Clock.schedule_interval(self.update, FPS)

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if text.isdigit():
            self.control_object.button_press(text)
            return True

        if keycode[1] in ('backspace', 'spacebar'):
            self.control_object.button_press(keycode[1])
            return True

        return False

    def keyboard_closed(self):
        try:
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)
            self._keyboard = None
        except AttributeError:
            return

    def prepare(self):
        for x in range(MAX_COWS):
            x_coord = 2 * COW_WIDTH * x + \
                random.randint(Window.width / 20, Window.width / 10)
            self.add_cow(x_coord, x, False)

        self.add_widget(CowStartMenu())

    def display_lifes(self, timing=None):
        if self.index == LIFE:
            return False
        self.add_widget(self.life_list[self.index])
        self.index += 1

    def add_cow(self, x, index, on_horizon=False):
        cow = Cow(x, index, on_horizon)
        self.add_widget(cow)
        self.cows[index] = cow
        # self.cows.append(cow)
        # print cow.parent

    def start(self, difficulty):
        if not android:
            self._keyboard = Window.request_keyboard(
                self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.points = 0
        self.life = LIFE
        self.life_list = []
        self.index = 0

        for life in range(LIFE):
            image = Image(
                source=('img/life_%s.png' % random.randint(1, 2)),
                x = 1.1 * life * (self.height // 17),
                y = self.height - self.height // 17,
                size = (self.height // 17, self.height // 17),
                allow_stretch = True)
            self.life_list.append(image)
        Clock.schedule_interval(self.display_lifes, 0.2)

        for child in self.children:
            if isinstance(child, UFO):
                self.remove_widget(child)
        self.difficulty = difficulty
        self.add_widget(UFO(self.cows, self.difficulty, self.engine_sound, self.shot_sound))
        self.control_object = Controls()
        self.add_widget(self.control_object)

    def update(self, timing=None):
        # Screw it. Just checking all of them.
        # But it looks mice when they walk through each other
        # for i, cow in enumerate(self.cows):
        #     for another_cow in self.cows[:i] + self.cows[i + 1:]:
        #         if cow and another_cow:
        #             cow.check_collision_with(another_cow)

        for cow in self.cows:
            if cow:
                cow.check_collision_with()

    def check_answer(self, value):
        # Because c could be None
        for cow in [c for c in self.cows if c]:
            right_answer = cow.check_answer(value)
            if right_answer:
                if self.pop_sound.status == 'stop':
                    self.pop_sound.play()
                self.points += 2 ** self.difficulty
                # print value, self.cows
                self.control_object.clear()
            # if cow.answer == value:
            #     cow.start_falling()
            #     control_object.clear()

    def lose_the_cow(self, cow):
        sound = SoundLoader.load('sound/moo_%s.ogg' % random.randint(0, 2))
        sound.play()
        self.life -= 1

        self.remove_widget(self.life_list[-1])
        del self.life_list[-1]

        self.cows[cow.index] = None
        # self.cows = self.cows[:cow.index-1] + self.cows[cow.index:]
        self.remove_widget(cow)
        x = random.randint(0, Window.width - COW_WIDTH)

        # c_w_e_c = False  # Collides_with_existing_cow

        # while not c_w_e_c:
        #     for cow_ in self.cows:
        #         if cow_ and cow_.collide_point(x):
        #             c_w_e_c = True
        #             x = random.randint(0, Window.width - COW_WIDTH)
        #             break

        #     c_w_e_c = True
        self.add_cow(x, cow.index, True)
        if self.life == 0:
            self.game_over()
            return

    def game_over(self):
        # print 'game_over', self.children
        # This is weird. But something wrong with Controls delete
        self.keyboard_closed()
        for child in reversed(self.children):
            try:
                child.game_over()
            except AttributeError:
                continue
        self.add_widget(CowStartMenu(points=self.points))


class CowsApp(App):

    def build(self):
        main_window = CowsMainWidget()
        return main_window


def test():
    c = Cow(random.randint(0, 100), 1)
    for _ in range(100):
        x = random.randint(170, 200)
        # print COW_WIDTH,
        # if c.collide_point(x):
            # print c.x - COW_WIDTH, x, c.right + 10, c.collide_point(x)


if __name__ == '__main__':
    # test()
    # from kivy.uix.button import Button
    # print help(Button())
    CowsApp().run()
    # print COW_SPEED, BOTTOM_BORDER
    # print help(min)
    # print dir(CowsMainWidget())
    # print help(CowsMainWidget().on_opacity)
    # print help(Animation())
    # print help(Rectangle())
