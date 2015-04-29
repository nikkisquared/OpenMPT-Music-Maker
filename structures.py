#!/usr/bin/env python

"""Class objects defining aspects of a tracker production"""


def plural(value):
    """Get an "s" or "" depending on value"""
    return "s" if value != 1 else ""


class Channel(object):

    def __init__(self, instruments=[], volumes=[], effects=[],
                overwrite=True, muted=False):

        self.instruments = {"local": list(instruments), "useGlobals": False,
            "spacing": (0, 0), "curSpacing": 0}
        self.volumes = {"local": list(volumes), "useGlobals": False,
            "spacing": (0, 0), "curSpacing": 0}
        self.effects = {"local": list(effects), "useGlobals": False,
            "spacing": (0, 0), "curSpacing": 0}
        self.overwrite = overwrite
        self.muted = muted
        self.reset()

    def reset(self):
        """Reset a Channel for production"""
        for local in (self.instruments, self.volumes, self.effects):
            local["curSpacing"] = 0
        # stores a tuple of instrument data during production 
        self.nextInstrument = None
        # keeps track of changing the SA for Instrument Offsets
        self.currentSA = 0
        self.nextSA = 0

    def __str__(self):

        n = len(self.instruments["local"])
        info = "Uses %s Instrument%s%s " % (n, plural(n),
            " (G)" * self.instruments["useGlobals"])
        info += "at %s-%s, " % self.instruments["spacing"]
        n = len(self.volumes["local"])
        info += "%s Volume%s%s " % (n, plural(n),
            " (G)" * self.volumes["useGlobals"])
        info += "at %s-%s, " % self.volumes["spacing"]
        n = len(self.effects["local"])
        info += "and %s Effect%s%s " % (n, plural(n),
            " (G)" * self.effects["useGlobals"])
        info += "at %s-%s. " % self.effects["spacing"]

        info += "Overwriting. " if self.overwrite else "Preserving. "
        info += "Muted." if self.muted else "In use."

        return info


class Instrument(object):

    def __init__(self, number=0, octaves=[], volumes=[], offsets=[]):
        self.number = number
        self.octaves = {"local": list(octaves), "useGlobals": False}
        self.volumes = {"local": list(volumes), "useGlobals": False}
        self.offsets = {"local": list(offsets), "useGlobals": False}
        self.usedBy = []

    def __str__(self):

        info = "Instrument #%s. " % self.number

        n = len(self.octaves["local"])
        info += "Uses %s Octave%s%s, " % (n, plural(n),
            " (G)" * self.octaves["useGlobals"])
        n = len(self.volumes["local"])
        info += "%s Volume%s%s, " % (n, plural(n),
            " (G)" * self.volumes["useGlobals"])
        n = len(self.offsets["local"])
        info += "and %s Offset%s%s. " % (n, plural(n),
            " (G)" * self.offsets["useGlobals"])

        if self.usedBy:
            n = len(self.usedBy)
            info += "Used by %s Channel%s." % (n, plural(n))
        else:
            info += "Not in use."

        return info


class Octave(object):

    defaultPitches = ["C-", "C#", "D-", "D#", "E-", "F-",
                    "F#", "G-", "G#", "A-", "A#", "B-"]

    def __init__(self, number=5, pitches=defaultPitches):
        self.number = number
        self.pitches = list(pitches)
        self.usedBy = []

    def __str__(self):
        info = "Pitch %s. " % self.number
        # compares the current keys to the full default
        if self.pitches == self.defaultPitches:
            info += "It uses the full octave."
        else:
            info += "It is limited to the %s pitches." % (self.pitches)
        if self.usedBy:
            n = len(self.usedBy)
            info += " Used by %s Instrument%s." % (n, plural(n))
        else:
            info += " Not in use."
        return info


class Effect(object):

    def __init__(self, effect="", valueRange=(0, 255)):
        self.effect = effect
        self.valueRange = valueRange
        self.usedBy = []

    def __str__(self):

        vr = self.valueRange
        info = "Effect %s. " % self.effect
        vr = ("%X" % vr[0], "%X" % vr[1])
        if vr[0] == vr[1]:
            info += "The value is always %s. " % vr[0]
        else:
            info += "The value range is %s to %s. " % (vr[0], vr[1])
        if self.usedBy:
            n = len(self.usedBy)
            info += "Used by %s Channel%s." % (n, plural(n))
        else:
            info += "Not in use."

        return info


class Volume(Effect):

    def __init__(self, effect="", valueRange=(0, 64)):
        super(Volume, self).__init__(effect.lower(), valueRange)
        self.usedBy = {"Channels": [], "Instruments": []}

    def __str__(self):

        info = "Volume Control %s. " % self.effect
        vr = self.valueRange
        if vr[0] == vr[1]:
            info += "The value is always %s. " % vr[0]
        else:
            info += "The value range is %s to %s. " % (vr[0], vr[1])

        n = len(self.usedBy["Channels"])
        info += "Used by %s Channel%s, " % (n, plural(n))
        n = len(self.usedBy["Instruments"])
        info += "and %s Instrument%s." % (n, plural(n))

        return info


class Offset(Effect):

    def __init__(self, valueRange=(0, 255), sampleArea=(0, 0)):
        super(Offset, self).__init__("O", valueRange)
        self.sampleArea = sampleArea

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
            info = "The Sample Area is always %s. " % sa[0]
            if vr[0] == vr[1]:
                info += "The Offset Value is always %s." % vr[0]
            else:
                info += "The Offset range is %s to %s." % (vr[0], vr[1])
        else:
            info = "The Offset range is SA%s-O%02s to SA%s-O%02s." % (
                sa[0], vr[0], sa[1], vr[1])
        return info