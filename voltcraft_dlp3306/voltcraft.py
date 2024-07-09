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

import time
import asyncio

from datetime import datetime
from typing import List, Tuple, Union, Optional
from scpi import SCPIDevice
from .tcp import TCPTransport
from .writer import Writer

MAX_VOLTAGE = 31.00
MAX_CURRENT = 6.10
CHANNEL_INDEXES = [1, 2, 3]
ON_STATE = 1
OFF_STATE = 0

DEFAULT_IP_ADDR = "192.168.1.99"
DEFAULT_PORT = 7890


async def get_default_voltcraft() -> "VoltcraftDLP3306":
    return await VoltcraftDLP3306.create_device()


class VoltcraftDLP3306(SCPIDevice):
    """
    Voltcraft Power supply related features
    Application of documentation from: https://asset.conrad.com/media10/add/160267/c1/-/en/002619140ML00/mode-demploi-2619140-alimentation-de-laboratoire-reglable-voltcraft-dlp-3306-0-30-v-0-6-a-378-w-rs-232-usb-lan-fonction-esclave-nbr-d.pdf
    """

    @property
    def channels():
        return CHANNEL_INDEXES

    async def ping(self) -> str:
        try:
            return await self.identify()
        except:
            return None

    async def get_running_current(
        self, chan: Optional[Union[int, List[int]]]
    ) -> Union[List[float], float]:
        if chan == None or sorted(list(chan)) == CHANNEL_INDEXES:
            return await self.get_running_current_all_chan()
        else:
            return [await self.get_running_current_chan(c) for c in list(chan)]

    async def get_running_voltage(
        self, chan: Optional[Union[int, List[int]]]
    ) -> Union[List[float], float]:
        if chan == None or sorted(list(chan)) == CHANNEL_INDEXES:
            return await self.get_running_voltage_all_chan()
        else:
            return [await self.get_running_voltage_chan(c) for c in list(chan)]

    async def get_running_current_all_chan(self) -> List[float]:
        meas = await self.ask("MEAS:CURR:ALL?")
        return list(map(float, meas.split(", ")))

    async def get_running_voltage_all_chan(self) -> List[float]:
        meas = await self.ask("MEAS:VOLT:ALL?")
        return list(map(float, meas.split(", ")))

    async def get_running_power_all_chan(self) -> List[float]:
        volt_meas = await self.get_running_voltage_all_chan()
        curr_meas = await self.get_running_current_all_chan()
        return [v * c for v, c in zip(volt_meas, curr_meas)]

    async def get_running_current_chan(self, chan: int) -> float:
        assert chan in CHANNEL_INDEXES

        await self.command(f"INST:NSEL {chan}")
        return float(await self.ask("MEAS:CURR?"))

    async def get_running_voltage_chan(self, chan: int) -> float:
        assert chan in CHANNEL_INDEXES

        await self.command(f"INST:NSEL {chan}")
        return float(await self.ask("MEAS:VOLT?"))

    async def get_setup_voltage_chan(self, chan: int) -> float:
        assert chan in CHANNEL_INDEXES

        await self.command(f"INST:NSEL {chan}")
        return float(await self.ask("VOLT?"))

    async def get_setup_current_chan(self, chan: int) -> float:
        assert chan in CHANNEL_INDEXES

        await self.command(f"INST:NSEL {chan}")
        return float(await self.ask("CURR?"))

    async def set_setup_current_chan(self, current: float, chan: int):
        assert chan in CHANNEL_INDEXES
        assert current > 0 and current <= MAX_CURRENT

        await self.command(f"INST:NSEL {chan}")
        await self.command(f"CURR {current}")

    async def set_setup_voltage_chan(self, voltage: float, chan: int):
        assert chan in CHANNEL_INDEXES
        assert voltage > 0 and voltage <= MAX_VOLTAGE

        await self.command(f"INST:NSEL {chan}")
        await self.command(f"VOLT {voltage}")

    async def set_limit_voltage_chan(self, voltage: float, chan: int):
        assert chan in CHANNEL_INDEXES
        assert voltage > 0 and voltage <= MAX_VOLTAGE

        await self.command(f"INST:NSEL {chan}")
        await self.command(f"VOLT:LIM {voltage}")

    async def set_limit_current_chan(self, current: float, chan: int):
        assert chan in CHANNEL_INDEXES
        assert current > 0 and current <= MAX_CURRENT

        await self.command(f"INST:NSEL {chan}")
        await self.command(f"CURR:LIM {current}")

    async def get_limit_voltage_chan(self, chan: int):
        assert chan in CHANNEL_INDEXES

        await self.command(f"INST:NSEL {chan}")
        return float(await self.ask("VOLT:LIM?"))

    async def get_limit_current_chan(self, chan: int):
        assert chan in CHANNEL_INDEXES

        await self.command(f"INST:NSEL {chan}")
        return float(await self.ask("CURR:LIM?"))

    async def set_state_chan(self, state: int, chan: int):
        assert chan in CHANNEL_INDEXES
        assert state in [OFF_STATE, ON_STATE]

        all_states = await self.ask("CHAN:OUTP:ALL?")
        all_states = list(map(str, all_states.split(", ")))
        all_states[chan - 1] = str(state)
        all_states = ",".join(all_states)

        await self.command(f"CHAN:OUTP:ALL {all_states}")

    async def turn_on_chan(self, chan: int):
        await self.set_state_chan(ON_STATE, chan)

    async def turn_off_chan(self, chan: int):
        await self.set_state_chan(OFF_STATE, chan)

    async def watch(
        self,
        channels: List[int],
        frequency: float = 1,
        out: Optional[str] = None,
        should_continue_cb: Optional[callable] = None,
    ):
        assert frequency > 0

        if isinstance(channels, Tuple):
            channels = list(channels)

        if not isinstance(channels, List):
            channels = [channels]

        writer = Writer.get_writer_from_extension(out)

        def should_continue():
            if should_continue_cb:
                return should_continue_cb()
            return True

        try:
            titles_row = ["TIME", "DELTA_TIME"]
            for c in channels:
                titles_row.append(f"CHAN_{c}_VOLTAGE")
                titles_row.append(f"CHAN_{c}_CURRENT")

            writer.write(*titles_row)
            start_time = time.time()

            while should_continue():
                delta_time = time.time() - start_time
                now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                voltages = dict(zip(channels, await self.get_running_voltage(channels)))
                currents = dict(zip(channels, await self.get_running_current(channels)))

                row = [now, delta_time]
                for c in channels:
                    row.append(voltages[c])
                    row.append(currents[c])

                writer.write(*row)

                await asyncio.sleep(frequency)
        finally:
            writer.close()

    @classmethod
    async def create_device(
        cls, ip: str = DEFAULT_IP_ADDR, port: int = DEFAULT_PORT
    ) -> "VoltcraftDLP3306":
        connection = TCPTransport()
        await connection.open_connection(ipaddr=ip, port=port)

        device = VoltcraftDLP3306(instancefrom=connection, use_safe_variants=False)

        return device
