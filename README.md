# RAM Monitor Daemon (`deamon_core.py`)

A lightweight, automated Python background daemon that continuously monitors system memory (RAM) usage. When system RAM crosses a critical threshold, the daemon identifies the heaviest memory-consuming process from a predefined target list, terminates it to restore system stability, logs the event, and sends a real-time alert via a Discord webhook.

*(Note: While referred to as a "CPU daemon," this script specifically monitors and manages system Virtual Memory/RAM).*

## Features

- **Continuous System Monitoring:** Polls system RAM utilization every 5 seconds.
- **Automated Culprit Termination:** Automatically identifies and terminates the heaviest memory-consuming process among specified target applications when RAM usage exceeds the defined threshold.
- **Self-Preservation:** Explicitly ignores its own Process ID (`DAEMON_PID`) so it never accidentally terminates itself when `python.exe` is in the target list.
- **Discord Alerts:** Sends formatted alert notifications to a configured Discord channel whenever a process is terminated.
- **Rotating Logs:** Logs system vitals, warnings, and actions taken to `system.log` with automatic log rotation (max 5 MB per file, keeping up to 2 backup files).

## Prerequisites

- **Python 3.x**
- **Dependencies:**
  - `psutil` (for system and process monitoring)
  - `requests` (for sending Discord webhook notifications)

## Installation

1. Clone or download the repository containing `deamon_core.py`.
2. Install the required Python libraries:

```bash
pip install psutil requests
```

## Configuration

Before running the daemon, you can customize the thresholds and targets directly at the top of `deamon_core.py`:

```python
RAM_THRESHOLD = 75.0  # RAM usage percentage that triggers the cleanup
TARGET_HOGS = ['chrome.exe', 'spotify.exe', 'python.exe']  # Processes eligible for termination
WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"  # Discord Webhook URL for alerts
```

> **Security Note:** Be sure to keep your `WEBHOOK_URL` private and avoid committing live webhook URLs to public repositories. Consider using environment variables for production use.

Additionally, inside `check_ram_vitals()`, the daemon requires a target process to be consuming at least **150.0 MB** of Virtual Memory (`proc_vms_mb > 150.0`) before it is eligible for termination.

## Usage

Run the script from your terminal or command prompt:

```bash
python deamon_core.py
```

*Note: Depending on the processes you are targeting, you may need to run your terminal as an **Administrator** (Windows) or with **`sudo`** (Linux/macOS) to avoid `AccessDenied` errors when terminating high-privilege processes.*

To stop the daemon gracefully, press `Ctrl+C` in the terminal.

## Logging

All activity is recorded in `system.log` in the same directory. 

**Example Log Output:**
```text
2026-06-23 13:15:03,912 - INFO - System Stable: RAM at 73.7%
2026-06-23 13:15:08,915 - WARNING - Critical resource Strain: RAM at 75.1%
2026-06-23 13:15:09,745 - WARNING - culprit is found
2026-06-23 13:15:09,746 - WARNING - the heaviest memory user is python.exe (PID 16528 at 0.1%)
2026-06-23 13:15:09,746 - WARNING - ACTION TAKEN: Terminated python.exe to free up RAM.
```

## Project Structure

- `deamon_core.py` - Main script containing the monitoring loop, process killer, and Discord alert logic.
- `system.log` - Auto-generated rotating log file tracking system RAM metrics and daemon actions.