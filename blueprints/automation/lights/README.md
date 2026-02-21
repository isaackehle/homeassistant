# Lights Controller Blueprint

A comprehensive Home Assistant automation blueprint for controlling lights based on door sensors, motion detection, and button inputs with advanced features like motion bypass and timer-based auto-off.

## Features

- **Motion-Activated Lighting**: Automatically turns on lights when motion is detected, with configurable timer for auto-off
- **Door Sensor Integration**: Special handling for door open/close events to manage lighting behavior
- **Multi-Paddle Button Support**: Control lights with top and bottom paddle buttons supporting single and double-tap actions
- **Bypass Helper**: Optional toggle to temporarily disable automatic light turn-off (useful for manual control periods)
- **Multiple Light Types**: Support for toggle lights, dimmers, RGBW lights (color + brightness), and RGB-only lights
- **Advanced Debugging**: Detailed logbook entries for troubleshooting automation behavior
- **Flexible Configuration**: Highly customizable with optional sensors and flexible entity grouping

## Installation

1. Copy `lights_controller.yaml` to your Home Assistant blueprints directory
2. In Home Assistant, go to **Settings > Automations & Scenes > Create Automation > Create from Blueprint**
3. Select "Lights Controller" blueprint
4. Configure the required and optional inputs (see Configuration section below)

## Configuration

### Required Inputs

| Input              | Description                                                                               |
| ------------------ | ----------------------------------------------------------------------------------------- |
| **Door Sensors**   | Binary sensors that detect when doors open/close (e.g., `binary_sensor.living_room_door`) |
| **Timer Entity**   | A timer entity that controls the auto-off delay (e.g., `timer.lights_timer`)              |
| **Motion Sensors** | Motion detectors to trigger automatic lighting (e.g., `binary_sensor.motion_living_room`) |

### Optional Light Entity Groups

Configure which lights should be controlled. Leave empty to skip:

- **Toggle Lights**: Simple on/off lights (no brightness control)
- **Dimmer Lights**: Dimmable lights (brightness 0-100%)
- **RGBW Lights**: Color + brightness lights with white channel support
- **RGB Lights**: Color + brightness lights without white channel

### Button Configuration

- **Top Paddle Events**: Entity that provides top button events (single/double tap)
- **Bottom Paddle Events**: Entity that provides bottom button events (single/double tap)

### Advanced Options

#### Timer Reset Duration

Default: `00:20:00` (20 minutes)

How long the timer stays active after each motion detection or door trigger.

#### Bypass Helper

Default: Empty (disabled)

Optional boolean helper entity to temporarily disable automatic light turn-off:

- When ON: Lights won't turn off when timer expires (must be manually controlled)
- When OFF: Normal automatic turn-off behavior resumes

**Note**: Double-tap events and sensor-action changes toggle this helper automatically when configured.

#### Bypass Action Sensors

Default: Empty (disabled)

Event sensors that trigger bypass logic through button interactions:

- `"single"` state: Enable bypass (prevent auto-off)
- `"double"` state: Disable bypass (allow auto-off)

## Automation Behavior

### Door Opened

- Resets timer to configured duration
- Turns on all configured light entities at full brightness (dimmers) or full color (RGB/RGBW)

### Door Closed

- Starts or restarts the timer
- If motion is detected, timer runs for full duration
- If no motion, waits for motion to trigger lights

### Motion Detected

- Resets timer to configured duration
- Turns on lights if not already on
- If timer expires while motion is still present, resets timer for 5 more minutes

### Timer Expires (Auto-Off)

The automation intelligently handles light turn-off:

1. **Motion Still Detected**: Resets timer for 5 minutes (lights stay on)
2. **No Motion + Bypass OFF**: Turns off all configured lights
3. **Bypass ON**: Does nothing (lights stay as-is, manual control only)

Detailed logbook entries are created for each decision to aid troubleshooting.

### Button Controls

**Top Paddle:**

- Single tap: Custom action (configured per implementation)
- Double tap: Custom action (configured per implementation)

**Bottom Paddle:**

- Single tap: Custom action (configured per implementation)
- Double tap: Custom action (configured per implementation)

## Troubleshooting

### Lights Turn Off Unexpectedly

- Check the **logbook** when the timer expires to see why lights turned off
- Verify motion sensors are reporting correct state
- Confirm bypass helper is OFF if you want automatic control

### Lights Won't Turn Off

- Check if **bypass helper is enabled** (ON state)
- Verify motion sensors in the **Lights Controller** logbook messages
- Ensure timer entity exists and is configured correctly

### Button Actions Not Working

- Verify button event entities are correctly configured
- Check that the entity IDs match your actual button/remote event entities
- Confirm events are sending `KeyPressed` (single) or `KeyPressed2x` (double) values

### Motion Not Triggering Lights

- Check motion sensor configuration and entity IDs
- Verify sensors are not in "unavailable" state
- Confirm door sensors are in correct state (might be preventing motion triggers)

## Tips & Best Practices

1. **Create a Template Helper for Bypass**: Use a toggle helper entity for the bypass function—easier to manage than direct automation calls
2. **Test Motion Sensors First**: Verify sensors work independently before relying on them in this automation
3. **Use Descriptive Timer Names**: Name your timer entity clearly (e.g., `timer.living_room_lights`)
4. **Check Logbook Regularly**: Monitor logbook entries when debugging to understand automation decisions
5. **Set Reasonable Timers**: 15-30 minutes is typical; shorter times may turn lights off too quickly, longer times waste energy

## Example Use Cases

### Living Room Motion-Activated Lighting

- Door sensor on living room entrance
- Motion detector in room
- Lights turn on for 20 minutes after motion detected
- Lights auto-off when motion stops for 20 minutes
- Bypass helper prevents unwanted turn-off during TV watching

### Hallway Smart Lighting

- Multiple door sensors (room entrances)
- Hall motion detector
- Fast timer (5 minutes) for energy efficiency
- Button control for manual overrides

### Kitchen with Button Control

- Motion sensors for automatic operation during cooking
- Button paddles for quick on/off and special modes
- Different light groups (overhead, under-cabinet, accent)
- Bypass for when cooking extends beyond motion detection time

## Entity Requirements

Before creating an automation from this blueprint, ensure you have:

1. ✅ At least one **binary sensor** for doors (entity_id: `binary_sensor.*`)
2. ✅ At least one **timer** entity (entity_id: `timer.*`)
3. ✅ At least one **motion sensor** (entity_id: `binary_sensor.*`)
4. ✅ One or more **light entities** to control (entity_id: `light.*`)
5. ⚠️ (Optional) A **boolean helper** for bypass control (entity_id: `input_boolean.*`)
6. ⚠️ (Optional) **Event sensors** for button/remote control (entity_id: `event.*`)

## Support & Customization

This blueprint provides a solid foundation for motion-activated lighting. For custom scenarios:

- Duplicate and modify the blueprint file for alternative behaviors
- Use Home Assistant automations or scripts alongside this blueprint for additional logic
- Check the logbook frequently when making configuration changes

---

**Last Updated**: January 2026
**Home Assistant Version**: 2024.1+
