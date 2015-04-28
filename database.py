#!/usr/bin/env python

from __future__ import print_function

"""Functions for directly handling the database"""

import pickle

import interface
import structures
import userinput as ui

def print_db(database):
    for key in database:
        print("Looking at %s:" % key)
        if type(database[key]) != list:
            print("  %s" % database[key])
        else:
            for thing in database[key]:
                print("  %r" % thing)


def choose_structure():
    """Prompts the user for a Structure type to act on"""
    prompt = ("Choose a Structure Type:\n"
                    "(C)hannel\t(I)nstrument\n"
                    "(O)ctave\t(V)olume\n"
                    "(E)ffect\t(F) Offset\n"
                    "(B)ack")
    valid = list("CIOVEFB")
    return ui.get_choice(prompt, valid)


def add_to_db(database, choice, title, useGlobals):
    """Let the user add a structure to a database"""

    funcs = {"O": interface.make_octave, "V": interface.make_volume,
            "E": interface.make_effect, "F": interface.make_offset}

    print("\nMaking a %s." % title[:-1])
    if choice == "C":
        new = interface.make_channel(database)
    elif choice == "I":
        new = interface.make_instrument(database)
    else:
        new = funcs[choice]()
    if useGlobals:
        database["Globals"][title].append(new)
    else:
        database[title].append(new)


def delete_from_db(database, choice, title, useGlobals):
    """Let the user delete structures from the Database."""

    if useGlobals:
        db = database["Globals"]
        globalNote = "Global "
    else:
        db = database
        globalNote = ""

    prompt = "Choose %s%s to delete. Press C to continue." % (
        globalNote, title)
    deleteThese = ui.make_mult_choice(prompt, db[title], "C")

    for structure in deleteThese:
        interface.remove_all_links(structure)
        db[title].remove(structure)
    print("\nDeleted %s %s%s." % (len(deleteThese), globalNote, title))


def view_db(database, choice, title, useGlobals):
    """Let the user page through part of the database"""

    if useGlobals:
        db = database["Globals"]
        globalNote = "Global "
    else:
        db = database
        globalNote = ""

    pages = interface.paginate(db[title])
    if pages[0] == []:
        prompt = "There are no %s%s to view. Press any key to continue."
        ui.get_input(prompt % (globalNote, title))
        return None

    choice = ""
    curPage = 1
    header = "\nViewing Page %s of " + globalNote + title

    while choice != "B":
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
        choice = ui.get_choice(prompt, valid)


def edit_db(database, choice, title, useGlobals):
    """Let the user edit a structure in the database"""

    funcs = {"O": interface.edit_octave, "V": interface.edit_volume,
            "E": interface.edit_effect, "F": interface.edit_offset}

    print("\nEditing a %s." % title[:-1])
    prompt = "Choose a %s to edit." % title[:-1]
    db = database["Globals"] if useGlobals else database
    structure = ui.make_mult_choice(prompt, db[title], single=True)
    if choice == "C":
        interface.edit_channel(database, structure)
    elif choice == "I":
        interface.edit_instrument(database, structure)
    else:
        funcs[choice](structure)


def arrange_db(database):
    """Must be given the root database"""
    prompt = "Do you want to move (T)o or (F)rom the Globals database?"
    valid = list("TF")
    while True:
        choice = choose_structure()
        if choice == "B":
            return None
        where = get_choice(prompt, valid)


def db_actions(action, database, useGlobals):
    """Middle function for performing actions on the database"""

    functions = {"A": add_to_db, "D": delete_from_db,
                "V": view_db, "E": edit_db}
    actions = {"A": "adding to %s database",
                "D": "deleting from %s database",
                "V": "viewing parts of %s database",
                "E": "editing structures in %s database"}
    titles = {"C": "Channels", "I": "Instruments", "O": "Octaves",
                "V": "Volumes", "E": "Effects", "F": "Offsets"}
    if useGlobals:
        actions[action] %= "Globals"
    else:
        actions[action] %= "root"

    choice = choose_structure()
    while choice != "B":
        functions[action](database, choice, titles[choice], useGlobals)
        print("\nRepeating %s." % actions[action])
        choice = choose_structure()


def save_db(database, given, overwrite):
    """Save the database to a file"""
    prompt = "Enter the name of the file to save to."
    filename = ui.get_filename(prompt, 'w', given, overwrite)
    if filename:
        # pickle seems to not work well unless I do this?
        if filename in os.listdir("."):
            os.remove(filename)
        with open(filename, 'w') as outfile:
            pickle.dump(database, outfile)
    else:
        print("No file to save to.")


def load_db(database, given=""):
    """Load a file into or over the database"""

    prompt = "Enter the name of a file to load from."
    filename = ui.get_filename(prompt, 'r', given)
    if not filename:
        print("No file to load from.")
        return None
    with open(filename, 'r') as infile:
        newDatabase = pickle.load(infile)

    prompt = "(O)verwrite Database, or (A)ppend to it?"
    if given:
        print("Automatically appended database from %s." % filename)
    if not given and ui.get_binary_choice(prompt, list("OA"), "O", False):
        print("Overwriting database.")
        database.update(newDatabase)
    else:
        structures = ("Channels", "Instruments", "Octaves",
                        "Effects", "Volumes", "Offsets")
        for key in structures:
            database[key] += newDatabase[key]
            database["Globals"][key] += newDatabase["Globals"][key]