#!/usr/bin/env python

from __future__ import print_function

"""A Note and Effect randomizer for OpenMPT"""

import os
import copy

import config
import tracker
import database as db
import userinput as ui


def switch_globals(useGlobals):
    """Switches the useGlobals flag and prints an appropiate message"""
    if useGlobals:
        print("No longer working on Globals.")
    else:
        print("Now working on Globals.")
    return not useGlobals


def context_header(menu, useGlobals):
    """Used for varying menu headers depending on context"""
    header = ""
    if menu == "database":
        if useGlobals:
            header = "Working on Globals database\n"
        else:
            header = "Working on root database\n"
    return header


def init_menus():
    """Initializes and returns menu dialogs"""

    prompt = {}
    valid = {}

    prompt["root"] = (
        "Choose an option:\n"
        "(R)un Program\t(T)oggle Channels\n"
        "(P)arse Args\t(B)atch Operations\n"
        "(D)atabase Operations Menu\n"
        "(S)ave Database\t(L)oad Database\n"
        "(I)ni File Settings\n"
        "(Q)uit")
    valid["root"] = list("BDILPQRST")

    prompt["database"] = (
        "Choose an option:\n"
        "(A)dd Things\t(D)elete Things\n"
        "(V)iew Things\t(E)dit Things\n"
        "(M)ove Things\t(G)lobals Switch\n"
        "(L)ink Explorer\n"
        # ie default/decimal/hex
        "(N)umber Base Switch\n"
        "(B)ack to Main Menu")
    valid["database"] = list("ABDEGLMNV")

    return prompt, valid


def main():
    """Run the main menu of the program"""

    prompt, valid = init_menus()
    menu = "root"
    
    database = {"Channels": [], "Instruments": [], "Octaves": [],
                "Effects": [], "Volumes": [], "Offsets": []}
    database["Globals"] = copy.deepcopy(database)
    useGlobals = False
    numberBase = "default"

    dbConfig, production = config.init_config_file()
    if dbConfig["load"]:
        db.load_db(database, dbConfig["load"])

    choice = ""
    while choice != "Q":
        header = context_header(menu, useGlobals)
        choice = ui.get_choice(header + prompt[menu], valid[menu])

        if menu == "database":
            if choice == "B":
                menu = "root"
            elif choice in "ADVE":
                db.db_actions(choice, database, useGlobals)
            elif choice == "M":
                db.arrange_db(database)
            elif choice == "G":
                useGlobals = switch_globals(useGlobals)
        elif choice == "Q":
            continue
        elif choice == "R":
            tracker.produce(database, production)
        elif choice == "D":
            menu = "database"
        elif choice == "S":
            db.save_db(database, dbConfig["save"], dbConfig["overwrite"])
        elif choice == "L":
            db.load_db(database)
        else:
            msg = "You chose %s, but it hasn't been implemented yet :("
            print(msg % choice)

main()