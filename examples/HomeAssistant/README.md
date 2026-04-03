# Home Assistant API Integration
Home Assistant is an open-source home automation platform that allows you to control and automate smart devices from a single interface. For more details, visit: https://www.home-assistant.io/

SMARTWIZ+ art uses the Home Assistant API to display camera images, today’s weather forecast, and calendar events.
This folder provides sample implementations for displaying information via the API.

## Prerequisites
The sample scripts use an environment variable called ART_SDK_ROOT to reference the key files and the SMARTWIZ+ art library (epd_util.py).

From the examples directory, please run:
```bash
# Set ART_SDK_ROOT to the path of the `examples` directory
. ./export.sh
```

In addition, to call the Home Assistant API, you need to set a Long-Lived Access Token generated in Home Assistant as an environment variable named HA_ACCESS_TOKEN:
```bash
# Set HA_ACCESS_TOKEN to your Home Assistant Long-Lived Access Token
export HA_ACCESS_TOKEN=<Your Long-Lived Access Token>
```
