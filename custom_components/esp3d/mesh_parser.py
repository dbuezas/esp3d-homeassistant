from typing import Dict

from enum import Enum, auto
import re


def is_number(s):
    # Regular expression to match integers and floating-point numbers
    # This pattern matches optional leading -, followed by digits,
    # optionally followed by a decimal point and more digits.
    pattern = r"^[+-]?\d+(\.\d+)?$"
    return re.match(pattern, s) is not None


class State(Enum):
    WAITING = auto()
    HEADER = auto()
    TABLE = auto()


# Bilinear Leveling Grid:
#       0      1      2      3      4
#  0 +0.032 +0.041 +0.038 +0.012 -0.004
#  1 +0.028 +0.026 +0.011 -0.012 -0.060
#  2 +0.031 +0.046 +0.031 -0.014 -0.076
#  3 +0.059 +0.054 +0.033 -0.019 -0.092
#  4 +0.104 +0.070 +0.049 -0.008 -0.081
# echo:Bed Leveling OFF
# echo:Fade Height 10.00
# ok P63 B15


class MeshParser:
    def __init__(self):
        self.state = State.WAITING
        self.z: list[list[float]] = []
        self.x: list[float] = []
        self.y: list[float] = []

    def parse(self, line: str) -> None | dict[str, list[float]]:
        if line == "Bilinear Leveling Grid:":
            self.__init__()
            self.state = State.HEADER
            return

        if self.state is State.HEADER:
            substrings = line.split()
            if all(sub.isdigit() for sub in substrings):
                self.state = State.TABLE
                self.x = [float(sub) for sub in substrings]
                return
            self.__init__()

        if self.state is State.TABLE:
            substrings = line.split()
            if all(is_number(sub) for sub in substrings):
                self.y.append(float(substrings[0]))
                numbers = [float(sub) for sub in substrings[1:]]
                self.z.append(numbers)
                return
            match = re.search(r"^ok(?:$|\s)", line)
            if match:
                mesh = {"x": self.x, "y": self.y, "z": self.z}
                self.__init__()
                return mesh
