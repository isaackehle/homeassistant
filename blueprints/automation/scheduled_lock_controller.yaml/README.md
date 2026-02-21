# Scheduled Lock Controller Blueprint

Automatically locks a configurable list of locks at a specified time each day. Features include retry logic if locks fail and optional notifications.

## Features

- **Configurable Lock Time**: Set the time when locks should engage
- **Multiple Locks**: Control any number of locks in a single automation
- **Retry Logic**: If a lock fails to engage, it will retry after a delay
- **Smart Notifications**: Optional notifications for lock status (success, failure, or both)
- **Parallel Execution**: All locks are processed in sequence with proper delay handling

## Usage

1. Create an automation from this blueprint via Home Assistant UI
2. Configure the following inputs:
   - **Time to Lock**: Set the time you want locks to engage (default: 22:30)
   - **Locks to Control**: Select the lock entities you want to control
   - **Retry Delay**: Time to wait before checking if lock succeeded (default: 30 seconds)
   - **Notification Service**: (Optional) Your notification service (e.g., `notify.mobile_app_your_phone`)
   - **Notify on Failure Only**: Choose whether to notify on all locks or only failures

## Example Configuration

When creating an automation from this blueprint, select:
- Time: 22:30
- Locks: basement_door, kitchen_sliding_door, dining_room_door, living_room_door
- Retry Delay: 30 seconds
- Notification Service: notify.mobile_app_isaac_iphone_16
- Notify on Failure Only: true

## How It Works

1. At the specified time, the blueprint triggers
2. For each lock in the list:
   - Attempts to lock the device
   - Waits for the retry delay period
   - Checks if the lock is now in the `locked` state
   - If locked: optionally sends success notification
   - If not locked: retries the lock command and sends failure notification

## Notes

- Ensure all selected lock entities are valid and accessible
- The retry delay should be long enough for your locks to respond (30 seconds is typical)
- Notifications are optional - leave blank to disable
- The automation runs in `single` mode to prevent overlapping executions
