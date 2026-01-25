# Coffee Pot Monitor

A Home Assistant automation blueprint that monitors a coffee pot's power consumption and provides visual and audio feedback on the brewing status.

## Features

- **Three-State Monitoring**: Tracks brewing in three stages:
  - 🔵 **Brewing Started** - Power exceeds the start threshold (bright cool-white light)
  - 🟠 **Brewing in Progress** - Power within the in-progress window (dim amber light)
  - 🟢 **Brewing Finished** - Power drops below finish threshold (bright green light)

- **Push Notifications**: Sends notifications when brewing starts and when coffee is ready
- **Visual Indicators**: Uses a light entity to display the current brewing state with color and brightness changes
- **Optional Logging**: Conditionally writes entries to the Home Assistant Logbook based on a toggle
- **Fully Configurable**: All thresholds, entities, and services are customizable inputs

## Requirements

- A power sensor (e.g., a smart plug) that reports the coffee pot's power consumption in watts
- A light entity to act as a visual indicator
- A notification service (defaults to `notify.notify`)
- An input boolean to control optional logging

## Configuration

When creating an instance of this blueprint, you'll need to configure:

### Required Inputs
- **Power sensor**: The entity that reports power consumption (e.g., `sensor.coffee_pot_power`)
- **Indicator light**: A light to show the brewing status (e.g., `light.coffee_indicator`)

### Optional Inputs
- **Notification service**: Service to send push notifications (default: `notify.notify`)
- **Logging toggle**: Input boolean to enable/disable logbook entries (default: required)

### Thresholds (Watts)
- **Start threshold**: Power level that indicates brewing has started (default: 1000W)
- **Finish threshold**: Power level that indicates brewing is complete (default: 500W)
- **In-progress lower bound**: Lower bound of the brewing-in-progress window (default: 500W)
- **In-progress upper bound**: Upper bound of the brewing-in-progress window (default: 1000W)

## How It Works

The blueprint monitors your coffee pot's power consumption and triggers different actions based on power thresholds:

1. When power **exceeds the start threshold** → Light turns bright cool-white and a notification is sent
2. When power falls **between the in-progress bounds** → Light turns dim amber
3. When power **drops below the finish threshold** → Light turns bright green and a ready notification is sent

All transitions include optional logbook entries (if enabled) and a 2-second delay to avoid false triggers.

## Tips

- Adjust the thresholds to match your specific coffee pot's power profile
- Test with your coffee pot to find the optimal threshold values
- Use the logging toggle to keep your logbook clean or enable it for detailed tracking
- Consider setting the indicator light to a smart bulb that's visible from your workspace

## Automation Mode

This blueprint uses `restart` mode, meaning the latest power reading always takes precedence if multiple triggers occur simultaneously.
