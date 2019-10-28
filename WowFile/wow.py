#!`/usr/bin/whereis python3`
# -*- coding: iso-8859-9 -*-

import datetime
from PIL import Image
from . import __version__

# Ignore movement which are larger than this value for:
# - Layer thickness calculation
# - Movement time
# This is mainly to ignore the last movement made after the final layer
# which as the gcode is made would screw the thickness calculation on that
# layer. (There is nothing to know that the layer ended in that specific case)
# TODO: this need to be improved in a way. This is not completely reliable
_IgnoreMovementLargerThan = 15 # in mm


class layer:
    """Implement one layer of SLA with all linked parameters"""
    def __init__(self, number):
        self.thickness = 0
        self.exposition_time = 0
        self.move_time = 0
        self.number = number
        self.speed_up = 0
        self.speed_down = 0
        self.up_distance = 0
        self.down_distance = 0
        self.exposition = 0
        self.data = b""
        self.width = 0
        self.height = 0
        self.image = None
        self.illuminated_pixel = 0

    def set_image(self, data, size):
        self.width = size[0]
        self.height = size[1]
        self.image = Image.frombytes("1", size, data, "raw", "1;R")
        self.image = self.image.rotate(90, expand=True)
        self.data = data
        # TODO: Run that in the background
        self.illuminated_pixel = sum(_b2ba[int(b)] for b in data)

    def update_movetime(self):
        if self.speed_up > 0 or self.speed_down > 0:
            self.move_time = abs(self.up_distance) / (self.speed_up / 60)
            self.move_time += abs(self.up_distance - self.thickness) / (self.speed_down / 60)
        else:
            # Absurdely huge number to show that there is a problem
            # (movement set to 0 is not a wanted value)
            self.move_time = 9999999

    def get_packed_image(self):
        return self.data

    def set_exposition(self, value):
        self.exposition = value


def _nothing(code, cur_layer):
    """Stub for unused gcode command"""
    pass


def _g1(code, cur_layer):
    """Decode gcode G1 command"""
    distance = 0
    speed = 0

    for param in code:
        if param[0] == "Z" or param[0] == "z":
            distance = float(param[1:])
            if abs(distance) <= _IgnoreMovementLargerThan:

                if distance > 0:
                    cur_layer.up_distance = distance
                else:
                    cur_layer.down_distance = distance

                cur_layer.thickness += distance
                cur_layer.thickness = round(cur_layer.thickness, 5)
                if speed is not 0:
                    cur_layer.move_time += abs(distance) / (speed / 60)
                    if distance > 0:
                        cur_layer.speed_up = speed
                    else:
                        cur_layer.speed_down = speed

        elif param[0] == "F" or param[0] == "f":
            speed = float(param[1:])
            if distance is not 0:
                cur_layer.move_time += abs(distance) / (speed / 60)
                if distance > 0:
                    cur_layer.speed_up = speed
                else:
                    cur_layer.speed_down = speed


def _g4(code, cur_layer):
    """Decode gcode G4 command"""
    for param in code:
        if param[0] == "S" or param[0] == "s":
            value = float(param[1:])
            # Ending have a really long pause, don't change layer exposition if it is longer than 120 seconds
            if value <= 120:
                cur_layer.exposition_time += value


def _m106(code, cur_layer):
    """Decode gcode M106 command"""
    if cur_layer is not None:
        for param in code:
            if param[0] == "S" or param[0] == "s":
                value = float(param[1:])
                if value > 0:
                    cur_layer.set_exposition(value)


_b2ba = [bin(i).count("0") for i in range(0, 256)]


