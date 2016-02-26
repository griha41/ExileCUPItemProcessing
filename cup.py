#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from re import compile
from random import random, randint
from collections import OrderedDict

# import logging
# logging.basicConfig(level=logging.DEBUG, format='%(message)s')
# dbg = logging.debug
# logging.disable(level=logging.CRITICAL)

__re_match_item = compile('class\s+(CUP_[A-Za-z0-9_]*)\s*\{.quality.=.([0-9]);.price.=.([0-9]{1,4})').match  # groups: classname, quality, price
__re_match_header = compile('\[([A-Za-z0-9\ \-_]{1,32})\]').match  # groups: header name
__re_match_invalid = compile('(?:\s*[/#]+|\*[#/]|^\s*$)').match  # groups: none


def roundprice(n):
    '''
    :param int n: Price
    :return int: Rounded-off price
    '''
    if 300 <= n:
        return round((n / 50)) * 50
    else:
        return round(n / 10) * 10


def line_to_dict_entry(line, dictionary, header=None):
    '''
    Takes a line of text from the source file and parses it.
    :str line: A line from the source file
    :dict dictionary: A dictionary to stuff things in
    :str header: The header for the current line
    :dict return: The modified `dictionary`
    '''
    classname, quality, price = __re_match_item(line).groups()

    if header in ["CUP Optics", "CUP RailAttachments"]:
        adjustment = randint(2, 3) * 10
    elif header in ["CUP Light Ammo", "CUP Heavy Ammo", "CUP Muzzle Attachments"]:
        adjustment = randint(1, 2) * 10
    else:
        adjustment = randint(1, 3) * 10

    price = str(max(roundprice(int(price) + adjustment), 10))

    if header:
        try:
            dictionary[header].append((classname, quality, price))
        except KeyError:  # dict[header] does not exist, first item in group
            dictionary[header] = [(classname, quality, price)]

    else:
        dictionary[classname] = (quality, price)


def file_to_dict(input_file):
    '''
    Takes the input file and parses it to a dict of items.
    :file input_file: Source file
    :dict return: Dictionary of items
    '''
    header = "errors"  # default value for header, anything works
    d = OrderedDict()

    with open(input_file) as file:

        for line in file:
            isheader = __re_match_header(line)
            invalid = __re_match_invalid(line)

            if isheader:
                header = isheader.group(1)
                pass

            elif not invalid:
                line_to_dict_entry(line, d, header)

    return d


def dict_to_configcpp(dictionary: dict, file=None, tabs=3):
    '''
    Takes the item dict and a file, and fills the file with classnames from the dict.
    :dict dictionary: Dictionary of items
    :file file: File to stuff output into
    :int tabs: Number of tabs preceding lines in file
    :return: None
    '''
    new_dict = OrderedDict()
    for header, itemlist in dictionary.items():
        for item in itemlist:
            name, quality, price = item
            new_dict[name] = (quality, price)

        dictionary = new_dict

    if file:
        write = file.write
    else:
        write = lambda x: print(*x, sep='', end='')

    last = len(dictionary)
    i = 0

    for key, value in dictionary.items():
        i += 1
        write('\t' * tabs + "\"" + key + "\"" + ",\n" * (i < last))


def dict_to_pricelist(dictionary: dict, file=None, tabs=1):
    '''
    Takes the item dict and a file, and fills the file with the pricelist from the dict.
    :dict dictionary: Dictionary of items
    :file file: File to stuff output into
    :int tabs: Number of tabs preceding lines in file
    :return: None
    '''
    if file:
        write = file.write
    else:
        write = lambda x: print(*x, sep='', end='')

    for header, itemlist in dictionary.items():  # write the category name above the price list
        write("\n" + '\t' * tabs + r'///////////////////////////////////////////////////////////////////////////////' + "\n")
        write('\t' * tabs + r'//' + header + "\n")
        write('\t' * tabs + r'///////////////////////////////////////////////////////////////////////////////' + "\n\n")
        for item in itemlist:  # then write out all items in the category
            item, quality, price = item
            write('\t' * tabs + 'class {0: <45} {{ quality = {1}; price = {2}; }};\n'.format(item, quality, price))


def dict_to_lootgroups(dictionary: dict, file=None):
    '''
    Takes the item dict and a file, and fills the file with the lootgroup compiler info from the dict.
    :dict dictionary: Dictionary of items
    :file file: File to stuff output into
    :return: None
    '''
    explosive_keywords = ["g7", "maaws", "rpg18", "strela", "stinger", "bomb", "m136", "at13", "smaw",
                          "javelin", "mine", "grenade", "igla", "nlaw", "dragon", "he_gp", "hedp"]
    if file:
        write = file.write
    else:
        write = lambda x: print(*x, sep='', end='')
    for header, itemlist in dictionary.items():
        write("\n> " + header.replace(' ', '') + "\n")
        sumprices = 0
        l = len(itemlist)

        for item in itemlist:
            price = item[2]
            sumprices += float(price)

        for item in itemlist:
            name, quality, price = item
            lower = name.lower()

            def is_explosive(weapon_or_item):
                '''
                True if the weapon or item looks like an explosive, false otherwise.
                :param weapon_or_item: Classname
                :return: True
                '''
                return any(filter(lambda x: x in weapon_or_item.lower(), explosive_keywords))

                # modify the rarity of certain items; higher mod numbers = more rare

            mod = {
                True:                                1,
                "hgun" in lower:                     6,
                "smg" in lower:                      4,
                "gold" in lower:                     3,
                "aa12" in lower:                     2,
                "hgun" in lower and "gold" in lower: 18,
                is_explosive(lower):                 5,
            }[1]

            avgprice = round(sumprices / l)
            random_mult = 3 * (random() + 1)
            price = float(price)

            chance = max(1,
                         round(40 / (price * mod * random_mult / avgprice)))

            write("{chance}, {name}\n".format(chance=chance, name=name))


if __name__ == '__main__':
    OVERWRITE = 'w'
    dict = file_to_dict('source.txt')

    with open('lootgroups.h.txt', OVERWRITE) as lootgroups, \
            open('configcpp.txt', OVERWRITE) as configcpp, \
            open('cupprices.txt', OVERWRITE) as cupprices:

        dict_to_lootgroups(
                dictionary=dict,
                file=lootgroups
        )
        dict_to_configcpp(
                dictionary=dict,
                file=configcpp
        )
        dict_to_pricelist(
                dictionary=dict,
                file=cupprices
        )
