import json
from datetime import datetime, timezone
from pathlib import Path


def append_render_log(log_file, **record):
    path = Path(log_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **record,
    }

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False) + "\n")
