#!usr/bin/python

"""
Generates a completely randomized arrangement of notes for OpenMPT tracker
format, using an inter-connected database of musical structures
"""

import random
import userinput as ui


def get_random_value(valueRange):
    """
    Get a random value from within a valueRange
    valueRange is a list or tuple holding the low and high values
    """
    return random.randint(valueRange[0], valueRange[1])



def tick_spacing(channel, pos):
    """
    Decrement spacing at given position
    (0 is Instrument, 1 is Volume, 2 is Effect)
    Return True if the Channel should generate output for that position
    """
    if channel.currentSpacing[pos] <= 0:
        channel.currentSpacing[pos] = random.randint(
            channel.spacing[pos][0], channel.spacing[pos][1])
        return True
    else:
        channel.currentSpacing[pos] -= 1


def get_random_child(children, globalChildren, useGlobals):
    """
    Get a random child from a list of children, and
    optionally a list of global children
    If there are no children available, it returns None
    """

    numChildren = len(children)
    possible = numChildren
    if useGlobals:
        possible += len(globalChildren)
    if possible == 0:
        return None

    # pick a random instrument across local and global lists
    roll = random.randint(0, possible - 1)
    if roll < numChildren:
        return children[roll]
    else:
        roll -= numChildren
        return globalChildren[roll]


def format_offset(offset):
    """Format an Offset"""

    nextSA = 0
    low = 0
    high = 255

    nextSA = get_random_value(offset.sampleArea)
    if nextSA == offset.sampleArea[0]:
        low = offset.valueRange[0]
    if nextSA == offset.sampleArea[1]:
        high == offset.valueRange[1]
    value = "O%X" % get_random_value((low, high))

    return nextSA, value


def get_instrument(globalDB, channel):
    """Return a random Instrument for a Channel"""

    instrument = get_random_child(channel.instruments,
        globalDB["Instruments"], channel.useGlobals[0])
    instrument_map = list("0123456789:;<=>?@ABCDEFGHI")

    note = ""
    volume = ""
    offset = ""
    nextSA = channel.currentSA

    if instrument is not None:
        note = get_octave(globalDB, instrument)
        # since Octaves might not be defined, don't always
        # add Instrument data to note, so it'll be left blank
        if note:
            number = instrument.number
            note += "%s%s" % (instrument_map[number / 10], number % 10)
        volume = get_volume(globalDB, instrument)
        if instrument.offset is not None:
            nextSA, offset = format_offset(instrument.offset)

    return (note, volume, offset), nextSA


def get_octave(globalDB, instrument):
    """Return a random Octave for an Instrument"""
    octave = get_random_child(instrument.octaves,
            globalDB["Octaves"], instrument.useGlobals[0])
    if octave is None:
        return ""
    else:
        key = random.randint(0, len(octave.keys) - 1)
        return "%s%s" % (octave.keys[key], octave.pitch)


def get_volume(globalDB, source):
    """Return a random Volume for a Channel or an Instrument"""
    volume = get_random_child(source.volumes,
        globalDB["Volumes"], source.useGlobals[1])
    if volume is None:
        return ""
    else:
        return volume.effect + ("%X" % get_random_value(volume.valueRange))


def get_effect(globalDB, channel):
    """Return a random Effect for a Channel"""
    effect = get_random_child(channel.effects,
        globalDB["Effects"], channel.useGlobals[2])
    if effect is None:
        return ""
    else:
        return effect.effect + ("%X" % get_random_value(effect.valueRange))


def get_channel_line(database, channel):
    """Generates a single line for a channel"""

    space = "." if channel.overwrite else " "
    note = ""
    volume = ""
    effect = ""

    # interrupts creating a line in favour of setting the
    # Sample Area for the channel correctly
    if (channel.currentSpacing[0] <= 1 and
                channel.nextSA != channel.currentSA):
        channel.currentSA = channel.nextSA
        return "|%sSA%x" % ((space * 8), channel.nextSA)

    # if an Instrument is available, and should play now
    if channel.nextInstrument != "" and tick_spacing(channel, 0):
        note, volume, effect = channel.nextInstrument
        channel.nextInstrument, channel.nextSA = get_instrument(
            database["Globals"], channel)

    if not volume and tick_spacing(channel, 1):
        volume = get_volume(database["Globals"], channel)
    if not effect and tick_spacing(channel, 2):
        effect = get_effect(database["Globals"], channel)

    line = "|"
    line += note or space * 5
    line += volume or space * 3
    line += effect or space * 3
    return line


def init_channels(database):
    """Initialize a list of Channels to produce"""

    channels = []

    for channel in database["Channels"]:
        if channel.muted:
            continue
        channels.append(channel)
        channel.currentSA = 0
        channel.currentSpacing = [0, 0, 0]
        channel.nextInstrument, channel.nextSA = get_instrument(
            database["Globals"], channel)
        for x in range(3):
            tick_spacing(channel, x)

    return channels



def produce(database):
    """
    Produces a tracker song from a given database
    """

    filePrompt = "Enter the name of a file to write the tracker notes to."
    linesPrompt = "Enter how many lines you want to generate."
    filename = ui.get_filename(filePrompt, 'w')
    if filename is None:
        return None
    lines = ui.get_number(linesPrompt, 1)
    channels = init_channels(database)

    with open(filename, 'w') as outfile:
        # header required for OpenMPT to parse file
        outfile.write("ModPlug Tracker  IT")
        for _ in xrange(lines):
            line = ""
            for channel in channels:
                line += get_channel_line(database, channel)
            outfile.write(line + "\n")