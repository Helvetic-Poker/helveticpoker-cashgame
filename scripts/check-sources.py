from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sources = json.loads((ROOT / "data/cashgames-sources.json").read_text(encoding="utf-8"))

results = []
for s in sources:
    item = {"id": s["id"], "name": s["name"], "url": s["source_url"], "ok": False, "status": None, "sha256": None, "error": None}
    try:
        req = urllib.request.Request(s["source_url"], headers={"User-Agent": "HelveticPoker-CashGameChecker/1.0"})
        with urllib.request.urlopen(req, timeout=25) as r:
            content = r.read()
            item["status"] = getattr(r, "status", 200)
            item["ok"] = 200 <= item["status"] < 400
            item["sha256"] = hashlib.sha256(content).hexdigest()
    except Exception as e:
        item["error"] = str(e)
    results.append(item)

ok = sum(1 for r in results if r["ok"])
payload = {
    "checked_at": datetime.now(timezone.utc).isoformat(),
    "expected_sources": len(sources),
    "reachable_sources": ok,
    "failed_sources": len(sources) - ok,
    "status": "ok" if ok == len(sources) else "failed_closed",
    "sources": results,
}
(ROOT / "data/source-status.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if ok != len(sources):
    raise SystemExit(f"FAIL-CLOSED: {ok}/{len(sources)} official sources reachable; existing cash-game data remains unchanged.")
print(f"OK: {ok}/{len(sources)} official sources reachable.")
