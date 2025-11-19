# mmumu

A Python wrapper for Netease MuMu Player automation, providing a clean API for managing emulators and interacting with them via the MuMu SDK.

## Features

- **Emulator Management**: Create, delete, clone, rename, and list MuMu instances.
- **Control**: Launch, shutdown, restart, and manage window layout.
- **Automation**: Connect via MuMu SDK (ctypes) to send touch/key events and capture screen.
- **Robustness**: Thread-safe connection pooling, automatic path detection, and proper error handling.

## Installation

```bash
pip install mmumu
```

## Usage

### Basic Manager Operations

```python
from mmumu import MuMuManager

# Initialize manager (auto-detects MuMu installation)
manager = MuMuManager()

# List all players
players = manager.get_all_players_info()
for player in players:
    print(f"Player {player.index}: {player.name}")

# Launch a player
manager.launch_player(0)
```

### Advanced Control with API

```python
from mmumu import MuMuApi

api = MuMuApi()

# Connect to a running instance
# Note: You need the base install path and instance index
handle = api.connect("C:\\Program Files\\Netease\\MuMu", 0)

# Send a touch event
api.input_event_touch_down(handle, display_id=0, x=100, y=100)
api.input_event_touch_up(handle, display_id=0)

# Clean up
api.disconnect(handle)
```

## Requirements

- Windows OS
- Netease MuMu Player installed
- Python 3.9+

## License

MIT License
