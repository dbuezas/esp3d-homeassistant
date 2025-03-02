"""Common code for TCP component."""

from __future__ import annotations
import asyncio
from datetime import datetime

from .file_list_parser import FileListParser
from .mesh_parser import MeshParser
from .event_emitter import EventEmitter, Event

import logging
import re
from typing import Final


from homeassistant.core import HomeAssistant

_LOGGER: Final = logging.getLogger(__name__)


class Esp3d:
    """Base entity class for TCP platform."""

    def __init__(self, hass: HomeAssistant, name: str, host: str, port=23) -> None:
        """Set all the config values if they exist and get initial state."""

        self._hass = hass
        self.name = name
        self._host = host
        self._port = port
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.killed = False
        self.event_emitter = EventEmitter()
        self.mesh_parser = MeshParser()
        self.file_list_parser = FileListParser()

    async def _async_continuous_read(self):
        while not self.killed:
            if self.reader is None:
                break
            text = await self.reader.readline()
            if text is None or len(text) == 0:
                break
            text = text.decode("utf-8")
            # M420 V uses a \r instead of \n before the ok
            lines = re.split(r"\r|\n", text)
            for line in lines:
                if len(line) == 0:
                    continue
                _LOGGER.debug(f"Received: {line}")
                self.event_emitter.emit(Event.ANY, line)
                self.parse_temperature(line)
                self.parse_ok(line)
                self.parse_pos(line)
                self.parse_SD_status(line)
                self.parse_firmware_info(line)
                self.parse_is_busy(line)
                self.parse_mesh(line)
                self.parse_file_list(line)
                self.parse_file_opened(line)
                self.parse_sd_card_event(line)
                self.parse_notification(line)
                self.event_emitter.emit(Event.CONNECTION_STATUS, True)

    async def async_keep_alive(self):
        last_received = datetime.now()

        def update_last_received(_):
            nonlocal last_received
            last_received = datetime.now()

        self.event_emitter.on(Event.ANY, update_last_received)

        while not self.killed:
            if (datetime.now() - last_received).total_seconds() >= 30:
                try:
                    self.writer.write(("M105" + "\r").encode())
                    await self.writer.drain()
                except:
                    self.reader, self.writer = (None, None)

            wait_time = max(0, 30 - (datetime.now() - last_received).total_seconds())
            await asyncio.sleep(wait_time)

    async def async_monitor_connection(self):
        while not self.killed:
            try:
                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(self._host, self._port), timeout=5
                )
                self.event_emitter.emit(Event.CONNECTION_STATUS, True)
                # self.writer.write(("M115\r").encode())  # fetch uuid
                # await self.writer.drain()
                await self._async_continuous_read()
            except:
                self.reader, self.writer = (None, None)
                _LOGGER.warn("Unable to connect. Will retry...")
            self.event_emitter.emit(Event.CONNECTION_STATUS, False)
            await asyncio.sleep(2)

    async def async_kill(self):
        self.killed = True
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def async_send(self, gcode: str):
        if self.writer is None or self.killed:
            raise ConnectionError()
        try:
            self.writer.write((gcode + "\r").encode())
            await self.writer.drain()
            _LOGGER.debug(f"sent: {gcode}")
        except:
            self.writer.close()
            raise
        responses = []
        stop_event = asyncio.Event()

        def stop_waiting():
            stop_event.set()

        def append_response(line):
            if not stop_event.is_set():
                responses.append(line)

        self.event_emitter.on(Event.ANY, append_response)
        self.event_emitter.on(Event.OK, stop_waiting)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=5)
        except asyncio.TimeoutError:
            if len(responses) == 0:
                self.event_emitter.emit(Event.CONNECTION_STATUS, False)
            raise
        finally:
            self.event_emitter.off(Event.OK, stop_waiting)
            self.event_emitter.off(Event.ANY, append_response)

        return "\n".join(responses)

    def parse_ok(self, input_string: str):
        pattern = r"^ok P(\d+) B(\d+)$"
        match = re.search(pattern, input_string)
        if match:
            planner_buffer, block_buffer = match.groups()
            self.event_emitter.emit(Event.PLANNER_BUFFER, planner_buffer)
            self.event_emitter.emit(Event.BLOCK_BUFFER, block_buffer)
            self.event_emitter.emit(Event.OK)
            return
        pattern = r"^ok(?:$|\s)"
        match = re.search(pattern, input_string)
        if match:
            self.event_emitter.emit(Event.OK)

    def parse_pos(self, input_string: str):
        pattern = r"X:(-?\d+\.?\d*) Y:(-?\d+\.?\d*) Z:(-?\d+\.?\d*) E:(-?\d+\.?\d*)"
        # X:46.77 Y:210.00 Z:14.50 E:1.93 Count X:7483 Y:31500 Z:5800
        match = re.search(pattern, input_string)
        if match:
            x, y, z, e = match.groups()
            self.event_emitter.emit(Event.X, x)
            self.event_emitter.emit(Event.Y, y)
            self.event_emitter.emit(Event.Z, z)
            self.event_emitter.emit(Event.E, e)

    def parse_temperature(self, input_string: str):
        pattern = r"T:(\d+\.?\d*) /(\d+\.?\d*) B:(\d+\.?\d*) /(\d+\.?\d*)"
        match = re.search(pattern, input_string)
        if match:
            nozzle_current, nozzle_target, bed_current, bed_target = match.groups()

            self.event_emitter.emit(Event.NOZZLE_CURRENT, nozzle_current)
            self.event_emitter.emit(Event.NOZZLE_TARGET, nozzle_target)
            self.event_emitter.emit(Event.BED_CURRENT, bed_current)
            self.event_emitter.emit(Event.BED_TARGET, bed_target)

    def parse_SD_status(self, input_string: str):
        # Not SD printing
        # SD printing byte 123/12345
        pattern = r"SD printing byte (\d+)/(\d+)"
        match = re.search(pattern, input_string)
        if match:
            current_byte, total_bytes = match.groups()
            self.event_emitter.emit(Event.CURRENT_BYTE, int(current_byte))
            self.event_emitter.emit(Event.TOTAL_BYTES, int(total_bytes))
            self.event_emitter.emit(Event.IS_PRINTING, int(current_byte) > 0)

        pattern = r"Not SD printing"
        match = re.search(pattern, input_string)
        if match:
            self.event_emitter.emit(Event.CURRENT_BYTE, None)
            self.event_emitter.emit(Event.TOTAL_BYTES, None)
            self.event_emitter.emit(Event.IS_PRINTING, False)

        # If the input string does not match the expected format, return None
        return None

    def parse_firmware_info(self, input_string: str):
        pattern = r"FIRMWARE_NAME:(.*?) SOURCE_CODE_URL:(.*?) PROTOCOL_VERSION:(.*?) MACHINE_TYPE:(.*?) EXTRUDER_COUNT:(\d+) UUID:(.*)"
        match = re.search(pattern, input_string)
        if match:
            (
                firmware_name,
                source_code_url,
                protocol_version,
                machine_type,
                extruder_count,
                uuid,
            ) = match.groups()

            self.event_emitter.emit(Event.FIRMWARE_NAME, firmware_name)
            self.event_emitter.emit(Event.SOURCE_CODE_URL, source_code_url)
            self.event_emitter.emit(Event.PROTOCOL_VERSION, protocol_version)
            self.event_emitter.emit(Event.MACHINE_TYPE, machine_type)
            self.event_emitter.emit(Event.EXTRUDER_COUNT, int(extruder_count))
            self.event_emitter.emit(Event.UUID, uuid)

    def parse_is_busy(self, input_string: str):
        pattern = r"busy: processing"
        match = re.search(pattern, input_string)
        self.event_emitter.emit(Event.IS_BUSY, match != None)

    def parse_mesh(self, input_string: str):
        table = self.mesh_parser.parse(input_string)
        if table is not None:
            self.event_emitter.emit(Event.MESH, table)

    def parse_file_list(self, input_string: str):
        file_list = self.file_list_parser.parse(input_string)
        if file_list is not None:
            self.event_emitter.emit(Event.FILE_LIST, file_list)

    def parse_file_opened(self, input_string: str):
        match = re.search(r"^File opened: (.+) Size: (\d+)$", input_string)
        if match:
            (filename, size) = match.groups()
            self.event_emitter.emit(Event.FILE_OPENED, filename.lower(), int(size))

    def parse_sd_card_event(self, input_string: str):
        if re.search(r"SD card ok$", input_string):
            self.event_emitter.emit(Event.SDCARD_INSERTED)
        if re.search(r"No media$", input_string):
            self.event_emitter.emit(Event.SDCARD_REMOVED)

    def parse_notification(self, input_string: str):
        match = re.search(r"^//action:notification (.*)$", input_string)
        if match:
            (value,) = match.groups()
            self.event_emitter.emit(Event.NOTIFICATION, value)
