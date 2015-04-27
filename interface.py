#!/usr/bin/python

from __future__ import print_function

"""Provides an interface to let users create any structure"""

import userinput as ui
import structures


def paginate(array, pageLength=10):
    """Turn array into a a list of pages spaced out by pageLength"""
    pages = []
    newPage = []
    for count, item in enumerate(array):
        if count > 0 and count % 10 == 0:
            pages.append(newPage)
            newPage = []
        newPage.append(item)
    pages.append(newPage)
    return pages


def add_x_to_y_at_z(x, y, z):
    """
    Adds as many elements of x possible to y's z;
    inserts references back to y in each x
    x is a list of structures
    y is a Channel or Instrument
    z is the list to add structures to
    """
    for thing in x:
        if thing and thing not in z:
            z.append(thing)
            thing.usedBy.append(y)


def make_channel(database):
    """Wrapper for creating a new Channel"""
    return edit_channel(database, structures.Channel())


def edit_channel(database, channel):
    """Let the user edit an existing Channel"""

    addTo = (channel.instruments, channel.volumes, channel.effects)
    for pos, term in enumerate(["Instruments", "Volumes", "Effects"]):

        if ui.get_binary_choice("Add %s? Y/N" % term):
            chosen = ui.make_mult_choice(
                "Press C to continue. Toggle %s to use:" % term,
                database[term] + database["Globals"][term], "C")
            add_x_to_y_at_z(chosen, channel, addTo[pos])

        prompt = "Change %s spacing from %s to %s? Y/N" % (
                term, channel.spacing[pos][0], channel.spacing[pos][1])
        if ui.get_binary_choice(prompt):
            msgs = ["Minimum %s spacing?" % term,
                    "Maximum %s spacing?" % term]
            channel.spacing[pos] = ui.get_range(msgs)
        prompt = "Turn %s global " + term + "? It's currently %s. Y/N"
        prompt %= ("off", "on") if channel.useGlobals[pos] else ("on", "off")
        if ui.get_binary_choice(prompt):
            channel.useGlobals[pos] = not channel.useGlobals[pos]

    prompt = "Turn %s overwriting? It's currently %s. Y/N"
    prompt %= ("off", "on") if channel.overwrite else ("on", "off")
    if ui.get_binary_choice(prompt):
        channel.overwrite = not channel.overwrite

    prompt = "%s the Channel? It's currently %s. Y/N"
    if channel.muted:
        prompt %= ("Unmute", "muted")
    else:
        prompt %= ("Mute", "unmuted")
    if ui.get_binary_choice(prompt):
        channel.muted = not channel.muted

    return channel


def make_instrument(database):
    """Wrapper for creating a new Instrument"""
    return edit_instrument(database, structures.Instrument())


def edit_instrument(database, instrument):
    """Let the user edit an existing Instrument"""

    prompt = "Change Instrument number from %s? Y/N" % instrument.number
    if not instrument.number or ui.get_binary_choice(prompt):
        prompt = "Enter a number for the Instrument."
        instrument.number = ui.get_number(prompt, 1, 255)

    addTo = (instrument.octaves, instrument.volumes)

    for pos, term in enumerate(["Octaves", "Volumes"]):
        if ui.get_binary_choice("Add %s? Y/N"% term):
            chosen = ui.make_mult_choice(
                "Press C to continue. Toggle %s to use:" % term,
                database[term] + database["Globals"][term], "C")
            add_x_to_y_at_z(chosen, instrument, addTo[pos])

        prompt = "Turn %s global " + term + "? It's currently %s. Y/N"
        if instrument.useGlobals[pos]:
            prompt %= ("off", "on")
        else:
            prompt %= ("on", "off")
        if ui.get_binary_choice(prompt):
            instrument.useGlobals[pos] = not instrument.useGlobals[pos]

    if ui.get_binary_choice("Add an Offset? Y/N"):
        instrument.offset = ui.make_mult_choice(
            "Choose an octave below.", database["Offsets"], single=True)
        instrument.offset.usedBy.append(instrument)

    return instrument


def make_octave():
    """Wrapper to let the user create an Octave"""
    return edit_octave(structures.Octave())


def edit_octave(octave):
    """Let the user edit an existing Octave"""
    prompt = "Enter a pitch for the Octave. Currently it's %s."
    octave.pitch = ui.get_number(prompt % octave.pitch, 0, 9)
    prompt = "Change key limits? Y/N"
    if ui.get_binary_choice(prompt):
        #octave.keys = get_octave_keys()
        print("NEED TO IMPLEMENT")
    return octave


def make_volume():
    """Wrapper to let the user create a Volume"""
    return edit_volume(structures.Volume())


def edit_volume(volume):
    """Let the user edit an existing Volume"""
    prompt = "Enter a Volume Command."
    if volume.effect:
        prompt += " Currently it's %s." % volume.effect
    volume.effect = ui.get_choice(prompt, list("VPABCDEFGH")).lower()
    high = 64 if volume.effect in "vp" else 9
    if high == 9 and volume.valueRange[1] > 9:
        volume.valueRange[1] = 9
    if volume.valueRange[0] > volume.valueRange[1]:
        volume.valueRange[0] = volume.valueRange[1]
    volume.valueRange = ui.get_value_range(volume.valueRange, high, False)
    return volume


def make_effect():
    """Wrapper to let the user create an Effect"""
    return edit_effect(structures.Effect())


def edit_effect(effect):
    """Let the user create an Effect"""
    prompt = "Enter an Effect Type."
    if effect.effect:
        prompt += " Currently it's %s." % effect.effect
    types = list("#\ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    effect.effect = ui.get_choice(prompt, types)
    effect.valueRange = ui.get_value_range(effect.valueRange, 255, True)
    return effect


def make_offset():
    """Let the user create an Offset"""
    return edit_offset(structures.Offset())
    

def edit_offset(offset):
    """Let the user edit an existing Offset"""

    print("\nCurrently: %s" % offset.range_info())
    getSA = ui.get_binary_choice("Change Sample Areas? Y/N")
    getOV = ui.get_binary_choice("Change Offset Values? Y/N")
    msgs = ("Enter the %s Sample Area in hex.",
            "Enter the %s Offset Value in hex.")

    if getSA:
        offset.sampleArea[0] = ui.get_number(msgs[0] % "lowest", 0, 15, True)
    if getOV:
        offset.valueRange[0] = ui.get_number(msgs[1] % "lowest", 0, 255, True)

    if getSA:
        low = offset.sampleArea[0]
        if low == 15:
            print("You already entered the maximum value for a Sample Area, "
                    "so it's being set to %s automatically." % (
                        ui.convert_to_hex(low)))
            offset.sampleArea[1] = low
        else:
            offset.sampleArea[1] = ui.get_number(
                msgs[0] % "highest", low, 15, True)

    if getOV:
        if offset.sampleArea[0] == offset.sampleArea[1]:
            low = offset.valueRange[0]
            if low == 255:
                print("You already entered the maximum value for this Value "
                        "Range, so it's being set to %s automatically." % (
                            ui.convert_to_hex(low)))
                offset.valueRange[1] = low
            else:
                offset.valueRange[1] = ui.get_number(
                    msgs[1] % "highest", low, 255, True)
        else:
            offset.valueRange[1] = ui.get_number(
                msgs[1] % "highest", 0, 255, True)

    return offset