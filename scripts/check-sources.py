from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sources = json.loads((ROOT / "data/cashgames-sources.json").read_text(encoding="utf-8"))

MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 3
TIMEOUT_SECONDS = 25

results = []
for s in sources:
    item = {
        "id": s["id"],
        "name": s["name"],
        "url": s["source_url"],
        "ok": False,
        "status": None,
        "sha256": None,
        "error": None,
        "attempts": 0,
    }

    for attempt in range(1, MAX_ATTEMPTS + 1):
        item["attempts"] = attempt
        try:
            req = urllib.request.Request(
                s["source_url"],
                headers={"User-Agent": "HelveticPoker-CashGameChecker/1.1"},
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as r:
                content = r.read()
                item["status"] = getattr(r, "status", 200)
                item["ok"] = 200 <= item["status"] < 400
                item["sha256"] = hashlib.sha256(content).hexdigest()
                item["error"] = None
                break
        except Exception as e:
            item["error"] = str(e)
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)

    item["status_label"] = "reachable" if item["ok"] else "unreachable"
    results.append(item)

ok = sum(1 for r in results if r["ok"])
payload = {
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "expected_sources": len(sources),
    "reachable_sources": ok,
    "failed_sources": len(sources) - ok,
    "status": "ok" if ok == len(sources) else "partial",
    "sources": results,
}
(ROOT / "data/source-status.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

if ok != len(sources):
    failed = ", ".join(r["name"] for r in results if not r["ok"])
    print(f"WARNING: {ok}/{len(sources)} official sources reachable after retries.")
    print(f"Unreachable: {failed}")
else:
    print(f"OK: {ok}/{len(sources)} official sources reachable after retries.")
