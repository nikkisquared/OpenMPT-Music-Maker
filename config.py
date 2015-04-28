#!usr/bin/python

import ConfigParser


def init_config_file():
    """Opens a config file to parse through it and returns it"""

    config = ConfigParser.ConfigParser()

    if not config.read("config.ini"):
        # make ini from scratch
        pass
    production = dict(config.items("Production"))
    production["overwrite"] = bool(production["overwrite"])
    dbConfig = dict(config.items("Database"))
    dbConfig["overwrite"] = bool(dbConfig["overwrite"])

    return dbConfig, production