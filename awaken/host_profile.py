"""Best-effort host / session hints for UI (not used for security decisions)."""

from __future__ import annotations

import os
import platform
import sys


def describe_host_lines() -> list[str]:
    """Short lines for TUI: OS, arch, session hints (Linux XDG, etc.)."""
    lines = [
        f"{platform.system()} {platform.release()} · {platform.machine()}",
    ]
    if sys.platform == "linux":
        st = os.getenv("XDG_SESSION_TYPE") or "(unset)"
        desk = os.getenv("XDG_CURRENT_DESKTOP") or "(unset)"
        sess = os.getenv("DESKTOP_SESSION") or "(unset)"
        lines.append(f"XDG_SESSION_TYPE={st}")
        lines.append(f"XDG_CURRENT_DESKTOP={desk}")
        lines.append(f"DESKTOP_SESSION={sess}")
    elif sys.platform == "darwin":
        lines.append("Session: macOS (Darwin)")
    elif sys.platform == "win32":
        lines.append("Session: Windows")
    else:
        lines.append(f"sys.platform={sys.platform}")
    return lines
