# Door lock automation

## Triggers

- Door lock state binary sensor: locked and unlocked
- Door position binary sensor: opened or closed
- Timer entity for the delay
- Timer default (how much time to wait for the door to lock)
- Passage mode (to disable the auto lock)

## Events

- Door position changed (position)
- Lock state changed (lock_state)
- Timer changed
- Passage mode changed

## Logic

| Lock state | Door position | Timer state | Passage Mode | Description        | Action(s)     |
| ---------- | ------------- | ----------- | ------------ | ------------------ | ------------- |
| **Locked** | Closed        | Idle        | X            |                    |               |
| **Locked** | Closed        | Active      | X            |                    | Timer -> Idle |
| Locked     | Closed        | **Idle**    | X            | Target final state |               |
| Locked     | Closed        | **Active**  | X            | Stop timer         | Timer -> Idle |
| Locked     | **Closed**    | X           | X            | Alert?             | Timer -> Idle |

| Lock state | Door position | Timer state | Passage Mode | Description | Action(s)         |
| ---------- | ------------- | ----------- | ------------ | ----------- | ----------------- |
| **Locked** | Open          | X           | X            | Alert??     | State -> Unlocked |
| Locked     | **Open**      | X           | X            | Alert??     | State -> Unlocked |
| Locked     | Open          | X           | **X**        | Alert??     | State -> Unlocked |
| Locked     | Open          | **Idle**    | X            |             |                   |
| Locked     | Open          | **Active**  | X            |             | Timer -> Idle     |

| Lock state   | Door position | Timer state | Passage Mode | Description               | Action(s)     |
| ------------ | ------------- | ----------- | ------------ | ------------------------- | ------------- |
| **Unlocked** | Open          | Idle        | X            | Waiting for door to close |               |
| Unlocked     | **Open**      | Idle        | X            | Waiting for door to close |               |
| Unlocked     | Open          | **Idle**    | X            | Waiting for door to close |               |
| Unlocked     | Open          | Idle        | **X**        | Waiting for door to close |               |
| **Unlocked** | Open          | Active      | X            | Waiting, clear timer      | Timer -> Idle |
| Unlocked     | **Open**      | Active      | X            | Waiting, clear timer      | Timer -> Idle |
| Unlocked     | Open          | **Active**  | X            | Waiting, clear timer      | Timer -> Idle |
| Unlocked     | Open          | Active      | **X**        | Waiting, clear timer      | Timer -> Idle |

| Lock state   | Door position | Timer state | Passage Mode | Description                             | Action(s)       |
| ------------ | ------------- | ----------- | ------------ | --------------------------------------- | --------------- |
| **Unlocked** | Closed        | Idle        | X            | Start timer                             | Timer -> Active |
| Unlocked     | **Closed**    | Idle        | X            | Start timer                             | Timer -> Active |
| Unlocked     | Closed        | **Idle**    | X            | Timer expired!                          | State -> Lock   |
| Unlocked     | Closed        | Idle        | **Enabled**  | Automation disabled                     |                 |
| Unlocked     | Closed        | Idle        | **Disabled** | Automation enabled after timer expired! | State -> Lock   |
| **Unlocked** | Closed        | Active      | X            | Wait for timer                          |                 |
| Unlocked     | **Closed**    | Active      | X            | Wait for timer                          |                 |
| Unlocked     | Closed        | **Active**  | X            | Wait for timer                          |                 |
| Unlocked     | Closed        | Active      | **Enabled**  | Automation disabled                     |                 |
| Unlocked     | Closed        | Active      | **Disabled** | Reset timer                             | Timer -> Active |
