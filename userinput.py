#!/usr/bin/python

from __future__ import print_function

"""Handles all non-arg user input"""

INT_HIGH = float("inf")


def get_input(msg, upper=True):
    """Prompt user with msg and return their response in uppercase"""
    response = raw_input("\n" + msg + "\n").strip()
    return response.upper() if upper else response


def get_choice(msg, valid):
    """Prompt the user with msg until they enter a valid option"""
    c = get_input(msg)
    while c not in valid:
        print("You entered %s which is not a valid option." % c,
                "\nEnter one of %s." % valid)
        c = get_input(msg)
    return c


def get_binary_choice(msg, valid=["Y", "N"], wanted="Y"):
    """Get a response to a binary choice from the user"""
    valid.append("")
    return get_choice(msg, valid).startswith(wanted)


def get_mult_choice(msg, valid, options, exit):
    """
    Prompt the user with msg and let them keep toggling
    various valid options until they enter the exit char
    """
    valid.append(exit)
    valid.append("")
    c = get_choice(msg, valid)
    status = ""
    while c != exit:
        # toggle the chosen option
        options[c] = not options[c]
        status = "on" if options[c] else "off"
        print("Option %s is now %s." % (c, status))
        c = get_choice(msg, valid)


def make_mult_choice(msg, options, exit="", default=False, single=False):
    """Wrapper for calling get_mult_choice with a generic list"""

    bools = {}
    valid = [""]
    for x, option in enumerate(options, 1):
        msg += "\n%s) %s" % (x, option)
        x = str(x)
        bools[x] = default
        valid.append(x)

    if single:
        chosen = get_choice(msg, valid)
            # enumerate gave an offset of 1
        return options[int(x) - 1]
    else:
        get_mult_choice(msg, valid, bools, exit)
        chosen = []
        for x, status in bools.items():
            if status:
                # enumerate gave an offset of 1
                chosen.append(options[int(x) - 1])
        return chosen


def convert_to_hex(value):
    """Convert value to hex format"""
    return hex(value).upper().split("X")[1]


def convert_to_int(value, getHex=False):
    """Convert value to int format"""
    if getHex:
        try:
            return int(value, 16)
        except:
            print("Could not parse %s as a hex value." % value)
    elif value.isdigit():
        return int(value)
    else:
        print("Could not parse %s as an int value." % value)
    return None
        

def get_number(msg, low=0, high=INT_HIGH, getHex=False):
    """
    Prompt user with msg until they enter
    a number of a valid type between or equal to low / high
    """
    error = "The %s is %s, but you entered %s."
    if getHex:
        bounds = (convert_to_hex(low), convert_to_hex(high))
    else:
        bounds = (low, high)
    if high == INT_HIGH:
        msg += " It must be at least %s." % bounds[0]
    else:
        msg += " It must be within %s and %s." % (bounds)

    while True:
        i = get_input(msg)
        n = convert_to_int(i, getHex)
        if type(n) != int:
            continue
        elif n < low:
            print(error % ("minimum", bounds[0], i))
        elif n > high:
            print(error % ("maximum", bounds[1], i))
        else:
            return n


def get_range(msgs, low=0, high=INT_HIGH, current=[], getHex=False):
    """Prompt the user with msgs to make a range between two values"""
    if len(current) == 2:
        for x in range(2):
            msgs[x] += " Currently it's %s."
            msgs[x] %= convert_to_hex(current[x]) if getHex else current[x]
    first = get_number(msgs[0], low, high, getHex)
    if first == high:
        print("\nYou entered the maximum value possible already, "
                "so the range is complete.")
        second = first
    else:
        second = get_number(msgs[1], first, high, getHex)
    return [first, second]


def get_value_range(current, high, getHex):
    """Let the user create a Value Range for an Effect"""
    choicePrompt = "Change value range from %s-%s? Y/N"
    rangePrompt = "Enter the %s possible value"
    if getHex:
        choicePrompt %= (convert_to_hex(current[0]),
                        convert_to_hex(current[1]))
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


def get_file(msg, mode):
    """Prompt the user to choose a file to read or write to"""
    pass