from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "public"
BASE = "https://cashgame.helveticpoker.ch"

sources = json.loads((DATA / "cashgames-sources.json").read_text(encoding="utf-8"))
games = json.loads((DATA / "cashgames.json").read_text(encoding="utf-8"))

confirmed = [g for g in games if g.get("status") == "confirmed"]
paused = [g for g in games if g.get("status") == "paused"]

def money(v):
    return "—" if v is None else f"CHF {v:,}".replace(",", "'")

def shell(title, description, body, canonical):
    return f"""<!doctype html>
<html lang="de-CH">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{escape(canonical)}">
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f6f8;color:#172331;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
header{{background:#101b25;color:#fff}}nav{{max-width:1160px;margin:auto;padding:16px 20px;font-weight:700}}nav a{{color:#fff;text-decoration:none}}
main{{max-width:1160px;margin:auto;padding:28px 18px 60px}}h1{{font-size:clamp(32px,5vw,54px);margin:0 0 10px}}h2{{margin-top:34px}}
.hero,.card,.notice{{background:#fff;border:1px solid #dce3e9;border-radius:16px;padding:22px;box-shadow:0 2px 10px rgba(0,0,0,.03)}}
.hero{{margin-bottom:16px}}.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}}
.meta{{color:#687685;font-size:14px;margin:7px 0 13px}}.pill{{display:inline-block;border-radius:999px;padding:5px 9px;background:#eaf5ed;font-size:12px;font-weight:700}}
.card h3{{margin:0;font-size:20px}}a.source{{display:inline-block;margin-top:14px;color:#bd1530;font-weight:700;text-decoration:none}}
table{{width:100%;border-collapse:collapse;background:#fff;border:1px solid #dce3e9;border-radius:14px;overflow:hidden}}
th,td{{padding:12px;text-align:left;border-bottom:1px solid #e8edf1;font-size:14px}}th{{background:#f7f9fa}}
footer{{max-width:1160px;margin:auto;padding:25px 18px;color:#71808d;font-size:13px}}
@media(max-width:800px){{.grid{{grid-template-columns:1fr}}table{{display:block;overflow:auto;white-space:nowrap}}}}
</style>
</head>
<body>
<header><nav><a href="{BASE}/">Helvetic Poker · Cash Games Schweiz</a></nav></header>
<main>{body}</main>
<footer>Offizielle Quellen · tägliche Quellenprüfung · Turniere und Cash Games werden getrennt geführt.</footer>
</body></html>"""

def card(g):
    buy = "—"
    if g.get("min_buy_in") is not None or g.get("max_buy_in") is not None:
        buy = f"{money(g.get('min_buy_in'))} – {money(g.get('max_buy_in'))}"
    return f"""<article class="card">
<h3>{escape(g.get("variant",""))} {escape(g.get("stakes",""))}</h3>
<div class="meta">{escape(g.get("schedule",""))} · Buy-in {escape(buy)}</div>
<span class="pill">Bestätigt</span>
<a class="source" href="{escape(g["source_url"])}" rel="noopener" target="_blank">Offizielle Quelle →</a>
</article>"""

OUT.mkdir(exist_ok=True)
(OUT / "index.html").write_text(shell(
    "Cash Games Schweiz | Helvetic Poker",
    "Aktuelle Cash Games in Schweizer Casinos: Varianten, Limits, Buy-ins und Spielzeiten.",
    f"""<section class="hero"><h1>Cash Games Schweiz</h1>
<p>Aktuelle Poker-Cash-Games in Schweizer Casinos – getrennt vom Turnierkalender.</p>
<p><strong>{len(confirmed)}</strong> bestätigte Angebote · <strong>{len(paused)}</strong> pausiertes Angebot · <strong>21</strong> geprüfte Anbieter</p></section>
<h2>Aktuelle Cash Games</h2>
<div class="grid">{''.join(card(g) for g in confirmed)}</div>
<h2>Schweizer Casinos</h2>
<div class="grid">{''.join(f'<article class="card"><h3>{escape(s["name"])}</h3><div class="meta">{escape(s["city"])} · {escape(s["canton"])}</div><a class="source" href="/anbieter/{escape(s["id"])}/">Cash-Game-Seite →</a></article>' for s in sources)}</div>""",
    BASE + "/"
), encoding="utf-8")

for s in sources:
    sgames = [g for g in games if g.get("provider_id") == s["id"] and g.get("status") == "confirmed"]
    body = f"""<section class="hero"><h1>{escape(s["name"])}</h1><p>{escape(s["city"])} · Kanton {escape(s["canton"])}</p>
<p><a class="source" href="{escape(s["source_url"])}" rel="noopener" target="_blank">Offizielle Website →</a></p></section>"""
    if sgames:
        body += '<h2>Bestätigte Cash Games</h2><div class="grid">' + ''.join(card(g) for g in sgames) + '</div>'
    else:
        body += '<div class="notice"><strong>Aktuell keine bestätigten Cash-Game-Daten.</strong><p>Die offizielle Quelle wird täglich geprüft. Ein nicht bestätigtes Angebot wird bewusst nicht als aktiv dargestellt.</p></div>'
    path = OUT / "anbieter" / s["id"] / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(shell(f'Cash Games {s["name"]} | Helvetic Poker', f'Cash-Game-Informationen für {s["name"]} in {s["city"]}.', body, f'{BASE}/anbieter/{s["id"]}/'), encoding="utf-8")

print(f"Generated homepage and {len(sources)} provider pages.")
