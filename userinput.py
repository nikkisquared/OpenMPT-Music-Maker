#!/usr/bin/env python

from __future__ import print_function

"""Handles all non-arg user input"""

import os

INFINITY = float("inf")


def get_input(prompt, case="upper"):
    """
    Prompt user and return their response in desired case
    case can be upper (default), lower, title, or preserve
    Raise a ValueError if case is incorrect, to prevent unexpected bugs
    """
    response = raw_input("\n" + prompt + "\n").strip()
    if case == "upper":
        return response.upper()
    elif case == "lower":
        return response.lower()
    elif case == "title":
        return response.title()
    elif case == "preserve":
        return response
    else:
        raise ValueError("Incorrect case given, potentially fatal.")


def get_choice(prompt, valid, case="upper"):
    """Prompt the user until they enter a valid option"""
    c = get_input(prompt, case)
    while valid and c not in valid:
        print("\nYou entered \"%s\" which is not a valid option." % c,
                "\nEnter one of %s." % valid)
        c = get_input(prompt, case)
    return c


def get_binary_choice(prompt, valid=["Y", "N", "YES", "NO", ""], wanted="Y"):
    """
    Get a response to a binary choice from the user, where
    the only test is whether or not they picked a specified option
    This only compares the start of the input to the wanted input
    if valid is an empty list, user can enter anything
    Assumes uppercase for valid and wanted variables
    """
    if valid:
        return get_choice(prompt, valid).startswith(wanted)
    else:
        return get_input(prompt).startswith(wanted)


def get_mult_choice(prompt, valid, options, exit):
    """
    Prompt the user and let them keep toggling
    various valid options until they enter the exit char
    """
    valid.append(exit)
    c = get_choice(prompt, valid)
    status = ""
    while c != exit:
        # toggle the chosen option
        options[c] = not options[c]
        status = "on" if options[c] else "off"
        print("Option %s is now %s." % (c, status))
        c = get_choice(prompt, valid)


def make_mult_choice(prompt, options, exit="", default=False, single=False):
    """
    Wrapper for making a multiple choice prompt from a generic list
    Defaults to using get_mult_choice and returns all True items, 
    but if single is True, it will use get_choice and return only one
    """

    bools = {}
    valid = []
    for n, option in enumerate(options, 1):
        prompt += "\n%s) %s" % (n, option)
        n = str(n)
        bools[n] = default
        valid.append(n)

    if single:
        chosen = get_choice(prompt, valid)
        # enumerate gave an offset of 1
        return options[int(chosen) - 1]
    else:
        get_mult_choice(prompt, valid, bools, exit)
        chosen = []
        for i, status in bools.items():
            if status:
                # enumerate gave an offset of 1
                chosen.append(options[int(i) - 1])
        return chosen


def convert_to_int(value, getHex=False):
    """Convert value to int format"""
    if getHex:
        try:
            return int(value, 16)
        except:
            print("Could not parse \"%s\" as a hex value." % value)
    else:
        if value.isdigit():
            return int(value)
        else:
            print("Could not parse \"%s\" as an int value." % value)
        

def get_number(prompt, low=0, high=INFINITY, getHex=False):
    """
    Prompt user until they enter a number of a valid type
    between or equal to low / high
    Defaults to retrieving an integer, but setting getHex to True
    will try to retrieve a hex character instead
    """
    error = "The %s is %s, but you entered %s."
    if getHex:
        bounds = ("%X" % low, "%X" % high)
    else:
        bounds = (low, high)
    if high == INFINITY:
        prompt += " It must be at least %s." % bounds[0]
    else:
        prompt += " It must be within %s and %s." % (bounds)

    while True:
        i = get_input(prompt)
        n = convert_to_int(i, getHex)
        if type(n) != int:
            continue
        elif n < low:
            print(error % ("minimum", bounds[0], i))
        elif n > high:
            print(error % ("maximum", bounds[1], i))
        else:
            return n


def get_range(prompts, low=0, high=INFINITY, current=[], getHex=False):
    """
    Prompt to make a range between two values
    prompts is a list of two distinct messages for the
    first and second values, respectively
    """
    if len(current) == 2:
        for x in range(2):
            prompts[x] += " Currently it's %s."
            prompts[x] %= "%X" % current[x] if getHex else current[x]
    first = get_number(prompts[0], low, high, getHex)
    if first == high:
        print("\nYou entered the maximum value possible already, "
                "so the range is complete.")
        second = first
    else:
        second = get_number(prompts[1], first, high, getHex)
    return (first, second)


def get_value_range(current, high, getHex):
    """Let the user create a Value Range for an Effect"""
    choicePrompt = "Change value range from %s-%s? Y/N"
    rangePrompt = "Enter the %s possible value"
    if getHex:
        choicePrompt %= ("%X" % current[0], "%X" % current[1])
        rangePrompt += " in hex."
    else:
        choicePrompt %= current[0], current[1]
        rangePrompt += "."
    if get_binary_choice(choicePrompt):
        return get_range(
            [rangePrompt % "lowest", rangePrompt % "highest"],
            0, high, current, getHex)
    else:
        return current


def verify_filename(filename, mode, overwrite):
    """
    Verify a file for writing or reading and return it on success
    Return None if there is a problem and the user declines to try again
    """

    againPrompt = "Pick a different file? Y/N"
    existsPrompt = "File %s already exists. Overwrite? Y/N"
    found = filename in os.listdir(".")

    if mode == 'r' and not found:
        # if found:
        #     print("\nReading from \"%s\"." % filename)
        print("\"%s\" cannot be read as it doesn't exist." % filename)
        filename = ""
        if not get_binary_choice(againPrompt):
            return None

    elif mode == 'w':
        if not found:
            print("\nWriting to \"%s\"." % filename)
        elif overwrite:
            print("\nAutomatically overwriting \"%s\"." % filename)
        elif get_binary_choice(existsPrompt % filename):
            print("\nOverwriting \"%s\"." % filename)
        else:
            filename = ""
            if not get_binary_choice(againPrompt):
                return None

    return filename


def get_filename(prompt, mode, filename="", overwrite=False):
    """
    Prompt the user to choose a file to read or write to
    Return the pathname for it
    If the user declines to open any file, return a blank string
    filename if specified will first verify it for operations
    overwrite if True will not ask before overwriting a file
    """
    if filename:
        filename = verify_filename(filename, mode, overwrite)
    while not filename:
        # user declined to try again in verify_filename
        if filename is None:
            return ""
        filename = raw_input("\n" + prompt + "\n").strip()
        filename = verify_filename(filename, mode, overwrite)
    return filename