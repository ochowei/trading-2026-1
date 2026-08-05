"""Secure file publication and bounded locking for local ledger persistence."""

from __future__ import annotations

import fcntl
import os
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class FileLockTimeout(TimeoutError):
    """A bounded file lock could not be acquired."""


@contextmanager
def locked_file(path: Path, timeout_seconds: float) -> Iterator[None]:
    """Hold an exclusive advisory lock for a bounded interval."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    deadline = time.monotonic() + timeout_seconds
    try:
        while True:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise FileLockTimeout(f"timed out waiting for file lock: {path}") from None
                time.sleep(0.05)
        yield
    finally:
        fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def atomic_write(path: Path, content: bytes, *, replace: bool) -> None:
    """Publish private bytes atomically; non-replacing writes fail on collisions."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if replace:
            os.replace(temporary, path)
        else:
            os.link(temporary, path)
            temporary.unlink(missing_ok=True)
        os.chmod(path, 0o600)
    finally:
        temporary.unlink(missing_ok=True)
