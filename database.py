#!/usr/bin/env python

from __future__ import print_function

"""Functions for directly handling the database"""

import os
import copy
import pickle

import interface
import structures
import userinput as ui


def init_db(dbConfig=None):
    """Initalize a new database, optionally using config file settings""" 
    database = {"Channels": [], "Instruments": [], "Octaves": [],
                "Effects": [], "Volumes": [], "Offsets": []}
    database["Globals"] = copy.deepcopy(database)
    if dbConfig and dbConfig["load"]:
        load_db(database, dbConfig["load"])
    return database


def add_to_db(database, useGlobals, structType):
    """Let the user add a structure to a database"""

    functions = {
        "Octaves": interface.make_octave, "Volumes": interface.make_volume,
        "Effects": interface.make_effect, "Offsets": interface.make_offset}

    print("\nMaking a %s." % structType[:-1])
    if structType == "Channels":
        new = interface.make_channel(database)
    elif structType == "Instruments":
        new = interface.make_instrument(database)
    else:
        new = functions[structType]()

    if useGlobals:
        database["Globals"][structType].append(new)
    else:
        database[structType].append(new)


def delete_from_db(database, useGlobals, structType):
    """Let the user delete structures from the Database."""

    if useGlobals:
        db = database["Globals"]
        globalNote = "Global "
    else:
        db = database
        globalNote = ""

    prompt = "Choose %s%s to delete. Press C to continue." % (
        globalNote, structType)
    deleteThese = ui.make_mult_choice(prompt, db[structType], "C")

    for structure in deleteThese:
        interface.remove_all_links(structure)
        db[structType].remove(structure)

    deleted = len(deleteThese)
    msg = "\nDeleted %s %s" % (deleted, globalNote)
    if deleted == 1:
        msg += structType[:-1] + "."
    else:
        msg += structType + "."
    print(msg)


def view_db(database, useGlobals, structType):
    """Let the user page through part of the database"""

    if useGlobals:
        db = database["Globals"]
        globalNote = "Global "
    else:
        db = database
        globalNote = ""

    pages = interface.paginate(db[structType])
    if pages[0] == []:
        prompt = "There are no %s%s to view. Press any key to continue."
        ui.get_input(prompt % (globalNote, structType))
        return None

    choice = ""
    curPage = 1
    header = "\nViewing Page %s"
    header += "/%s of %s%s" % (len(pages), globalNote, structType)

    while choice != "B":

        print(header % curPage)
        for item in pages[curPage - 1]:
            print(item)

        prompt = ""
        valid = ["B"]
        if curPage > 1:
            prompt += "(P)revious, "
            valid.append("P")
        prompt += "(B)ack" 
        if curPage < len(pages):
            prompt += ", or (N)ext"
            valid.append("N")

        choice = ui.get_choice(prompt, valid)
        if choice == "P":
            curPage -= 1
        if choice == "N":
            curPage += 1


def edit_db(database, useGlobals, structType):
    """Let the user edit a structure in the database"""

    functions = {
        "Octaves": interface.edit_octave,"Volumes": interface.edit_volume,
        "Effects": interface.edit_effect, "Offsets": interface.edit_offset}

    prompt = "Choose a %s to edit." % structType[:-1]
    db = database["Globals"] if useGlobals else database
    structure = ui.make_mult_choice(prompt, db[structType], single=True)

    if structType == "Channels":
        interface.edit_channel(database, structure)
    elif structType == "Instruments":
        interface.edit_instrument(database, structure)
    else:
        functions[structType](structure)


def arrange_db(database):
    """Must be given the root database"""
    prompt = "Do you want to move (T)o or (F)rom the Globals database?"
    valid = list("TF")


def db_actions(database, useGlobals, args):
    """Middle function for performing basic actions on the database"""
    action = args[0]
    structType = args[1]
    if args[2]:
        useGlobals = False if args[2] == "root" else True
    functions = {"add": add_to_db, "delete": delete_from_db,
                "view": view_db, "edit": edit_db}
    functions[action](database, useGlobals, structType)


def save_db(database, args, dbConfig):
    """Save the database to a file"""
    filename = args[0]
    overwrite = args[1]
    prompt = "Enter the name of the file to save to."
    filename = ui.get_filename(prompt, 'w', filename, overwrite)
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
    if not given and ui.get_binary_choice(prompt, list("OA"), "O"):
        print("Overwriting database.")
        database.update(newDatabase)
    else:
        structures = ("Channels", "Instruments", "Octaves",
                        "Effects", "Volumes", "Offsets")
        for key in structures:
            database[key] += newDatabase[key]
            database["Globals"][key] += newDatabase["Globals"][key]