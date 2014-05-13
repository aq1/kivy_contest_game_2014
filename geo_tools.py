#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import random
import pickle

# from kivy.app import App
# from kivy.uix.widget import Widget
# from kivy.uix.image import Image
# from kivy.clock import Clock

import Image as Img

from collections import defaultdict


# a = Img.open('img/geography/world_map_color.png')
# a = Img.open('img/geography/world_map.png')
# a = Img.open('/home/aq1/Desktop/test.png')
# a = Img.open('img/geography/out.png')
# a = Img.open('img/geography/out1.png')
a = Img.open('img/geography/map_color_1.png')
# a = Img.open('img/geography/539c030a2dcfebbc450bf82339e1a3982.jpg')
colors_dict = defaultdict(list)


error = 30


def is_same_colors(color, another_color):
    for x, y in zip(color, another_color):
        if not x - error < y < x + error:
            return False
    return True


init_colors = ((132, 180, 228), (0, 0, 0), (255, 255, 255))
not_blue_colors = ((140, 140, 140), (121, 121, 121), (182, 182, 182))
black = (71, 71, 71)


def closest_color(color):
    a = []
    if any([is_same_colors(c, color) for c in not_blue_colors]):
        return init_colors[2]
    elif is_same_colors(color, black):
        return init_colors[1]

    for i_color in init_colors:
        a.append([abs(x - y) for x, y in zip(color, i_color)])

    index = min((val, indx) for indx, val in enumerate(a))[1]
    return init_colors[index]

# for x in init_colors:
#     print closest_color(x)

# print closest_color((71, 71, 71))
# print a.getpixel((933, 241))

def recolor():
    for y in range(a.size[1]):
        for x in range(0, a.size[0]):
            pixel = a.getpixel((x, y))

            a.putpixel((x, y), closest_color(pixel))

    try:
        a.save('img/geography/world_map.png')
    except:
        pass
    a.show()


def read():
    # test = (29, 255, 5)
    for y in range(a.size[1]):
        x0 = 0
        color = a.getpixel((1, y))
        for x in range(1, a.size[0]):
            current_color = a.getpixel((x, y))

            if not color == current_color:
            # if not is_same_colors(color, current_color):
                colors_dict[color].append([y, x0, x - 1])
                color = current_color
                x0 = x
        if x0 != x and color not in init_colors:
            colors_dict[color].append([y, x0, x - 1])

    for x in colors_dict.keys():
        if x in init_colors:
            del colors_dict[x]
    
    clean_dictionary(colors_dict)

    with open('colors_dict.pkl', 'wb') as cd:
        pickle.dump(colors_dict, cd)

    with open('colors.txt', 'w') as colors:
        for x, y in colors_dict.items():
            colors.write('%s|| %s\n' % (x, y))

    for x in colors_dict.keys():
        print x

    # print help(a.putpixel)
    # a.show()


def write():
    global colors_dict
    with open('colors_dict.pkl', 'rb') as s:
        colors_dict = pickle.load(s)
    # for x, y in colors_dict.items():
    #     print x


def paint_all():
    d = Img.open('img/geography/world_map.png')
    a = d.load()
    with open('colors_dict.pkl', 'rb') as s:
        colors_dict = pickle.load(s)
        # print colors_dict.keys()

    # for key, coords in colors_dict.items():
    #     for y, x0, x1 in coords:
    #         for x in range(x0, x1 + 1):
    #             a.putpixel((x, y), (0, 255, 0))

    # print len(coords)
    # colors = ((255, 255, 0),
    #           (255, 5, 5),
    #           (255, 190, 13),)

    coords = colors_dict[random.choice(colors_dict.keys())]

    for coords in colors_dict.values():
        for y, x0, x1 in coords:
            for x in range(x0, x1 + 1):
                # a.putpixel((x, y), (255, 0, 0))
                a[x, y] = (0, 255, 0)
    # for y in range(a.size[1]):
    #     for x in range(0, a.size[1]):
    #         pixel = a.getpixel((x, y))
    #         if is_same_colors(colors[0], pixel):
    #             a.putpixel((x, y), (0, 255, 0))

    d.show()
    # a.save('img/geography/working_image.png')


def write_countries_dict():
    a = dict()
    b = dict()
    with open('countries', 'r') as c:
        for line in c.readlines():
            key, val, zone = line.split(': ')
            # print val[1:-1]
            v = [int(d) for d in val[1:-1].split(', ')]
            # a[tuple(v)] = key
            b[key] = (tuple(v), zone)

    # print a.keys()
    return b


def fill_country(country):
    color = countries[country][0]
    d = Img.open('img/geography/world_map.png')
    a = d.load()
    print color
    # print colors_dict[color]
    for c in colors_dict[color]:
        for x in range(c[1], c[2] + 1):
            # print x
            # a.putpixel((x, y), (255, 0, 0))
            a[x, c[0]] = (0, 255, 0)
    d.show()

def clean_dictionary(dict_):
    countrs = [x[0] for x in write_countries_dict().values()]
    # print countrs
    for key in dict_.keys():
        if key not in countrs:
            del dict_[key]
            print key
    print len(dict_.keys())

# print dir(Map())
# recolor()
# a.show()
countries = write_countries_dict()
# print countries
# read()
write()
paint_all()
# fill_country('India')
