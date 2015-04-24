#!/usr/bin/python

from __future__ import print_function

"""Handles arg based user input"""

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-x")

def parse(argv=None):
    args = vars(parser.parse_args(argv))
    print(args)

parse()
parse(["-x", "5"])