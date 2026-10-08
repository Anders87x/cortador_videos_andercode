import json
import threading
from datetime import datetime, timezone
from pathlib import Path


_log_lock = threading.Lock()


def append_render_log(log_file, **record):
    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **record,
    }

    try:
        with _log_lock:
            with path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError:
        return False

    return True