class WowFile:
    """"""
    _GCodes = {
        "G21": _nothing,   # Set unit to millimetre
        "G91": _nothing,   # Set positioning to relative
        "M17": _nothing,   # Set On/Off all steppers
        "M106": _m106,     # UV Backlight power
        "G28": _nothing,   # Move to origin (Homing)
        "M18": _nothing,   # Move to origin (Homing)
        "G1": _g1,         # Move
        "G4": _g4,         # Sleep
    }

    _Preamble = "G21;\n" \
        "G91;\n" \
        "M17;\n" \
        "M106 S0;\n" \
        "G28 Z0;\n" \
        ";W:{W};\n" \
        ";H:{H};\n"

    _Ending = "M106 S0;\n" \
        "G1 Z20.0;\n" \
        "G4 S300;\n" \
        "M18;"

    _LayerStart = ";L:{layer:d};\n" \
        "M106 S0;\n" \
        "G1 Z{up:,g} F{spdu:g};\n" \
        "G1 Z{down:,g} F{spdd:g};\n" \
        "{{{{\n"

    _LayerEnd = "\n" \
        "}}}}\n" \
        "M106 S{exp:g};\n" \
        "G4 S{wait:g};\n"

    _MaxBuildArea = (102, 56)  # in mm

    def _decode(self, code, cur_layer):
        splitcode = code.strip(";").split(" ")
        if code[0] == 'G' or code[0] == 'g' or code[0] == 'M' or code[0] == 'm':
            try:
                self._GCodes[splitcode[0]](splitcode, cur_layer)

            except KeyError:
                raise Exception("Not support gcode found: {code}".format(code=code))
        elif code[0] == ';':
            if code[1] == "H" or code[1] == "h":
                self.Height = int(code.strip(";").split(":")[1], 0)
            elif code[1] == "W" or code[1] == "w":
                self.Width = int(code.strip(";").split(":")[1], 0)
            elif code[1] == "L" or code[1] == "l":
                return layer(int(code.strip(";").split(":")[1], 0))
        else:
            raise Exception("Invalid gcode found: {code}".format(code=code))

        return None

    def __init__(self, file):
        f = open(file, "rb")
        self.layers = []
        EndOfFile = False
        cur_layer = None

        while not EndOfFile:
            # Read GCode header until we get to the picture ( {{ )
            while True:
                line = f.readline().decode("ASCII").strip("\n")
                if line == "":
                    EndOfFile = True
                    break

                if line[0:2] == "{{":
                    break
                new_layer = self._decode(line, cur_layer)

                if new_layer is not None:
                    if cur_layer is not None:
                        self.layers.append(cur_layer)
                    cur_layer = new_layer

            if not EndOfFile:
                data = f.read(int(self.Height*self.Width / 8))
                cur_layer.set_image(data, (self.Width, self.Height))
                # There is a newline at end of image data, and.. we don't care about it -> just discard it.
                f.readline()
                line = f.readline()
                if line != b"}}\n":
                    raise Exception("File is invalid, }} not found at end of frame")

            elif EndOfFile:
                # Don't forget to add the last layer!
                self.layers.append(cur_layer)

    def get_zheight(self):
        height = 0
        for l in self.layers:
            height = round(height + l.thickness, 5)
        return height

    def get_layer(self, layer_num):
        return self.layers[layer_num]

    def get_volume(self, human_readable=False):
        pixel_width = self._MaxBuildArea[0] / self.Height
        pixel_height = self._MaxBuildArea[1] / self.Width
        volume = 0
        for l in self.layers:
            volume += pixel_width * pixel_height * l.thickness * l.illuminated_pixel

        if human_readable:
            unit = ["mm³", "cm³", "m³", "dm³", "km³"]
            unit_idx = 0
            # Value is in mmÂ³
            while volume > 1000.:
                unit_idx += 1
                volume /= 1000.
            return "{vol} {unit}".format(vol=round(volume, 2), unit=unit[unit_idx])

        return volume

    def get_printtime(self, human_readable=False):
        exptime = 0
        for l in self.layers:
            exptime += l.exposition_time
            exptime += l.move_time
            exptime = round(exptime, 5)

        if human_readable:
            sec = round(exptime % 60, 0)
            mn = round(exptime // 60, 0)
            hour = round(mn // 60, 0)
            mn = round(mn % 60, 0)
            day = round(hour // 24, 0)
            hour = round(hour % 24, 0)
            out = ""
            if day > 0:
                out = " {d:g}d".format(d=day)
            if hour > 0:
                out = " {h:g}hr".format(h=hour)
            if mn > 0:
                out = out + " {m:g}min".format(m=mn)
            if sec > 0:
                out = out + " {s:g}s".format(s=sec)
            return out.lstrip()
        else:
            return exptime

    def get_layercount(self):
        return len(self.layers)

    def export_layer(self, layer_num, png_file):
        self.layers[layer_num].image.save(png_file, "PNG")

    def write_wow(self, filename):
        with open(filename, "wb") as f:
            # First write file preamble
            f.write(self._Preamble.format(H=self.Height, W=self.Width).encode("ascii"))

            for l in self.layers:
                # Write layer preamble
                f.write(self._LayerStart.format(layer=l.number,
                                                up=l.up_distance,
                                                down=round(l.thickness - l.up_distance, 5),
                                                spdu=l.speed_up,
                                                spdd=l.speed_down).encode("ascii"))
                # Write layer image
                f.write(l.get_packed_image())
                # Write layer ending
                f.write(self._LayerEnd.format(exp=l.exposition,
                                              wait=l.exposition_time).encode("ascii"))

            # Write ending
            f.write(self._Ending.encode("ascii"))


if __name__ == "__main__":
    print("WowFile v{ver}".format(ver=__version__))
    wN = WowFile("hollow_out_lcd_w.wow")
    print("Height in mm: {h}".format(h=wN.get_zheight()))
    print("Approx printing time: {exp}".format(exp=str(datetime.timedelta(seconds=wN.get_printtime()))))
    print("layer 1: {exp}".format(exp=wN.layers[1].exposition_time))
    print("layer 3: {exp}".format(exp=wN.layers[3].exposition_time))
    wN.export_layer(50, "test.png")
    #wN.write_wow("test.wow")