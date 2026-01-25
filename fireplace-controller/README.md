# Fireplace Controller Blueprint Documentation

## Overview
The Fireplace Controller Blueprint is a comprehensive Home Assistant automation that intelligently manages a fireplace blower based on temperature readings from multiple sources. It provides flexible control through different operation modes and supports both internal and external temperature monitoring.

This blueprint uses template-based logic for optimal compatibility and includes robust handling of optional sensor configurations.

## Purpose
This blueprint automates fireplace blower operation to:
- Improve heat circulation efficiency
- Prevent overheating of fireplace components
- Provide manual override capabilities
- Allow temperature-based automatic control
- Support flexible sensor configurations (both, one, or no sensors)

## Configuration Inputs

### Required Inputs
- **Blower Switch**: The switch entity that controls the fireplace blower
- **Operation Mode Entity**: An `input_select` helper to control operation mode

### Input Select Helper Setup
Before using this blueprint, create an `input_select` helper with these exact options:
- `off`
- `auto`
- `always_on`

**Steps to create:**
1. Go to Settings → Devices & Services → Helpers
2. Click "Create Helper" → "Dropdown"
3. Name: "Fireplace Operation Mode" (or your preference)
4. Options: off, auto, always_on
5. Set default to "auto"

### Optional Temperature Sensors
- **Internal Temperature Sensor**: Monitors fireplace internal temperature (completely optional)
- **External Temperature Sensor**: Monitors ambient/external temperature (completely optional)

**Note**: Both sensors are truly optional - you can use the blueprint with:
- Both sensors configured
- Only one sensor configured
- No sensors (manual operation only)

### Operation Modes
- **off**: Disables all automation
- **auto**: Temperature-based automatic control (default)
- **always_on**: Forces blower to run continuously

### Temperature Thresholds

#### Internal Sensor Thresholds
- **High Threshold**: Default 120° (turn on blower)
- **Low Threshold**: Default 90° (turn off blower)

#### External Sensor Thresholds
- **High Threshold**: Default 80° (turn on blower)
- **Low Threshold**: Default 75° (turn off blower)

**Note**: Thresholds are only used when their corresponding sensors are configured.

## How It Works

### Triggers
The automation uses a **dual-trigger system** for optimal responsiveness:
- **State Changes**: Immediate response when operation mode changes
- **Time Pattern**: Regular evaluation every 3 minutes for temperature conditions

### Operation Modes

#### Off Mode (`off`)
- All automation is disabled immediately upon selection
- No automatic blower control
- Manual switch operation only

#### Auto Mode (`auto`)
- **Immediate Activation**: Starts temperature monitoring when mode is selected
- **Blower Turns ON** when (checked every 3 minutes):
  - Internal sensor > internal high threshold (120°), OR
  - External sensor > external high threshold (80°)
- **Blower Turns OFF** when (checked every 3 minutes):
  - Internal sensor < internal low threshold (90°), OR
  - External sensor < external low threshold (75°)

#### Always On Mode (`always_on`)
- **Immediate Activation**: Blower turns on immediately when mode is selected
- Runs continuously regardless of temperature
- No temperature monitoring in this mode

### Sensor Configuration Flexibility

#### Both Sensors Configured
- Full dual-sensor temperature control
- Either sensor can trigger blower operation
- Provides redundancy and comprehensive monitoring

#### Single Sensor Configured
- Works with either internal OR external sensor only
- Other sensor inputs ignored if not configured
- Simplified single-point temperature control

#### No Sensors Configured
- Manual operation only through operation modes
- Can still use "off" and "always_on" modes
- Useful for manual fireplace control

### Safety Features

#### Hysteresis Prevention
- Separate high/low thresholds prevent rapid on/off cycling
- Default 30° gap between internal thresholds (120° on, 90° off)
- Default 5° gap between external thresholds (80° on, 75° off)

#### Graceful Degradation
- Continues operating if one sensor becomes unavailable
- Template conditions check sensor availability before evaluation
- Fallback to single-sensor operation

### Logic Flow

1. **Dual Trigger System**: Automation responds to both operation mode changes (immediate) and time pattern (every 3 minutes)
2. **Variable Evaluation**: Calculates operation mode, temperatures, and decision flags
3. **Mode Evaluation**:
   - If "always_on" or "off": Immediate action (turn on/off respectively)
   - If "auto": Evaluate temperature conditions from configured sensors
4. **Temperature Evaluation** (auto mode only):
   - Check if sensors are configured using template conditions
   - Read current sensor values and compare to thresholds
   - Execute appropriate blower action based on any configured sensor meeting conditions

### Technical Implementation

