#!/usr/bin/env python

"""
Generates a completely randomized arrangement of notes for OpenMPT tracker
format, using an inter-connected database of musical structures
"""

import random
import userinput as ui
import structures


def get_random_value(valueRange):
    """
    Get a random value from within a valueRange
    valueRange is a list or tuple holding the low and high values
    """
    return random.randint(valueRange[0], valueRange[1])


def tick_spacing(child):
    """
    Decrement/reset the current spacing of a child of a Channel
    Return True if the Channel should generate output for that child,
    and False otherwise
    child must be one of Channel's Instrument, Volume, or Effect dicts
    """
    if child["curSpacing"] <= 0:
        child["curSpacing"] = get_random_value(child["spacing"])
        return True
    else:
        child["curSpacing"] -= 1
        return False


def get_random_child(children, globalChildren, useGlobals):
    """
    Get a random child from a list of children, and
    optionally a list of global children
    If there are no children available, it returns None
    """
    possible = list(children)
    if useGlobals:
        for child in globalChildren:
            if child not in possible:
                possible.append(child)
    if possible == []:
        return None
    return possible[random.randint(0, len(possible) - 1)]


def get_instrument(globalDB, channel):
    """Return a random Instrument for a Channel"""

    note = ""
    volume = ""
    offset = ""
    nextSA = channel.currentSA
    instrument = get_random_child(channel.instruments["local"],
        globalDB["Instruments"], channel.instruments["useGlobals"])
    instrument_map = list("0123456789:;<=>?@ABCDEFGHI")

    if instrument is not None:
        note = get_octave(globalDB, instrument)
        # since Octaves might not be defined, don't always
        # add Instrument data to note, so it'll be left blank
        if note:
            number = instrument.number
            note += "%s%s" % (instrument_map[number / 10], number % 10)
        volume = get_volume(globalDB, instrument)
        temp = get_offset(globalDB, instrument)
        if temp:
            nextSA = temp[0]
            offset = temp[1]

    return (note, volume, offset), nextSA


def get_octave(globalDB, instrument):
    """Return a random Octave for an Instrument"""
    octave = get_random_child(instrument.octaves["local"],
            globalDB["Octaves"], instrument.octaves["useGlobals"])
    if octave is None:
        return ""
    else:
        pitch = random.randint(0, len(octave.pitches) - 1)
        return "%s%s" % (octave.pitches[pitch], octave.number)


def get_effect(globalDB, channel):
    """Return a random Effect for a Channel"""
    effect = get_random_child(channel.effects["local"],
        globalDB["Effects"], channel.effects["useGlobals"])
    if effect is None:
        return ""
    else:
        value = "%X" % get_random_value(effect.valueRange)
        return effect.effect + value.zfill(2)


def get_volume(globalDB, source):
    """Return a random Volume for a Channel or an Instrument"""
    volume = get_random_child(source.volumes["local"],
        globalDB["Volumes"], source.volumes["useGlobals"])
    if volume is None:
        return ""
    else:
        value = str(get_random_value(volume.valueRange))
        return volume.effect + value.zfill(2)


def get_offset(globalDB, instrument):
    """
    Return a random Sample Area and Offset Value for an Instrument
    If none can be found, returns None
    """
    offset = get_random_child(instrument.offsets["local"],
        globalDB["Offsets"], instrument.offsets["useGlobals"])
    if offset is None:
        return None
    else:
        return format_offset(offset)


def format_offset(offset):
    """Format an Offset"""

    nextSA = 0
    low = 0
    high = 255

    nextSA = get_random_value(offset.sampleArea)
    if nextSA == offset.sampleArea[0]:
        low = offset.valueRange[0]
    if nextSA == offset.sampleArea[1]:
        high = offset.valueRange[1]
    roll = get_random_value((low, high))
    value = "O" + ("%X" % roll).zfill(2)

    return nextSA, value


def get_channel_line(database, channel):
    """Generates a single line for a channel"""

    space = "." if channel.overwrite else " "
    note = ""
    volume = ""
    effect = ""

    # interrupts creating a line in favour of setting the
    # Sample Area for the channel correctly
    if (channel.instruments["curSpacing"] == 1 and
                channel.nextSA != channel.currentSA):
        channel.currentSA = channel.nextSA
        effect = "SA%X" % channel.nextSA

    if tick_spacing(channel.instruments) and channel.nextInstrument != "":
        note, volume, effect = channel.nextInstrument
        channel.nextInstrument, channel.nextSA = get_instrument(
            database["Globals"], channel)

    if not volume and tick_spacing(channel.volumes):
        volume = get_volume(database["Globals"], channel)
    if not effect and tick_spacing(channel.effects):
        effect = get_effect(database["Globals"], channel)

    line = "|"
    line += note or space * 5
    line += volume or space * 3
    line += effect or space * 3
    return line


def init_channels(database):
    """Initialize a list of Channels to produce"""

    channels = []

    if len(database["Channels"]) > 127:
        print("There are too many Channels available, OpenMPT only allows "
            "up to 127. Channels after 127 will be cut off.")

    for channel in database["Channels"][:127]:
        if channel.muted:
            continue
        channels.append(channel)
        channel.reset()
        channel.nextInstrument, channel.nextSA = get_instrument(
            database["Globals"], channel)
        for child in (channel.instruments, channel.volumes, channel.effects):
            tick_spacing(child)

    return channels


def output(database, filename, channels, lines):
    """Generate and output a tracker song""" 
    with open(filename, 'w') as outfile:
        # header required for OpenMPT to parse file
        outfile.write("ModPlug Tracker  IT\n")
        for _ in xrange(lines):
            line = ""
            for channel in channels:
                line += get_channel_line(database, channel)
            outfile.write(line + "\n")


def get_lines_wanted(configLines):
    """
    Prompt the user to enter a number of lines to write with
    as long as it's not defined in the config file already
    """
    if configLines:
        lines = configLines
        print("Automatically writing %s lines from the config file." % lines)
    else:
        linesPrompt = "Enter how many lines you want to generate."
        lines = ui.get_number(linesPrompt, 1)
    return lines


def produce(database, config):
    """Produce a tracker song from a given database"""

    filePrompt = "Enter the name of a file to write the tracker notes to."
    filename = ui.get_filename(filePrompt, 'w',
        config["filename"], config["overwrite"])
    if filename is None:
        return None

    repeat = True
    while repeat:
        channels = init_channels(database)
        lines = get_lines_wanted(config["lines"])
        output(database, filename, channels, lines)
        repeat = ui.get_binary_choice("Repeat? Y/N")