# Bathroom Exhaust Controller Blueprint

## Overview

This blueprint manages a bathroom exhaust fan using humidity, a manual run helper, and a steam-shower bypass mode.

It is designed to:
- Turn the fan on when humidity is high.
- Turn the fan off when humidity is low for a sustained period.
- Support manual run windows with automatic timeout.
- Force the fan off during steam-shower mode.
- Use a timer helper so remaining steam time is visible in the UI.
- Optionally recheck whether steam is still active before resuming normal behavior.
- Optionally announce when steam mode ends and exhaust resumes.

## Flow Chart

```mermaid
flowchart TD
    A[Trigger Event] --> B{Which trigger fired?}

    %% Humidity logic
    B -->|humidity_high| C{Bypass OFF?}
    C -->|Yes| C1[Turn fan ON]
    C -->|No| C2[No action]

    B -->|humidity_low for delay| D{Bypass OFF and Manual helper OFF?}
    D -->|Yes| D1[Turn fan OFF]
    D -->|No| D2[No action]

    %% Manual run logic
    B -->|manual_run_on| E{Bypass OFF?}
    E -->|Yes| E1[Turn fan ON]
    E -->|No| E2[No action]

    B -->|manual_run_timeout| F[Turn manual helper OFF]
    F --> G{Bypass ON?}
    G -->|Yes| G1[Turn fan OFF]
    G -->|No| H{Humidity below OFF threshold?}
    H -->|Yes| H1[Turn fan OFF]
    H -->|No| H2[Leave fan as-is]

    B -->|manual_run_off| I{Bypass OFF and Humidity below OFF threshold?}
    I -->|Yes| I1[Turn fan OFF]
    I -->|No| I2[No action]

    %% Bypass on logic
    B -->|bypass_on| J[Turn manual helper OFF]
    J --> J1[Turn fan OFF]
    J1 --> K{Steam timer idle?}
    K -->|Yes| K1[Start steam timer using Steam Shower Duration]
    K -->|No| K2[Keep current timer]

    %% Timer finished while bypass active
    B -->|steam_timer_finished| L{Bypass still ON?}
    L -->|No| L0[No action]
    L -->|Yes| M{Steam active sensor configured and ON?}
    M -->|Yes| M1[Restart timer using Recheck Interval]
    M -->|No| N[Wait Post-Steam Resume Delay]
    N --> N1[Turn manual helper ON]
    N1 --> N2[Turn bypass OFF]
    N2 --> N3[Turn fan ON]
    N3 --> O{Announcements enabled and configured?}
    O -->|Yes| O1[Send TTS announcement]
    O -->|No| O2[Done]

    %% Bypass off reconciliation
    B -->|bypass_off| P[Cancel steam timer]
    P --> Q{Manual helper ON?}
    Q -->|Yes| Q1[Turn fan ON]
    Q -->|No| R{Humidity above ON threshold?}
    R -->|Yes| R1[Turn fan ON]
    R -->|No| S{Humidity below OFF threshold?}
    S -->|Yes| S1[Turn fan OFF]
    S -->|No| S2[No action]
```

## Required Inputs

- Humidity Sensor (`sensor`)
- Exhaust Fan (`fan` or `switch`)
- Manual Run Helper (`input_boolean`)
- Steam Shower Bypass (`input_boolean`)
- Steam Shower Timer (`timer`)

## Optional Inputs

- Steam Still Active Sensor (`binary_sensor` or `input_boolean`)
- Enable Steam-End Announcement (`boolean`)
- TTS Service (`text`)
- Announcement Players (`media_player`, multiple)
- Announcement Message (`text`)

## Thresholds and Timers

- Turn-On Humidity: default `60%`
- Turn-Off Humidity: default `40%`
- Turn-Off Delay: default `10 minutes`
- Manual Run Time: default `40 minutes`
- Steam Shower Duration: default `15 minutes`
- Post-Steam Resume Delay: default `0 minutes`
- Steam Recheck Interval: default `5 minutes`

## Recommended Helper Setup

Create these helpers before using the blueprint:
- `input_boolean` for manual run helper
- `input_boolean` for steam-shower bypass
- `timer` for steam-shower timer
- Optional `binary_sensor` or `input_boolean` for steam-active recheck

## Notes

- Steam-shower mode intentionally forces the fan off.
- When steam mode completes, the blueprint can resume fan operation by turning the manual helper on, turning bypass off, and turning the fan on.
- If the optional steam-active sensor is still on when the timer ends, the timer is restarted instead of resuming.
- Automation mode is `queued` with `max: 10`, which helps process overlapping trigger events in order.
