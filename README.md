# Awaken

CLI/TUI utility that simulates light user activity (cursor moves and key presses) after a period of inactivity. **Use only where policy and law allow** — bypassing workplace presence or idle tracking can violate rules or contracts; you are responsible for compliance.

## Prerequisites

- [Python 3.12.x](https://www.python.org/downloads/release/python-3120/)
- [Poetry](https://python-poetry.org/docs/#installation)

## Installation

```bash
git clone https://github.com/just-better-code/awaken.git
cd awaken
poetry install
```

## Running

```bash
poetry run awaken
```

CLI flags set the **initial** values; in the TUI you can edit **idle**, **delay**, **dist**, **speed**, **random**, and **wheel** (integer: per wake, scroll **down** then **up** by that many PyAutoGUI clicks total; **0** turns it off, default **10**) in the text fields, and choose **key** from a combo (Space or Enter opens the list). Wheel bursts are split into uneven chunks and paced with pauses between them: **speed** scales those pauses (like cursor motion), and **random** picks separate easing curves for chunk sizes and for inter-click rhythm, plus occasional jitter—same spirit as the mouse path. **Session idle** is the running sum of completed user-idle gaps (between listener-detected input). **Stay-awake** is one read-only text line: **standby** until user-idle reaches the **idle** threshold, then **armed** (user idle ≥ that value), then briefly **emitting** during a wake (cursor / key / wheel). When **real** keyboard/mouse input arrives and the user-idle interval before it is **≥ delay** (same **delay** as system-idle threshold), a line is added to **Log** with that interval and the session total (synthetic input is filtered out). The **Log** row is at the **bottom** (below **Quit**): one read-only text field showing the last **5** messages joined with **·** (oldest dropped from the buffer); long text is truncated with a leading **…**. Changes apply automatically a few times per second once every field is valid. Invalid input keeps the previous settings.

### Exiting the TUI

- **Esc**: exit from almost any focused control (same clean shutdown as **Quit**).
- **Quit**: press **Tab** until the **` Quit `** button is highlighted, then **Enter**.
- **Ctrl+C** in the terminal also stops the process (less clean than Quit, but works).

Equivalent:

```bash
poetry run python -m awaken.main
```

### CLI options

| Option | Description |
|--------|-------------|
| `--idle` | Seconds without **user** input before actions (default: 60) |
| `--delay` | Seconds without **system** idle signal in legacy/fallback mode (default: 30) |
| `--key` | Key to press (default: `shift`) |
| `--dist` | Cursor move distance in pixels per axis (default: 500) |
| `--speed` | Move speed scale — higher is faster per segment (default: 10) |
| `--random` | Probability `0..1` of using a random easing curve vs linear (default: 0.5) |
| `--wheel-clicks N` | Wheel **down** then **up** by **N** clicks each way, chunked by **random** (easing) like the cursor (`0` = off, default: `10`) |

## PyAutoGUI failsafe

By default, moving the mouse to a **screen corner** can trigger PyAutoGUI’s failsafe and raise an exception. See the [PyAutoGUI docs](https://pyautogui.readthedocs.io/) for behavior and how to adjust `FAILSAFE` / `PAUSE` if needed.

## Platform notes

Idle detection tries monitors in order: **Windows** → **GNOME (Mutter) Wayland** → **KDE Plasma Wayland** (`org.kde.KIdleTime` on session D-Bus) → **X11** → **macOS**. If none apply, the app falls back to listener-based timing. Compositors without these APIs (e.g. some minimal wlroots setups) may only get accurate idle from the fallback.

## Development

```bash
poetry install
poetry run pytest
poetry run ruff check awaken tests
poetry run ruff format --check awaken tests
```

## Troubleshooting

- Confirm Python 3.12: `python --version` / `poetry env use 3.12`
- Reinstall deps: `poetry install`
- On Linux display servers, ensure input monitoring / X11 extensions match your session (X11 vs Wayland).
