# Theater Ceiling Fans Setup Guide

This guide provides step-by-step instructions for setting up direction control for your theater ceiling fans using the blueprint.

## Your Theater Fan Setup

### Current Entities
- **North Fan**: `fan.theater_ceiling_fan_north`
- **South Fan**: `fan.theater_ceiling_fan_south`

### New Entities You'll Create

#### Shelly Cover Entities (Shelly Plus 2PM Gen4 in Cover Mode)
- **North Fan Relay**: `cover.theater_fan_north_direction`
- **South Fan Relay**: `cover.theater_fan_south_direction`

#### Input Select Helpers (Direction Tracking)
- **North Fan Direction**: `input_select.theater_fan_north_direction`
- **South Fan Direction**: `input_select.theater_fan_south_direction`

---

## Step-by-Step Setup

### Step 1: Set Up Shelly Plus 2PM Gen4 Devices

1. **Install Shelly devices** physically (one per fan)
2. **Configure each Shelly in ROLLER/COVER mode** (not switch mode):
   - Open Shelly web interface
   - Go to Settings → Device Type
   - Select "Roller" or "Cover"
   - Configure relay behavior for polarity reversal
3. **Add to Home Assistant**:
   - Shelly integration will auto-discover devices
   - Accept the discovered devices
   - Rename cover entities to match:
     - `cover.theater_fan_north_direction`
     - `cover.theater_fan_south_direction`

### Step 2: Create Input Select Helpers

**Option A: Via Home Assistant UI (Recommended)**

1. Go to **Settings → Devices & Services → Helpers**
2. Click **"Create Helper"** → **"Dropdown"**
3. For North Fan:
   - Name: "Theater Fan North Direction"
   - Icon: `mdi:fan`
   - Options (add these exactly):
     - `Forward (Summer)`
     - `Reverse (Winter)`
   - Initial Value: `Forward (Summer)`
4. Click **"Create"**
5. Repeat for South Fan with "Theater Fan South Direction"

**Option B: Via YAML Configuration**

Copy the configuration from [example-helpers.yaml](example-helpers.yaml) to your `configuration.yaml` or `input_select.yaml` file, then restart Home Assistant.

### Step 3: Import the Blueprint to Your Main HA Config

In your **main Home Assistant configuration** (not this blueprints repo):

1. Go to **Settings → Automations & Scenes → Blueprints**
2. Click **"Import Blueprint"**
3. Enter URL:
   ```
   https://github.com/isaackehle/homeassistant/blueprints/automation/ceiling-fan/ceiling-fan-direction-control.yaml
   ```
4. Click **"Preview"** → **"Import"**

### Step 4: Create Automations from Blueprint

**For North Fan:**

1. Go to **Settings → Automations & Scenes**
2. Click **"Create Automation"** → **"Use Blueprint"**
3. Select **"Ceiling Fan Direction Control with Safety"**
4. Configure:
   - **Name**: "Theater North Fan - Direction Control"
   - **Ceiling Fan**: `fan.theater_ceiling_fan_north`
   - **Direction Relay**: `cover.theater_fan_north_direction`
   - **Direction Selector**: `input_select.theater_fan_north_direction`
   - **Notification Targets**: Select your mobile app or notification service
   - **Motor Stop Delay**: 10 seconds (default)
   - **Relay Settle Delay**: 3 seconds (default)
   - **Enable Notifications**: On
5. Click **"Save"**

**For South Fan:**

Repeat the above steps with:
- **Name**: "Theater South Fan - Direction Control"
- **Ceiling Fan**: `fan.theater_ceiling_fan_south`
- **Direction Relay**: `cover.theater_fan_south_direction`
- **Direction Selector**: `input_select.theater_fan_south_direction`

**Alternative: Use YAML**

Copy configurations from [example-automations.yaml](example-automations.yaml) to your `automations.yaml` file.

### Step 5: Add Dashboard Controls

1. Go to your **Theater Room dashboard**
2. Click **"Edit Dashboard"** → **"Add Card"**
3. Choose **"Manual"** (YAML editor)
4. Copy one of the card configurations from [example-dashboard.yaml](example-dashboard.yaml)
5. Paste and click **"Save"**

**Recommended**: Use Option 1 (Simple Entities Card) for clean, organized fan controls.

### Step 6 (Optional): Add Safety Blocking Automations

For extra protection against accidental fan activation during direction changes:

1. **First**, note the automation entity IDs created in Step 4:
   - Go to **Settings → Automations & Scenes**
   - Find your automations (e.g., "Theater North Fan - Direction Control")
   - Click to open → Check the entity ID at the top (e.g., `automation.theater_north_fan_direction_control`)

