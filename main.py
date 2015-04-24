#!/usr/bin/python

from __future__ import print_function

"""A Note and Effect randomizer for OpenMPT"""

import random
import copy

import interface
import userinput as ui
import tracker


INSTRUMENT_MAP = list("0123456789:;<=>?@ABCDEFGHI")
#print("%s%s" % (INSTRUMENT_MAP[x / 10], x % 10))
FULL_TITLES = {"C": "Channels", "I": "Instruments", "O": "Octaves",
                "V": "Volumes", "E": "Effects", "F": "Offsets"}


def print_db(database):
    for key in database:
        print("Looking at %s:" % key)
        if type(database[key]) != list:
            print("  %s" % database[key])
        else:
            for thing in database[key]:
                print("  %s" % thing)

def testing():
    database["Octaves"].append(interface.make_octave())
    database["Volumes"].append(interface.make_volume())
    database["Offsets"].append(interface.make_offset())
    database["Instruments"].append(interface.make_instrument(database))
    database["Effects"].append(interface.make_effect())
    database["Channels"].append(interface.make_channel(database))
    print_db(database)


def choose_structure():
    """Prompts the user for a Structure type to act on"""
    prompt = ("Choose a Structure Type:\n"
                    "(C)hannel\t(I)nstrument\n"
                    "(O)ctave\t(V)olume\n"
                    "(E)ffect\t(F) Offset\n"
                    "(B)ack")
    valid = list("CIOVEFB")
    return ui.get_choice(prompt, valid)


def add_to_db(database, thing, title, useGlobals):
    """Let the user add a structure to a database"""

    funcs = {"O": interface.make_octave, "V": interface.make_volume,
            "E": interface.make_effect, "F": interface.make_offset}

    print("\nMaking a %s." % title[:-1])
    if thing == "C":
        new = interface.make_channel(database)
    elif thing == "I":
        new = interface.make_instrument(database)
    else:
        new = funcs[thing]()
    if useGlobals:
        database["Globals"][title].append(new)
    else:
        database[title].append(new)


def delete_from_db(database, thing, title, useGlobals):
    pass


def view_db(database, thing, title, useGlobals):
    """Let the user page through part of the database"""

    if useGlobals:
        db = database["Globals"]
        globalNote = "Global "
    else:
        db = database
        globalNote = ""
    pages = interface.paginate(db[title])
    if pages[0] == []:
        msg = "There are no %s%s to view. Press any key to continue."
        ui.get_input(msg % (globalNote, title))
        return None

    c = ""
    curPage = 1
    header = "\nViewing Page %s of " + globalNote + title

    while c != "B":
        print(header % curPage)
        for item in pages[curPage - 1]:
            print(item)

        prompt = ""
        valid = ["B"]
        if curPage > 1:
            prompt += "Go to (P)revious Page\t"
            valid.append("P")
        prompt += "Go (B)ack" 
        if curPage < len(pages):
            prompt += "\tGo to (N)ext Page"
            valid.append("N")
        c = ui.get_choice(prompt, valid)

    print_db(database)


def edit_db(database, thing, title, useGlobals):
    """Let the user edit a thing in the database"""

    funcs = {"O": interface.edit_octave, "V": interface.edit_volume,
            "E": interface.edit_effect, "F": interface.edit_offset}

    print("\nEditing a %s." % title[:-1])
    prompt = "Choose a %s to edit." % title[:-1]
    db = database["Globals"] if useGlobals else database
    structure = ui.make_mult_choice(prompt, db[title], single=True)
    if thing == "C":
        interface.edit_channel(database, structure)
    elif thing == "I":
        interface.edit_instrument(database, structure)
    else:
        funcs[thing](structure)


def arrange_db(database):
    """Must be given the root database"""
    prompt = "Do you want to move (T)o or (F)rom the Globals database?"
    valid = list("TF")
    while True:
        c = choose_structure()
        if c == "B":
            return None
        where = get_choice(prompt, valid)


def handle_things(c, database, useGlobals):
    """Middle function for performing actions on the database"""
    functions = {"A": add_to_db, "D": delete_from_db,
                "V": view_db, "E": edit_db}
    structure = choose_structure()
    if structure == "B":
        return None
    functions[c](database, structure, FULL_TITLES[structure], useGlobals)
    if c != "V" and ui.get_binary_choice("Again? Y/N"):
        handle_things(c, database, useGlobals)


def main():
    """Run the main menu of the program"""

    prompt = ("Choose an option:\n"
            "(R)un Program\t(T)oggle Channels\n"
            "(A)dd Things\t(D)elete Things\n"
            "(V)iew Things\t(E)dit Things\n"
            "(M)ove Things\t(G)lobals Switch\n"
            "(B)ase Switch\n"
            "(P)arse Args\n"
            "(S)ave File\t(L)oad File\n"
            "(Q)uit")
    valid = list("RTADVEMGBPSLQ")

    database = {"Channels": [], "Instruments": [], "Octaves": [],
                "Effects": [], "Volumes": [], "Offsets": []}
    database["Globals"] = copy.deepcopy(database)
    useGlobals = False

    c = ""
    while c != "Q":
        c = ui.get_choice(prompt, valid)

        if c == "Q":
            continue
        elif c == "R":
            f = ui.get_file("w")
            tracker.produce(f)
        elif c in "ADVE":
            handle_things(c, database, useGlobals)
        elif c == "M":
            arrange_db(database)
        elif c == "G":
            useGlobals = not useGlobals
            if useGlobals:
                print("Now using Globals.")
            else:
                print("No longer using Globals.")
        else:
            print("You chose %s, which hasn't been implemented yet :(" % c)

main()