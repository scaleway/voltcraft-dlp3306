# Python package for Voltcraft DLP 3306 powersupply

**voltcraft_dlp3306** is a Python package to interact with Volcrat powersupply with respect [to its SCPI protocol implementation](https://asset.conrad.com/media10/add/160267/c1/-/en/002619140ML00/mode-demploi-2619140-alimentation-de-laboratoire-reglable-voltcraft-dlp-3306-0-30-v-0-6-a-378-w-rs-232-usb-lan-fonction-esclave-nbr-d.pdf)

## Installation

We encourage installing this package via the pip tool (a Python package manager):

```bash
pip install voltcraft-dlp3306
```

Physically plug an RJ45 cable to the Volcraft device and a switch or directly to your laptop.

![](docs/voltcraft_1.jpg)

The IP address and the port of your Voltcraft device can be found/setup at: 'Utility' button > 'Port set' tab > 'LAN set' subtab

## Getting started

This plugin is designed to be *straightforward and stateless*. Some improvements/optimizations could be done with a stateful object.

```python
import asyncio
from voltcraft_dlp3306 import VoltcraftDLP3306

async def main_async():
    # Device ip and port can be found directly on the powersupply option
    vlc = await VoltcraftDLP3306.create_device(ip="42.42.42.42", port="1234")

    # Set max delivered current (Ampere) at channel 1
    await vlc.set_setup_current_chan(4, 1)

    # Set delivered voltage (Volt) at channel 1
    await vlc.set_setup_voltage_chan(15, 1)

    # Switch on channel 1
    await vlc.turn_on_chan(1)

    # Print actual develired current (Ampere) at channel 1
    print(await vlc.get_running_current_chan(1))

    # Record channels values (voltage and current) to a csv file
    # You can provide a callback to stop the record at anytime
    await vlc.watch(frequency=0.2, out="measure.csv", channels=[1,2,3])

    # Turn off channel 1
    await vlc.turn_off_chan(1)

if __name__ == "__main__":
    # Package API must be used with asyncio
    asyncio.run(main_async())

```

Vocabulary explained:

![](docs/voltcraft_2.jpg)

## Development
This repository is at its early stage and is still in active development. If you are looking for a way to contribute please read [CONTRIBUTING.md](CONTRIBUTING.md).

## Reach us
We love feedback. Feel free to reach us on [Scaleway Slack community](https://slack.scaleway.com/), we are waiting for you on [#opensource](https://scaleway-community.slack.com/app_redirect?channel=opensource)..

## License
[License Apache 2.0](LICENSE)
