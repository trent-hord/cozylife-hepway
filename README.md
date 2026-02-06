# CozyLife Battery Home Assistant Integration

This is a custom integration for Home Assistant to control and monitor CozyLife / Hepway portable batteries.

## Features

- **AC Power Switch**: Turn the AC output on and off.
- **Battery Level Sensor**: Monitor the battery charge percentage.
- **Output Watts Sensor**: Monitor the current power output.
- **Incoming Watts Sensor**: Monitor incoming power (charging).
- **Minutes Remaining Sensor**: Estimate the remaining battery life.

## Installation

### Option 1: HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. Go to **HACS** > **Integrations**.
3. Click the **three dots** in the top right corner and select **Custom repositories**.
4. In the **Repository** field, enter the URL of this repository.
5. In the **Category** dropdown, select **Integration**.
6. Click **Add**.
7. Close the modal, find "CozyLife Battery" in the list, and install it.
8. Restart Home Assistant.

### Option 2: Manual Installation

1. Copy the `custom_components/cozylife_battery` directory to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration

1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **CozyLife Battery**.
4. Enter the **IP Address** (Host) of your battery device.
5. Click **Submit**.

## Usage

Once configured, the following entities will be available:

- `switch.cozylife_battery_ac_power`: Controls the AC power outlet.
- `sensor.cozylife_battery_battery_level`: Shows the battery charge percentage.
- `sensor.cozylife_battery_output_watts`: Shows the current output in Watts.
- `sensor.cozylife_battery_incoming_watts`: Shows the incoming power in Watts (charging).
- `sensor.cozylife_battery_minutes_remaining`: Shows the estimated runtime in minutes.

## Troubleshooting

If the device does not connect, ensure that:
- The IP address is correct and static (recommended).
- The device is on the same network as Home Assistant.
