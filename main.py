#!/usr/bin/env python

from __future__ import print_function

"""A Note and Effect randomizer for OpenMPT"""

import config
import tracker
import database as db
import userinput as ui


def init_aliases():
    """Initializes and returns command alias dicts"""

    aliases = {
        "help": ("help", "readme", "info", "?"),
        "verbose": ("verbose", "verbosity"),
        "aliases": ("aliases", "aka"),
        "repeat": ("repeat", "redo"),
        "run": ("run", "produce", "generate"),
        "toggle": ("toggle", "mute", "unmute"),
        "switch": ("switch", "workon", "cd"),
        "global": ("global",),
        "root": ("root",),
        "base": ("base", "number", "numeral"),
        "save": ("save", "backup"),
        "load": ("load", "restore"),
        "config": ("config", "ini"),
        "wipe": ("wipe", "erase"),
        # a ridiculous number of quit aliases exist just 'cause
        "quit": ("quit", "exit", "done", "part", "finished",
                "goodbye", "bye", "no", "die",
                "leave", "escape", "out", "over",
                "explode", "crash", "overflow", "close",
                "null", "void", "none", "infinity")
    }
    dbAliases = {
        "add": ("add", "insert", "create"),
        "delete": ("delete", "remove", "destroy"),
        "view": ("view", "look", "explore"),
        "edit": ("edit", "change", "modify"),
        "copy": ("copy", "duplicate"),
        "unlink": ("unlink", "unchain", "unbind"),
        "move": ("move", "organize", "arrange", "rearrange")
    }
    aliases["database"] = []
    for terms in dbAliases.values():
        aliases["database"] += list(terms)

    return aliases, dbAliases


def parse_args(args, needed):
    """
    Parse out a positional list of needed args
    needed is a list of lists of valid terms for each argument
    If a inner list is empty, that means anything is valid
    Return a list of args if multiple needed, otherwise return a single arg
    """
    found = []
    argsLength = len(args)
    for pos, valid in enumerate(needed):
        if pos >= argsLength or (valid and args[pos] not in valid):
            found.append("")
        else:
            found.append(args[pos])
    return found


def parse_database_command(dbAliases, command, givenArgs):
    """Parse a command related to database affecting actions"""

    structNames = ["channel", "channels", "instrument", "instruments",
        "octave", "octaves", "effect", "effects",
        "volume", "volumes", "offset", "offsets"]
    dbNames = ["global", "root", "default"]

    # goes through whole dict, but it's quite small
    for action, terms in dbAliases.items():
        if command in terms:
            command = action

    args = parse_args(givenArgs, [structNames, dbNames])
    # if nothing was correct, try reverse order and swap the results
    if not (args[0] or args[1]):
        args = parse_args(givenArgs, [dbNames, structNames])
        args[0], args[1] = args[1], args[0]
    if not args[0]:
        prompt = "What kind of structure do you want to %s?" % command
        args[0] = ui.get_choice(prompt, structNames, "lower")
    # only ask for a database if the user attempted to specify it
    if len(givenArgs) > 1 and not args[1]:
        prompt = ("Which database do you mean? global, root, or default.")
        args[1] = ui.get_choice(prompt, dbNames, "lower")

    # ensures standardization with database naming
    if not args[0].endswith("s"):
        args[0] += "s"
    args[0] = args[0].title()
    # makes sure the action is the first arg
    args.insert(0, command)

    return args


def parse_entry(aliases, dbAliases, entry):
    """
    Parse a line of a command to verify it and patch it up as needed
    Return either a complete command and arg list, or blank data
    """

    entry = entry.lower().split(" ")
    if len(entry) == 0:
        print("\nYou entered nothing.")
        return ("",)
    command = entry[0]
    args = entry[1:]

    # finds and applies master alias
    for cmd, names in aliases.items():
        if command in names:
            command = cmd

    if command == "help":
        # check first arg
        pass
    elif command == "switch":
        args = parse_args(args, [["root", "global"]])
        if args[0]:
            command = args[0]
    elif command == "database":
        args = parse_database_command(dbAliases, entry[0], args)
    elif command == "load":
        args = parse_args(args, [[], ["overwrite", "append"]])

    elif command == "save":
        args = parse_args(args, [[], ["overwrite", "safe", "safely"]])
        if args[1]:
            args[1] = bool(args[1] == "overwrite")
        else:
            args[1] = None
            
    elif command == "config":
        configOptions = ["view", "reset", "edit"]
        args = parse_args(args, [configOptions])
        if not args[0]:
            prompt = ("\nWhat do you want to do to the config file? "
                "View, reset, or edit it?")
            args[0] = ui.get_choice(prompt, configOptions, "lower")
        print("\nYou want to %s the config file!" % args[0])

    return command, args


def change_database(curDB, command):
    """Changes the database as requested"""
    if curDB == command:
        print("\nThe default database is already %s." % curDB)
    else:
        if command == "switch":
            print('hello')
            curDB = "global" if curDB == "root" else "root"
        else:
            curDB = command
        print("\nThe default database is now %s." % curDB)
    return curDB


def main_menu():
    """Run the main menu of the program"""

    repeat = False
    numberBase = "default"
    curDB  = "root"
    prompt = ("Repeat is %s.\nCurrent Default Database: %s.\n"
        "Enter a valid command, or help.")

    aliases, dbAliases = init_aliases()
    dbConfig, production = config.init_config_file()
    database = db.init(dbConfig)

    command = ""
    while command != "quit":
        entry = ui.get_input(
            prompt % (("on" if repeat else "off"), curDB), "lower")
        command, args = parse_entry(aliases, dbAliases, entry)

        if command == "help":
            print("\nI'm working on the help file!!")
        elif command == "repeat":
            repeat = not repeat
            print("\nRepeat is now %s." % ("on" if repeat else "off"))
        elif command == "run":
            tracker.produce(database, production)
        elif command in ("switch", "root", "global"):
            curDB = change_database(curDB, command)
        elif command == "database":
            db.basic_actions(database, curDB, *tuple(args))
        elif command == "load":
            db.load(database, *tuple(args))
        elif command == "save":
            db.save(database, dbConfig, *tuple(args))
        elif command == "wipe":
            wipePrompt = "Are you SURE you want to erase the database? Y/N"
            if ui.get_binary_choice(wipePrompt):
                database = db.init()
        elif command != "quit":
            print("\n\"%s\" is not a recognized command." % command)

main_menu()