#!/usr/bin/env python

from __future__ import print_function

"""A Note and Effect randomizer for OpenMPT"""

import config
import tracker
import database as db
import userinput as ui


def switch_globals(useGlobals):
    """Switches the useGlobals flag and prints an appropiate message"""
    useGlobals = not useGlobals
    msg = "\nNow working on %s."
    curDB = "Globals" if useGlobals else "root"
    print(msg % curDB)
    return useGlobals, curDB


def init_aliases():
    """Initializes and returns command alias dicts"""

    aliases = {
        "help": ("help", "readme", "?"),
        "run": ("run", "produce", "generate"),
        "toggle": ("toggle", "mute", "unmute"),
        "switch": ("switch", "workon"),
        "save": ("save", "backup"),
        "load": ("load", "restore"),
        "config": ("config", "ini"),
        "wipe": ("wipe", "clear", "erase"),
        # a ridiculous number of quit aliases exist just 'cause
        "quit": ("quit", "exit", "done", "part", "finish",
                "goodbye", "bye", "no", "die",
                "leave", "escape", "out", "over",
                "explode", "crash", "close",
                "null", "void", "none", "infinity")}
    dbAliases = {
        "add": ("add", "insert", "create"),
        "delete": ("delete", "remove", "destroy"),
        "view": ("view", "look", "explore"),
        "edit": ("edit", "change", "modify"),
        "unlink": ("unlink", "unchain", "unbind"),
        "move": ("move", "organize", "rarrange")
    }
    
    aliases["database"] = []
    for terms in dbAliases.values():
        aliases["database"] += list(terms)

    return aliases, dbAliases


def parse_args(args, needed):
    """
    Parse out a positional list of needed args
    needed is a list of lists of valid terms for each argument
    if a inner list is empty, that means anything is valid
    """
    found = []
    argsLength = len(args)
    for pos, valid in enumerate(needed):
        if pos >= argsLength or (valid and args[pos] not in valid):
            found.append("")
        else:
            found.append(args[pos])
    return found


def parse_database_command(command, dbAliases, givenArgs):
    """Parse a command related to database affecting actions"""

    structNames = ["channel", "channels", "instrument", "instruments",
        "octave", "octaves", "effect", "effects",
        "volume", "volumes", "offset", "offsets"]
    dbNames = ["global", "globals", "root"]

    args = parse_args(givenArgs, [dbNames, structNames])
    # nothing was correct, so try reverse order
    if not (args[0] or args[1]):
        # if db is't specified here, assume which one to use later
        args = parse_args(givenArgs, [structNames, dbNames])
    # user specified at least one term of this ordering correctly
    else:
        # database needs to be second, so swap these around
        args[0], args[1] = args[1], args[0]
        if not args[1]:
            prompt = ("What database do you want to work on? "
                "Globals, root, or none.")
            args[1] = ui.get_choice(prompt, dbNames + ["none"], "lower")
            if args[1] == "none":
                args[1] = ""
    if not args[0]:
        prompt = "What kind of structure do you want to %s?" % command
        args[0] = ui.get_choice(prompt, structNames, "lower")

    # ensures standardization with database naming
    if not args[0].endswith("s"):
        args[0] += "s"
    args[0] = args[0].title()

    # goes through whole dict but it's quite small
    for action, terms in dbAliases.items():
        if command in terms:
            # this makes it easier to find the command type
            args.insert(0, action)
    command = "database"

    return command, args


def parse_command_entry(aliases, dbAliases, entry):
    """
    Parse a line of a command to verify it and patch it up as needed
    Return either a complete command and arg list, or blank data
    """

    entry = entry.lower().split(" ")
    if len(entry) == 0:
        print("\nYou entered nothing.")
        return ("",)
    command = entry[0]
    givenArgs = entry[1:]
    args = []
    repeat = entry[-1] == "repeat"

    configOptions = ["view", "reset", "edit"]
    loadOptions = ["overwrite", "append"]
    saveSafe = ["safely", "safe", "no", "don't", False]
    saveOverwrite = ["overwrite", "dangerously", True]

    if command in aliases["help"]:
        command = "help"
    elif command in aliases["run"]:
        command = "run"
    elif command in aliases["switch"]:
        command = "switch"
    elif command in aliases["wipe"]:
        command = "wipe"
    elif command in aliases["quit"]:
        command = "quit"
    elif (command in aliases["database"]):
        command, args = parse_database_command(command, dbAliases, givenArgs)

    elif command in aliases["toggle"]:
        args = parse_args(givenArgs, [["channels"]])
        if not args[0]:
            prompt = "Do you mean %s Channels? Y/N" % command
            if not ui.get_binary_choice(prompt):
                command = ""

    elif command in aliases["save"]:
        args = parse_args(givenArgs, [[], saveSafe + saveOverwrite])
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

    elif command in aliases["load"]:
        args = parse_args(givenArgs, [[], loadOptions])
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

    elif command in aliases["config"]:
        args = parse_args(givenArgs, [configOptions])
        if not args[0]:
            prompt = ("\nWhat do you want to do to the config file? "
                "View, reset, or edit it?")
            arg[0] = ui.get_choice(prompt, configOptions)
        print("\nYou want to %s the config file!" % args[0])

    return command, args, repeat


def main_menu():
    """Run the main menu of the program"""

    # clear a bit of space for program start-up
    print()

    useGlobals = False
    curDB  = "root"
    prompt = "Current Default Database: %s.\nEnter a valid command, or help."
    numberBase = "default"
    aliases, dbAliases = init_aliases()

    dbConfig, production = config.init_config_file()
    database = db.init_db(dbConfig)

    command = ""
    while command != "quit":
        entry = ui.get_input(prompt % curDB , "lower")
        command, args, repeat = parse_command_entry(aliases, dbAliases, entry)
        # print(command, args, repeat)

        if command == "help":
            print("\nI'm working on the help file!!")
        if command == "run":
            tracker.produce(database, production)
        elif command == "switch":
            useGlobals, curDB  = switch_globals(useGlobals)
        elif command == "database":
            db.db_actions(database, useGlobals, args)
        elif command == "save":
            db.save_db(database, args, dbConfig)
        elif command == "wipe":
            wipePrompt = "Are you SURE you want to erase the database? Y/N"
            if ui.get_binary_choice(wipePrompt):
                database = db.init_db()
        elif command != "quit":
            print("\n\"%s\" is not a recognized command." % command)

main_menu()