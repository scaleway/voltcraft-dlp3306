# Copyright 2024 Scaleway
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import logging

from typing import Optional
from dataclasses import dataclass, field
from scpi.transports.baseclass import BaseTransport


LOGGER = logging.getLogger(__name__)


@dataclass
class TCPTransport(BaseTransport):
    ipaddr: Optional[str] = field(default=None)
    port: Optional[int] = field(default=None)
    reader: Optional[asyncio.StreamReader] = field(default=None)
    writer: Optional[asyncio.StreamWriter] = field(default=None)

    async def open_connection(self, ipaddr: str, port: int) -> None:
        self.reader, self.writer = await asyncio.open_connection(ipaddr, port)
        self.ipaddr = ipaddr
        self.port = port

    async def send_command(self, command: str) -> None:
        if not self.writer:
            raise RuntimeError("Writer not set")
        async with self.lock:
            LOGGER.debug("sending command: {}".format(command))
            self.writer.write((command + "\r\n").encode())
            await asyncio.sleep(0.05)
            await self.writer.drain()

    async def get_response(self) -> str:
        if not self.reader:
            raise RuntimeError("Reader not set")
        async with self.lock:
            data = await self.reader.readline()
            res = data.decode()
            LOGGER.debug("Got response: {}".format(res.strip()))
            return res

    async def quit(self) -> None:
        if not self.writer:
            raise RuntimeError("Writer not set")
        self.writer.close()
        await self.writer.wait_closed()

    async def abort_command(self) -> None:
        LOGGER.debug("TCP transport does not know what to do here")
