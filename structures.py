#!/usr/bin/python

"""Class objects defining aspects of a tracker production"""

from copy import deepcopy


def plural(value):
    """Get an "s" or "" depending on value"""
    return "s" if value != 1 else ""


class Channel(object):

    def __init__(self, instruments=[], volumes=[], effects=[],
                overwrite=False, muted=False):

        self.instruments = {"local": list(instruments), "useGlobal": False,
            "spacing": (0, 0), "curSpacing": 0}
        self.volumes = {"local": list(volumes), "useGlobal": False,
            "spacing": (0, 0), "curSpacing": 0}
        self.effects = {"local": list(effects), "useGlobal": False,
            "spacing": (0, 0), "curSpacing": 0}
        # stores a tuple of instrument data during production 
        self.nextInstrument = None
        # keeps track of changing the SA for Instrument Offsets
        self.currentSA = 0
        self.nextSA = 0
        self.overwrite = overwrite
        self.muted = muted

    def __str__(self):

        s = self.spacing
        numInst = len(self.instruments)
        info = "Uses %s Instrument%s" % (numInst, plural(numInst))
        if self.useGlobals[0]:
            info += " (G)"
        info += ", spaced %s-%s" % (s[0][0], s[0][1])
        numEffects = len(self.effects)
        info += ". Uses %s Effect%s" % (numEffects, plural(numEffects))
        if self.useGlobals[1]:
            info += " (G)"

        info += ", spaced %s-%s. Overwrite is " % (s[1][0], s[1][1])
        info += "on." if self.overwrite else "off."
        info += " Not in use." if self.muted else " In use."

        return info


class Instrument(object):

    def __init__(self, number=0, octaves=[], volumes=[], offsets=[]):
        self.number = number
        self.octaves = {"local": list(octaves), "useGlobal": False}
        self.volumes = {"local": list(volumes), "useGlobal": False}
        self.offsets = {"local": list(offsets), "useGlobal": False}
        self.useGlobals = list(useGlobals)
        self.usedBy = []

    def __str__(self):

        info = "Instrument #%s." % self.number

        numOctaves = len(self.octaves)
        info += " %s Octave%s" % (numOctaves, plural(numOctaves))
        if self.useGlobals[0]:
            info += " (G)"
        numVolumes = len(self.volumes)
        info += ". %s Volume%s" % (numVolumes, plural(numVolumes))
        if self.useGlobals[1]:
            info += " (G)"

        if self.offset is None:
            info += ". No Offset."
        else:
            info += ". Uses an Offset."
        if self.usedBy:
            n = len(self.usedBy)
            info += " Used by %s Channels%s." % (n, plural(n))
        else:
            info += " Not in use."

        return info


class Octave(object):

    def __init__(self, pitch=5,
                keys=["C-", "C#", "D-", "D#", "E-", "F-",
                    "F#", "G-", "G#", "A-", "A#", "B-"]):
        self.pitch = pitch
        self.keys = list(keys)
        self.usedBy = []

    def __str__(self):
        info = "Pitch %s. " % self.pitch
        # compares the current keys to the full default
        if self.keys == Octave.__init__.__defaults__[1]:
            info += "It uses the full octave."
        else:
            info += "It is limited to the %s keys." % (self.keys)
        if self.usedBy:
            n = len(self.usedBy)
            info += " Used by %s Instrument%s." % (n, plural(n))
        else:
            info += " Not in use."
        return info


class Effect(object):

    def __init__(self, effect="", valueRange=[0, 255]):
        self.effect = effect
        self.valueRange = list(valueRange)
        self.usedBy = []

    def __str__(self):

        vr = self.valueRange
        info = "Effect %s. " % self.effect
        vr = ("%X" % vr[0], "%X" % vr[1])
        if vr[0] == vr[1]:
            info += "The value is always %s." % vr[0]
        else:
            info += "The value range is %s to %s." % (vr[0], vr[1])
        if self.usedBy:
            n = len(self.usedBy)
            info += " Used by %s Channels%s." % (n, plural(n))
        else:
            info += " Not in use."

        return info


class Volume(Effect):

    def __init__(self, effect="", valueRange=[0, 64]):
        super(Volume, self).__init__(effect.lower(), valueRange)
        self.usedBy = {"Channels": [], "Instruments": []}

    def __str__(self):
        vr = self.valueRange
        info = "Volume Control %s. " % self.effect
        if vr[0] == vr[1]:
            info += "The value is always %s." % vr[0]
        else:
            info += "The value range is %s to %s." % (vr[0], vr[1])
        if self.usedBy:
            n = len(self.usedBy)
            info += " Used by %s Instrument%s." % (n, plural(n))
        else:
            info += " Not in use."
        return info


class Offset(Effect):

    def __init__(self, valueRange=[0, 255], sampleArea=[0, 0]):
        super(Offset, self).__init__("O", valueRange)
        self.sampleArea = list(sampleArea)

    def __str__(self):
        info = self.range_info()
        if self.usedBy:
            n = len(self.usedBy)
            info += " Used by %s Instrument%s." % (n, plural(n))
        else:
            info += " Not in use."
        return info

    def range_info(self):
        """Create a text representation of the offset values"""
        
        vr = []
        for value in self.valueRange:
            vr.append(("%X" % value).zfill(2))
        sa = self.sampleArea
        sa = ("%X" % sa[0], "%X" % sa[1])

        if sa[0] == sa[1]:
            info = "The Sample Area is always %s." % sa[0]
            if vr[0] == vr[1]:
                info += " The Offset Value is always %s." % vr[0]
            else:
                info += " The Offset range is %s to %s." % (vr[0], vr[1])
        else:
            info = " The Offset range is SA%s-O%02s to SA%s-O%02s." % (
                sa[0], vr[0], sa[1], vr[1])
        return info