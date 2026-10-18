"""Self-authored work sample: keep the old JSON file if a save fails.

Python 3.10+, standard library only. This is a demonstration, not client work.
"""

import json
import os
from pathlib import Path
import stat
import tempfile


def save_json(path, value):
    """Replace an existing regular file, or create one, after a complete write.

    Parent directory must exist. Existing symlinks are rejected. Concurrent
    writers are not coordinated; the last successful replace wins.
    """
    destination = Path(path)
    try:
        info = destination.lstat()
    except FileNotFoundError:
        mode = 0o600
    else:
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("destination must be a regular file")
        mode = stat.S_IMODE(info.st_mode) & 0o777

    # Serialize first: an invalid value cannot truncate the old file.
    payload = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", delete=False,
            dir=destination.parent, prefix=f".{destination.name}.", suffix=".tmp",
        ) as stream:
            temporary = Path(stream.name)
            os.fchmod(stream.fileno(), mode)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
