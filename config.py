#!/usr/bin/env python

from __future__ import print_function

"""Handles parsing and correction of config file for the program"""

import ConfigParser


def check_boolean(section, variable, value, default=False):
    """Check that a config variable is a proper boolean"""
    if value in (0, 1, "True", "False"):
        return bool(value)
    else:
        print("Boolean value (0/True or 1/False) was expected in "
            "%s %s but %s was found." % (section, variable, value))
        return default


def check_integer(section, variable, value):
    """Check that a config variable is a proper integer"""
    if value.isdigit():
        return int(value)
    else:
        print("Interger value was expected in %s %s but %s was found." % (
            section, variable, value))
        return 0


def init_config_file():
    """Opens a config file to parse through it and returns it"""

    config = ConfigParser.ConfigParser()

    if not config.read("config.ini"):
        # make ini from scratch
        pass

    production = dict(config.items("Production"))
    production["overwrite"] = check_boolean("Production", "overwrite",
        production["overwrite"])
    production["lines"] = check_integer("Production", "lines",
        production["lines"])

    dbConfig = dict(config.items("Database"))
    dbConfig["overwrite"] = check_boolean("Database", "overwrite",
            dbConfig["overwrite"])

    return dbConfig, production