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
        "switch": ("switch", "workon"),
        "base": ("base", "number", "numeral"),
        "save": ("save", "backup"),
        "load": ("load", "restore"),
        "config": ("config", "ini"),
        "wipe": ("wipe", "clear", "erase"),
        # a ridiculous number of quit aliases exist just 'cause
        "quit": ("quit", "exit", "done", "part", "finish",
                "goodbye", "bye", "no", "die",
                "leave", "escape", "out", "over",
                "explode", "crash", "overflow", "close",
                "null", "void", "none", "infinity")}
    dbAliases = {
        "add": ("add", "insert", "create"),
        "delete": ("delete", "remove", "destroy"),
        "view": ("view", "look", "explore"),
        "edit": ("edit", "change", "modify"),
        "copy": ("copy", "duplicate"),
        "unlink": ("unlink", "unchain", "unbind"),
        "move": ("move", "organize", "arrange", "rearrange")
    }

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
        prompt = ("What database do you want to work on? "
            "Global, root, or default.")
        args[1] = ui.get_choice(prompt, dbNames, "lower")

    # ensures standardization with database naming
    if not args[0].endswith("s"):
        args[0] += "s"
    args[0] = args[0].title()

    return command, args


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
    for cmd in aliases.keys():
        if command in aliases[cmd]:
            command = cmd

    configOptions = ["view", "reset", "edit"]
    loadOptions = ["overwrite", "append"]
    saveSafe = ["safely", "safe", "no", "don't", False]
    saveOverwrite = ["overwrite", "dangerously", True]

    if command in dbAliases.keys():
        command, args = parse_database_command(dbAliases, command, args)

    elif command == "save":
        args = parse_args(args, [[], saveSafe + saveOverwrite])
        if not args[0]:
            prompt = "What file do you want to save to?"
            args[0] = ui.get_input(prompt, "")
        if not args[1]:
            prompt = "Do you want to overwrite %s? Y/N" % args[0]
            args[1] = ui.get_binary_choice(prompt)
        if args[1] in saveOverwrite:
            print("\nOverwriting %s." % args[0])
            args[1] = True
        else:
            print("\nAttempting to save %s as a new file." % args[0])
            args[1] = False

    elif command == "load":
        args = parse_args(args, [[], loadOptions])
        if not args[0]:
            prompt = "What file do you want to load?"
            args[0] = ui.get_input(prompt, "")
        if not args[1]:
            prompt = ("Do you want to append to or overwrite the database "
                "with %s?" % args[0])
            args[1] = ui.get_choice(prompt, loadOptions, "")
        if args[1] == "overwrite":
            print("\nOverwriting the database with %s." % args[0])
        elif args[1] == "append":
            print("\nAppending the database with %s." % args[0])

    elif command == "config":
        args = parse_args(args, [configOptions])
        if not args[0]:
            prompt = ("\nWhat do you want to do to the config file? "
                "View, reset, or edit it?")
            arg[0] = ui.get_choice(prompt, configOptions)
        print("\nYou want to %s the config file!" % args[0])

    return command, args


def main_menu():
    """Run the main menu of the program"""

    # clear a bit of space for program start-up
    print()

    repeat = False
    numberBase = "default"
    curDB  = "root"
    prompt = "Current Default Database: %s.\nEnter a valid command, or help."

    aliases, dbAliases = init_aliases()
    dbConfig, production = config.init_config_file()
    database = db.init_db(dbConfig)

    command = ""
    while command != "quit":
        entry = ui.get_input(prompt % curDB , "lower")
        command, args = parse_entry(aliases, entry)
        # print(command, args)

        if command == "help":
            # try to grab whatever specific command there could be
            args = parse_args(args, [[]])
            print("\nI'm working on the help file!!")
        if command == "run":
            tracker.produce(database, production)
        elif command == "switch":
            curDB = "Global" if curDB == "root" else "root"
            print("\nNow working on %s." % curDB)
        elif command == "database":
            db.db_actions(database, curDB, command, args)
        elif command == "save":
            db.save_db(database, args, dbConfig)
        elif command == "wipe":
            wipePrompt = "Are you SURE you want to erase the database? Y/N"
            if ui.get_binary_choice(wipePrompt):
                database = db.init_db()
        elif command != "quit":
            print("\n\"%s\" is not a recognized command." % command)

main_menu()