#### Dual Trigger System
- **State Change Trigger**: `trigger: state` on `operation_mode_entity` for immediate response
- **Time Pattern Trigger**: `trigger: time_pattern` with `minutes: "/3"` for regular temperature evaluation
- **Smart Response**: Mode changes trigger immediate action, temperature monitoring continues every 3 minutes

#### Variable-Based Decision Logic
- **Pre-calculated Variables**: Decision flags computed before action execution
- **Operation Mode**: Extracted from input_select state for template usage
- **Temperature Readings**: Current sensor values stored as variables
- **Decision Flags**: `should_turn_on` and `should_turn_off` computed from mode and temperature conditions
- **Simplified Actions**: Choose blocks use decision variables instead of complex nested conditions

#### Entity-Based Operation Mode
- **Input Select Helper**: Uses Home Assistant `input_select` entity for mode control
- **Real Entity State**: `{{ states(operation_mode_entity) }}` reads actual entity state
- **Dashboard Integration**: Can be controlled from any Home Assistant interface
- **Automation Compatibility**: Other automations can change the mode programmatically

#### Template-Based Temperature Logic
- **Direct State Evaluation**: `{{ states(sensor) | float(0) > threshold }}`
- **Safe Defaults**: `| float(0)` handles unavailable sensors gracefully
- **Real-Time Comparison**: Compares current sensor values to thresholds each cycle
- **Immediate Response**: Mode changes trigger instant evaluation

#### Sensor Configuration Detection
- **Template Guards**: `{{ internal_temperature_sensor != '' and internal_temperature_sensor != none }}`
- **Smart Evaluation**: Only evaluates sensors that are actually configured
- **Error Prevention**: No attempts to read unconfigured sensor states
- **Flexible Configuration**: Works with any combination of sensor setups

### Use Cases

#### Standard Fireplace
- Internal sensor for heat monitoring
- External sensor for ambient temperature
- Auto mode for temperature-based control

#### Simple Setup
- Single internal sensor only
- Basic temperature control
- Manual override capabilities

#### Manual Operation
- No sensors required
- Use "off" and "always_on" modes only
- Complete manual control

#### Seasonal Operation
- Switch between modes based on season
- External sensor for cooling season
- Internal sensor for heating season

## Installation and Setup

### Prerequisites
1. **Create Input Select Helper** (Required):
   - Go to Settings → Devices & Services → Helpers
   - Create Helper → Dropdown
   - Name: "Fireplace Operation Mode" (or your preference)
   - Options: off, auto, always_on (exactly these values)
   - Set default to "auto"

### Blueprint Setup
1. **Import Blueprint**: Add blueprint to Home Assistant
2. **Create Automation**: Create new automation from blueprint
3. **Configure Required Inputs**:
   - Select the blower switch entity for your fireplace
   - Select the input_select helper you created for operation mode
4. **Configure Sensors** (Optional):
   - Select internal temperature sensor if available
   - Select external temperature sensor if available
   - Leave either or both empty if not needed
5. **Adjust Thresholds**: Modify temperature thresholds as needed for your setup
6. **Test Functionality**: Verify automation responds correctly

### Setup Notes
- **Entity Selection**: Optional sensors show empty dropdowns - this is normal
- **Input Select**: Must have exactly these options: off, auto, always_on
- **No Errors**: Empty sensor fields will not cause validation errors
- **Flexible Configuration**: Start simple and add sensors later as needed

### Operation Control
- **Dashboard**: Add the input_select helper to your dashboard for manual control
- **Voice Control**: Use voice assistants to change operation mode
- **Automation**: Other automations can change the mode programmatically

### Common Issues
- **Missing Input Select**: Create the required input_select helper before setting up automation
- **Wrong Helper Options**: Must use exactly: off, auto, always_on (case sensitive)
- **Immediate Response**: Mode changes now take effect immediately (not delayed)
- **Validation Errors**: Ensure operation mode entity and blower switch are configured

### Operational Issues
- **Blower not responding**: Check operation mode (ensure not "off") and verify input_select state
- **Mode changes ignored**: Verify input_select helper is working and has correct options
- **No temperature control**: Confirm sensors are configured and working
- **Dashboard Control**: Add input_select helper to dashboard for easy mode switching

### Debug Steps
1. **Check Helper**: Verify input_select has correct options and can be changed manually
2. **Automation Traces**: Check traces in Home Assistant for template evaluation results
3. **Entity States**: Verify sensor states are updating and readable in Developer Tools
4. **Template Testing**: Test conditions in Developer Tools > Templates
5. **Mode Testing**: Change operation mode and observe immediate response
6. **Monitor Logs**: Watch automation execution in Home Assistant logs