from typing import Dict

# https://gist.github.com/marc-x-andre/1c55b3fafd1d00cfdaa205ec53a08cf3

from enum import Enum, auto


class Event(Enum):
    OK = auto()
    PLANNER_BUFFER = auto()
    BLOCK_BUFFER = auto()
    X = auto()
    Y = auto()
    Z = auto()
    E = auto()
    NOZZLE_CURRENT = auto()
    NOZZLE_TARGET = auto()
    BED_CURRENT = auto()
    BED_TARGET = auto()
    CURRENT_BYTE = auto()
    TOTAL_BYTES = auto()
    FIRMWARE_NAME = auto()
    SOURCE_CODE_URL = auto()
    PROTOCOL_VERSION = auto()
    MACHINE_TYPE = auto()
    EXTRUDER_COUNT = auto()
    UUID = auto()
    CONNECTION_STATUS = auto()
    IS_BUSY = auto()
    MESH = auto()
    FILE_LIST = auto()
    SDCARD_INSERTED = auto()
    SDCARD_REMOVED = auto()
    FILE_OPENED = auto()
    IS_PRINTING = auto()
    NOTIFICATION = auto()
    ANY = auto()


class EventEmitter:
    def __init__(self):
        self.__events = {}

    def on(self, event_name: Event, handler):
        if event_name not in self.__events:
            self.__events[event_name] = []
        self.__events[event_name].append(handler)

    def off(self, event_name: Event, handler):
        if event_name in self.__events:
            try:
                self.__events[event_name].remove(handler)
                if not self.__events[event_name]:
                    del self.__events[event_name]
            except ValueError:
                pass

    def emit(self, event_name: Event, *args, **kwargs):
        for handler in self.__events.get(event_name, []):
            handler(*args, **kwargs)
