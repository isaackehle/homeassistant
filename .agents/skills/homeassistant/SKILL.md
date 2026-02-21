---
name: homeassistant
description: Home Assistant blueprints, automations, and API control - best practices and patterns.
homepage: https://www.home-assistant.io/
metadata: {"clawdis":{"emoji":"🏠","requires":{"bins":["curl"],"env":["HA_TOKEN"]},"primaryEnv":"HA_TOKEN"}}
---

# Home Assistant

Best practices for blueprints, automations, and API control.

---

## Blueprint Structure

### Basic Blueprint Template
```yaml
blueprint:
  name: Descriptive Name
  description: What this blueprint does
  domain: automation  # or script
  author: Your Name
  source_url: https://github.com/...
  input:
    # Required inputs first
    target_entity:
      name: Target Entity
      description: The entity to control
      selector:
        entity:
          domain: light
    # Optional inputs with defaults
    delay_seconds:
      name: Delay
      description: Time to wait before action
      default: 5
      selector:
        number:
          min: 0
          max: 300
          unit_of_measurement: seconds

triggers:
  - trigger: state
    entity_id: !input target_entity

actions:
  - delay:
      seconds: !input delay_seconds
  - action: light.turn_on
    target:
      entity_id: !input target_entity
```

### Input Selectors Reference
```yaml
# Entity selector
selector:
  entity:
    domain: light
    multiple: true  # allow selecting multiple entities

# Device selector
selector:
  device:
    integration: zwave_js

# Area selector
selector:
  area:
    multiple: true

# Number selector
selector:
  number:
    min: 0
    max: 100
    step: 5
    unit_of_measurement: "%"
    mode: slider  # or box

# Time selector
selector:
  time:

# Duration selector
selector:
  duration:

# Boolean selector
selector:
  boolean:

# Text selector
selector:
  text:
    multiline: false

# Select (dropdown)
selector:
  select:
    options:
      - "option_1"
      - "option_2"
      - label: "Friendly Name"
        value: "option_3"

# Target selector (entity, device, or area)
selector:
  target:
    entity:
      domain: light

# Action selector (for nested actions)
selector:
  action:

# Condition selector
selector:
  condition:

# Trigger selector
selector:
  trigger:
```

---

## Triggers

### Common Trigger Patterns
```yaml
# State change
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
    from: "off"  # optional, but explicit is better
    for:
      seconds: 5  # must be in state for duration

# Numeric state (threshold)
triggers:
  - trigger: numeric_state
    entity_id: sensor.temperature
    above: 75
    below: 85  # optional range

# Time pattern
triggers:
  - trigger: time_pattern
    minutes: "/5"  # every 5 minutes

# Specific time
triggers:
  - trigger: time
    at: "07:00:00"

# Sun events
triggers:
  - trigger: sun
    event: sunset
    offset: "-00:30:00"  # 30 min before sunset

# Template trigger
triggers:
  - trigger: template
    value_template: "{{ states('sensor.power') | float > 100 }}"

# Device trigger (preferred for physical devices)
triggers:
  - trigger: device
    device_id: abc123
    domain: zwave_js
    type: event.value_notification.entry_control

# Multiple triggers with IDs
triggers:
  - trigger: state
    entity_id: binary_sensor.motion
    to: "on"
    id: motion_on
  - trigger: state
    entity_id: binary_sensor.motion
    to: "off"
    for:
      minutes: 5
    id: motion_off
```

---

## Conditions

### Common Condition Patterns
```yaml
# State condition
conditions:
  - condition: state
    entity_id: input_boolean.vacation_mode
    state: "off"

# Numeric state
conditions:
  - condition: numeric_state
    entity_id: sensor.illuminance
    below: 50

# Time condition
conditions:
  - condition: time
    after: "08:00:00"
    before: "22:00:00"
    weekday:
      - mon
      - tue
      - wed
      - thu
      - fri

# Sun condition
conditions:
  - condition: sun
    after: sunset
    before: sunrise

# Template condition
conditions:
  - condition: template
    value_template: "{{ is_state('alarm_control_panel.home', 'armed_away') }}"

# AND/OR logic
conditions:
  - condition: and
    conditions:
      - condition: state
        entity_id: input_boolean.guests
        state: "off"
      - condition: or
        conditions:
          - condition: time
            after: "22:00:00"
          - condition: time
            before: "06:00:00"

# Trigger ID condition
conditions:
  - condition: trigger
    id: motion_on
```

---

## Actions

### Common Action Patterns
```yaml
# Service call
actions:
  - action: light.turn_on
    target:
      entity_id: light.living_room
    data:
      brightness_pct: 80
      transition: 2

# Dynamic target from input
actions:
  - action: light.turn_on
    target:
      entity_id: !input target_light

# Choose based on trigger
actions:
  - choose:
      - conditions:
          - condition: trigger
            id: motion_on
        sequence:
          - action: light.turn_on
            target:
              entity_id: !input target_light
      - conditions:
          - condition: trigger
            id: motion_off
        sequence:
          - action: light.turn_off
            target:
              entity_id: !input target_light
    default:
      - action: notify.notify
        data:
          message: "Unknown trigger"

# If/then/else
actions:
  - if:
      - condition: state
        entity_id: binary_sensor.door
        state: "on"
    then:
      - action: notify.mobile_app
        data:
          message: "Door is open!"
    else:
      - action: notify.mobile_app
        data:
          message: "Door is closed"

# Repeat
actions:
  - repeat:
      count: 3
      sequence:
        - action: light.toggle
          target:
            entity_id: light.alert
        - delay:
          seconds: 1

# Wait for trigger
actions:
  - wait_for_trigger:
      - trigger: state
        entity_id: binary_sensor.door
        to: "off"
    timeout:
      minutes: 5
    continue_on_timeout: true

# Variables
actions:
  - variables:
      light_brightness: "{{ states('sensor.illuminance') | int }}"
  - action: light.turn_on
    data:
      brightness: "{{ 255 - light_brightness }}"

# Parallel execution
actions:
  - parallel:
      - action: light.turn_on
        target:
          entity_id: light.room_1
      - action: light.turn_on
        target:
          entity_id: light.room_2
```

