#!/usr/bin/env python

from __future__ import print_function

"""Functions for directly handling the database"""

import os
import copy
import pickle

import interface
import structures
import userinput as ui


def init(dbConfig=None):
    """Initalize a new database, optionally using config file settings"""
    database = {}
    database["root"] = {"Channels": [], "Instruments": [], "Octaves": [],
                "Effects": [], "Volumes": [], "Offsets": []}
    database["global"] = copy.deepcopy(database["root"])
    # global Channels do not do anything, and so cannot exist
    del database["global"]["Channels"]
    if dbConfig is not None and dbConfig["load"]:
        load(database, dbConfig["load"], "init")
    return database


def add_to(database, curDB, structType):
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

    database[curDB][structType].append(new)


def delete_from(database, curDB, structType):
    """Let the user delete structures from the Database."""

    prompt = "Choose %s %s to delete. Press C to continue." % (
        curDB, structType)
    toDelete = ui.make_mult_choice(prompt, database[curDB][structType], "C")

    for structure in toDelete:
        interface.remove_all_links(structure)
        database[curDB][structType].remove(structure)

    deleted = len(toDelete)
    msg = "\nDeleted %s %s" % (deleted, curDB)
    if deleted == 1:
        msg += structType[:-1] + "."
    else:
        msg += structType + "."
    print(msg)


def view(database, curDB, structType):
    """Let the user page through part of the database"""

    pages = interface.paginate(database[curDB][structType])
    if pages[0] == []:
        prompt = "There are no %s %s to view. Press any key to continue."
        ui.get_input(prompt % (curDB, structType))
        return None

    choice = ""
    curPage = 1
    header = "\nViewing Page %s"
    header += "/%s of %s %s" % (len(pages), curDB, structType)

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


def edit(database, curDB, structType):
    """Let the user edit a structure in the database"""

    functions = {
        "Octaves": interface.edit_octave,"Volumes": interface.edit_volume,
        "Effects": interface.edit_effect, "Offsets": interface.edit_offset}

    prompt = "Choose a %s to edit." % structType[:-1]
    structure = ui.make_mult_choice(prompt, database[curDB][structType],
        single=True)

    if structType == "Channels":
        interface.edit_channel(database, structure)
    elif structType == "Instruments":
        interface.edit_instrument(database, structure)
    else:
        functions[structType](structure)


def basic_actions(database, curDB, action, structType, dbToUse=""):
    """Middle function for performing basic actions on the database"""
    if dbToUse and dbToUse != "default":
        curDB = dbToUse
    if curDB == "global" and structType == "Channels":
        msg = "\nYou can't %s global Channels, as there can't be any."
        print(msg % action)
        return None
    functions = {"add": add_to, "delete": delete_from,
                "view": view, "edit": edit}
    functions[action](database, curDB, structType)


def arrange(database):
    """Must be given the root database"""
    prompt = "Do you want to move (T)o or (F)rom the global database?"
    valid = list("TF")


def save(database, dbConfig, filename="", overwrite=None):
    """Save the database to a file"""

    if not filename:
        filename = dbConfig["save"]
        if overwrite is None:
            overwrite = bool(dbConfig["overwrite"])

    prompt = "Enter the name of the file to save to."
    filename = ui.get_filename(prompt, 'w', filename, overwrite)
    if not filename:
        print("\nNo file to save to.")
    else:
        # pickle seems to not work well unless I do this(!)
        if filename in os.listdir("."):
            os.remove(filename)
        with open(filename, 'w') as outfile:
            pickle.dump(database, outfile)


def load(database, filename="", mode=""):
    """Load a file into or over the database"""

    prompt = "Enter the name of a file to load from."
    filename = ui.get_filename(prompt, 'r', filename)
    if not filename:
        print("\nNo file to load from.")
        return None
    with open(filename, 'r') as infile:
        newDatabase = pickle.load(infile)
    if not mode:
        prompt = "Overwrite Database, or append to it?"
        mode = ui.get_choice(prompt, ["overwrite", "append"], "lower")

    if mode == "init":
        print("\nAutomatically appended database from \"%s\"." % filename)
    elif mode == "overwrite":
        print("\nOverwriting database with \"%s\"." % filename)
        database.update(newDatabase)
    elif mode == "append":
        print("\nAppending database with \"%s\"." % filename)
        # only root DB gets Channels
        database["root"]["Channels"] += newDatabase["root"]["Channels"]
        structs = ("Instruments", "Octaves", "Effects", "Volumes", "Offsets")
        for key in structs:
            database["root"][key] += newDatabase["root"][key]
            database["global"][key] += newDatabase["global"][key]