2. **Copy the safety blocking configurations** from [example-safety-blocking.yaml](example-safety-blocking.yaml)

3. **Update the entity IDs** in the conditions to match your actual automation entity IDs

4. **Add to your** `automations.yaml` file

---

## Testing the Setup

### Initial Test (North Fan)

1. **Ensure fan is OFF**
2. **Open your dashboard** with the fan controls
3. **Change direction** via `input_select.theater_fan_north_direction`:
   - Select "Reverse (Winter)"
4. **Observe the automation**:
   - Fan should already be off (or turn off automatically)
   - Wait ~10 seconds (motor stop delay)
   - Relay should switch (check cover entity state)
   - Wait ~3 seconds (relay settle delay)
   - You should receive a notification "Safe to turn on"
5. **Turn fan ON** and verify it operates correctly
6. **Change back to "Forward (Summer)"** and repeat test

### Repeat for South Fan

Follow the same testing procedure for the south fan.

### What to Listen For

- **No clicking or buzzing** during direction change = Good!
- **Clicking sounds** = Increase motor_stop_delay to 15-20 seconds
- **Relay chattering** = Increase relay_settle_delay to 5 seconds

---

## Troubleshooting

### Fan doesn't turn off automatically
- Check automation is enabled
- Verify fan entity is correct
- Check automation traces for errors

### Relay doesn't switch
- Verify Shelly is in COVER/ROLLER mode (not switch mode)
- Test cover entity manually: Developer Tools → Services
  - `cover.open_cover` for Forward
  - `cover.close_cover` for Reverse
- Check Shelly device connectivity

### Notifications not received
- Verify notification service is configured
- Check "Enable Notifications" is ON
- Test notification service manually

### Direction changes multiple times
- This shouldn't happen with `mode: single`
- Check for other automations changing the input_select
- Review automation traces

---

## Dashboard Preview

Your theater room dashboard will show:

```
┌─────────────────────────────────────┐
│    Theater Ceiling Fans             │
├─────────────────────────────────────┤
│  North Fan                          │
│  ▪ Fan Control      [ON] [50%]      │
│  ▪ Direction        [Forward (Sum…] │
│                                     │
│  ─────────────────────────────────  │
│                                     │
│  South Fan                          │
│  ▪ Fan Control      [OFF]           │
│  ▪ Direction        [Reverse (Win…] │
└─────────────────────────────────────┘
```

---

## Quick Reference

### Entity Naming Convention

| Component | North Fan | South Fan |
|-----------|-----------|-----------|
| Fan Entity | `fan.theater_ceiling_fan_north` | `fan.theater_ceiling_fan_south` |
| Shelly Cover | `cover.theater_fan_north_direction` | `cover.theater_fan_south_direction` |
| Input Select | `input_select.theater_fan_north_direction` | `input_select.theater_fan_south_direction` |
| Automation | `automation.theater_north_fan_direction_control` | `automation.theater_south_fan_direction_control` |

### Direction Mapping

| Input Select Value | Shelly Cover Action | Motor Polarity | Airflow |
|-------------------|--------------------|--------------------|---------|
| `Forward (Summer)` | `cover.open_cover` | Normal | Down (cooling) |
| `Reverse (Winter)` | `cover.close_cover` | Reversed | Up (warm air circulation) |

### Safety Delays

| Delay | Default | Purpose | When to Increase |
|-------|---------|---------|------------------|
| Motor Stop | 10s | Motor fully stops | Clicking/buzzing during change |
| Relay Settle | 3s | Relay contacts engage | Relay chattering |

---

## Files in This Directory

- **[ceiling-fan-direction-control.yaml](ceiling-fan-direction-control.yaml)** - The blueprint automation
- **[README.md](README.md)** - Complete blueprint documentation
- **[SETUP-GUIDE.md](SETUP-GUIDE.md)** - This setup guide
- **[example-helpers.yaml](example-helpers.yaml)** - Input select helper configurations
- **[example-automations.yaml](example-automations.yaml)** - Example automation configurations
- **[example-dashboard.yaml](example-dashboard.yaml)** - Dashboard card configurations
- **[example-safety-blocking.yaml](example-safety-blocking.yaml)** - Optional safety blocking automations

---

## Support

- **Blueprint Issues**: https://github.com/isaackehle/homeassistant/issues
- **Documentation**: See [README.md](README.md)
- **Testing**: Run `pytest tests/test_ceiling_fan_direction_control_blueprint.py`

---

**Ready to get started? Begin with Step 1: Set Up Shelly Plus 2PM Gen4 Devices**