---

## Jinja2 Templates

### Common Patterns
```yaml
# Get state
"{{ states('sensor.temperature') }}"

# Get state with default
"{{ states('sensor.temperature', 0) }}"

# Get attribute
"{{ state_attr('light.living_room', 'brightness') }}"

# Check state
"{{ is_state('binary_sensor.motion', 'on') }}"

# Check multiple states
"{{ is_state_attr('light.lamp', 'brightness', 255) }}"

# Type conversion
"{{ states('sensor.temp') | float }}"
"{{ states('sensor.count') | int }}"
"{{ states('sensor.value') | float(0) }}"  # with default

# Math operations
"{{ (states('sensor.temp') | float * 9/5) + 32 }}"

# Time comparisons
"{{ now().hour >= 22 or now().hour < 6 }}"
"{{ as_timestamp(now()) - as_timestamp(states.binary_sensor.motion.last_changed) > 300 }}"

# List operations
"{{ expand('group.all_lights') | selectattr('state', 'eq', 'on') | list | count }}"

# Area/device expansion
"{{ area_entities('living_room') | select('match', 'light.*') | list }}"
"{{ device_entities('abc123') }}"

# Formatting
"{{ states('sensor.temp') | round(1) }}°F"
"{{ now().strftime('%H:%M') }}"
```

### Template Best Practices
- Always use `| float(0)` or `| int(0)` with defaults to avoid errors
- Check for `unavailable` or `unknown` states: `{{ states('sensor.x') not in ['unavailable', 'unknown'] }}`
- Use `this.entity_id` in templates to reference the current entity
- Avoid complex templates in triggers; use template sensors instead

---

## Best Practices

### Naming Conventions
- **Blueprints**: `snake_case.yaml` (e.g., `motion_activated_light.yaml`)
- **Automations**: Descriptive names with location (e.g., "Kitchen Motion Light")
- **Helpers**: Prefix with purpose (e.g., `input_boolean.vacation_mode`)

### Blueprint Design
1. **Use descriptive input names** with clear descriptions
2. **Provide sensible defaults** for optional inputs
3. **Use appropriate selectors** to guide user input
4. **Include source_url** for easy updates
5. **Add trigger IDs** when handling multiple triggers
6. **Use `mode: restart`** for motion lights, `mode: single` for notifications

### Automation Modes
```yaml
mode: single      # Ignore new triggers while running (default)
mode: restart     # Cancel and restart on new trigger
mode: queued      # Queue up to max triggers
  max: 10
mode: parallel    # Run multiple instances
  max: 10
```

### Error Handling
```yaml
# Continue on error
actions:
  - action: notify.mobile_app
    data:
      message: "Test"
    continue_on_error: true

# Use default values in templates
"{{ states('sensor.missing') | float(0) }}"
```

### Performance Tips
- Prefer `state` triggers over `template` triggers
- Use `for:` in state triggers to debounce
- Avoid polling; use event-driven triggers
- Use `device_class` in selectors to filter relevant entities

---

## API Control

### Setup
Set environment variables:
- `HA_URL`: Your Home Assistant URL (e.g., `http://192.168.1.100:8123`)
- `HA_TOKEN`: Long-lived access token (create in HA → Profile → Long-Lived Access Tokens)

### Quick Commands
```bash
# List entities by domain
curl -s "$HA_URL/api/states" -H "Authorization: Bearer $HA_TOKEN" | \
  jq -r '.[] | select(.entity_id | startswith("switch.")) | .entity_id'

# Turn on/off
curl -s -X POST "$HA_URL/api/services/switch/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "switch.office_lamp"}'

# Control lights with brightness
curl -s -X POST "$HA_URL/api/services/light/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room", "brightness_pct": 80}'

# Trigger scene
curl -s -X POST "$HA_URL/api/services/scene/turn_on" \
  -H "Authorization: Bearer $HA_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "scene.movie_time"}'

# Get entity state
curl -s "$HA_URL/api/states/{entity_id}" -H "Authorization: Bearer $HA_TOKEN"
```

### Entity Domains
- `switch.*` — Smart plugs, generic switches
- `light.*` — Lights (Hue, LIFX, etc.)
- `scene.*` — Pre-configured scenes
- `automation.*` — Automations
- `climate.*` — Thermostats
- `cover.*` — Blinds, garage doors
- `media_player.*` — TVs, speakers
- `sensor.*` — Temperature, humidity, etc.
- `binary_sensor.*` — Motion, door/window, presence
- `input_boolean.*` — Toggle helpers
- `input_number.*` — Number helpers
- `input_select.*` — Dropdown helpers
