# Smart Door Auto-Lock Blueprint

A comprehensive Home Assistant blueprint for automatic door locking with safety features, multiple trigger types, and built-in debugging.

## Features

- **Time-based locking**: Lock after door has been closed for a configurable period
- **Presence-based locking**: Lock when presence entity indicates "away" status
- **Manual triggers**: Instant lock via button press or sensor action
- **Safety first**: Never locks while door is open; waits with configurable timeout
- **Override mode**: Disable automation via input_boolean helper
- **Flexible sensor support**: Handles both ON=open and ON=closed door sensors
- **Built-in debugging**: Optional system_log and logbook entries with full state snapshots
- **Restart mode**: New triggers cancel pending locks and start fresh
- **Grace periods**: Multiple configurable delays for final abort opportunities

## Inputs

### Required Entities

- **Lock**: The door lock entity to control
- **Door contact sensor**: Binary sensor monitoring door open/closed state
- **Presence entity**: Person or device_tracker for away detection
- **Override helper**: input_boolean to enable/disable auto-locking

### Optional Entities

- **Run now sensors**: Array of sensors that trigger immediate lock attempts when pressed

### Configuration

- **Away state**: State value indicating presence is away (default: "not_home")
- **Door closed for**: How long door must be closed before locking (default: 15 min)
- **Away for**: Grace period after going away before locking (default: 5 min)
- **Closed stability time**: How long door must stay closed to be considered stable (default: 30 sec)
- **Max wait for close (when away)**: Timeout for waiting for door to close when away (default: 10 min)
- **Final grace before locking**: Last-second delay before actual lock (default: 3 min)
- **Contact open equals 'on'**: Set false if your sensor reports ON=closed instead of ON=open

## Triggers

### Primary Triggers

1. **Door closed**: When door sensor indicates closed for the configured duration
2. **Presence away**: When presence entity reaches away state for the configured duration
3. **Override changed**: When override boolean is toggled (OFF may trigger immediate lock)
4. **Run now**: When any configured sensor reports "single" or "Press" action

## Logic Flow

### Case 0: Override Disabled
- Trigger: Override boolean turned OFF
- Condition: Door is closed AND lock is unlocked
- Action: Lock immediately

### Case 1: Door Closed Long Enough
- Trigger: Door has been closed for configured duration
- Condition: Lock is unlocked AND door still closed
- Action: Wait final grace period, then lock

### Case 2: Presence Away
- Trigger: Presence has been away for configured duration
- Condition: Lock is unlocked
- Logic:
  - If door is open, wait for it to close (up to timeout)
  - If door doesn't close, give up (safety)
  - If door closes, verify presence still away
  - Wait final grace period, then lock

### Case 3: Run Now
- Trigger: Run now sensor activated
- Condition: Door is closed AND lock is unlocked
- Action: Lock immediately (no grace period)

## Safety Features

- **Never locks open doors**: Always verifies door is closed before locking
- **Timeout protection**: Gives up waiting if door stays open too long
- **Restart mode**: New events cancel pending locks and re-evaluate
- **Override support**: Complete disable when override is ON
- **Multiple verification points**: Checks door state before and after delays

## Code Improvements

### Helper Variables
- `door_is_closed`: Single-evaluation template that handles both sensor polarities
- `override_state`: Direct state value for simplified comparisons
- Reduces code duplication from 6+ identical door-check templates to 1 reusable variable

### Debug Support
- Enable by setting `is_debug: true` in variables section
- Captures full snapshot on every trigger:
  - Trigger ID and timestamp
  - Lock and door states (raw and resolved)
  - Presence and override states
- Writes to both system_log and logbook
- Trace variables preserved even when debug logging is disabled

## Example Configuration

```yaml
alias: Front Door Auto-Lock
use_blueprint:
  path: door-lock-with-multiple-inputs.yaml
  input:
    lock_entity: lock.front_door
    contact_entity: binary_sensor.front_door_contact
    presence_entity: person.john_doe
    is_override_enabled: input_boolean.front_door_autolock_override
    run_now_sensors:
      - sensor.keypad_action
    away_state: "not_home"
    door_closed_for:
      minutes: 10
    away_for:
      minutes: 3
    grace_before_lock:
      minutes: 2
```

## Troubleshooting

1. **Lock won't engage**: Check that override boolean is OFF
2. **Locks while open**: Verify "Contact open equals 'on'" setting matches your sensor
3. **Never locks when away**: Check presence entity states and away_state configuration
4. **Enable debug logging**: Set `is_debug: true` in the automation's variables section to see detailed execution logs

