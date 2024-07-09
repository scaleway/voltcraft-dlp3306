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

from fire.core import Fire
from typing import List, Union
from voltcraft_dlp3306 import get_default_voltcraft, CHANNEL_INDEXES


ALL_CHANNELS = -1


async def _display_ping():
    vlt = await get_default_voltcraft()
    print(await vlt.ping())


async def _display_current(channel: int):
    vlt = await get_default_voltcraft()

    if channel == ALL_CHANNELS:
        print(await vlt.get_running_current_all_chan())
    else:
        print(await vlt.get_running_current_chan(channel))


async def _display_voltage(channel: int):
    vlt = await get_default_voltcraft()

    if channel == ALL_CHANNELS:
        print(await vlt.get_running_voltage_all_chan())
    else:
        print(await vlt.get_running_voltage_chan(channel))


async def _turn_on(channel: int):
    vlt = await get_default_voltcraft()

    await vlt.turn_on_chan(channel)


async def _turn_off(channel: int):
    vlt = await get_default_voltcraft()

    await vlt.turn_off_chan(channel)


async def _watch(frequency: float, out: str, channels: list):
    vlt = await get_default_voltcraft()

    if channels == ALL_CHANNELS:
        channels = CHANNEL_INDEXES

    await vlt.watch(frequency=frequency, out=out, channels=channels)


class Main(object):
    def ping(self):
        asyncio.run(_display_ping())

    def current(self, channel: int = ALL_CHANNELS):
        asyncio.run(_display_current(channel))

    def voltage(self, channel: int = ALL_CHANNELS):
        asyncio.run(_display_voltage(channel))

    def on(self, channel: int):
        asyncio.run(_turn_on(channel))

    def off(self, channel: int):
        asyncio.run(_turn_off(channel))

    def watch(
        self,
        frequency: float = 1.0,
        out: str = None,
        channels: Union[List[int], int] = ALL_CHANNELS,
    ):
        asyncio.run(_watch(frequency, out, channels))


if __name__ == "__main__":
    Fire(Main)
