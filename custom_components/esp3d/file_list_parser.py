from dataclasses import dataclass
from typing import Dict, Optional

from enum import Enum, auto
import re


class State(Enum):
    WAITING = auto()
    LISTING = auto()


# Begin file list
#   TES~1.GCO 277 test.gcode
#   CUBE_P~3.GCO 140739 Cube_PLA_2m24s.gcode
#   End file list
#   ok P63 B0


@dataclass
class FileDetail:
    short_name: str
    size: int
    long_name: Optional[str]


class FileListParser:
    def __init__(self):
        self.state = State.WAITING
        self.files: list[FileDetail] = []

    def parse(self, line: str) -> None | list[FileDetail]:
        if line == "echo:No media":
            self.__init__()
            return self.files
        if line == "Begin file list":
            self.__init__()
            self.state = State.LISTING
            return

        if self.state is State.LISTING:
            if line == "End file list":
                files = self.files
                self.__init__()
                return files
            match = re.search(r"^(.+?)\s+(\d+)(?:\s+(.+))?$", line)
            if match:
                short, size, long = match.groups()
                self.files.append(
                    FileDetail(
                        short_name=short.lower(),
                        size=int(size),
                        long_name=long,
                    )
                )
            else:
                self.__init__()
