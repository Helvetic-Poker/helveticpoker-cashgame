from pathlib import Path
from html import escape
from urllib.parse import urlparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "public"
BASE = "https://cashgame.helveticpoker.ch"
LOGO = f"{BASE}/assets/helvetic-poker-logo.png"
TOURNAMENTS = "https://pokerturniere.helveticpoker.ch/"

sources = json.loads((DATA / "cashgames-sources.json").read_text(encoding="utf-8"))
games = json.loads((DATA / "cashgames.json").read_text(encoding="utf-8"))

confirmed = [g for g in games if g.get("status") == "confirmed"]
paused = [g for g in games if g.get("status") == "paused"]

def money(v):
    return "—" if v is None else f"CHF {v:,}".replace(",", "'")

def domain(url):
    return (urlparse(url).hostname or "").removeprefix("www.")

PROVIDER_LOGOS = {
    "casino-luzern": "https://hrfestival.ch/wp-content/uploads/2025/11/logo_gcl_schwarz_gold_rgb.png",
    "casino-granges-paccot": "https://jeux-gratuits-fr.casino/wp-content/uploads/2020/05/casino-barriere-fribourg-logo.jpg",
    "casino-courrendlin": "https://cadeaux.lqj.ch/cdn/shop/files/Casino_26d56023-2212-45be-bb5c-22b836771d4e.jpg?v=1763623753",
    "casino-lugano": "https://cdn.freebiesupply.com/logos/large/2x/casino-lugano-logo-png-transparent.png",
    "casino-mendrisio": "https://hcap.ch/uploads/sponsor/Logo_Admiral_Mendrisio_50_x_20_cm-1.png",
}

def favicon(url):
    host = domain(url)
    return f"https://www.google.com/s2/favicons?domain={host}&sz=128" if host else ""

def provider_logo(provider_id, source_url):
    return PROVIDER_LOGOS.get(provider_id) or favicon(source_url)

def initials(name):
    words = [w for w in re.findall(r"[A-Za-zÄÖÜäöüÀ-ÿ0-9]+", name) if w.lower() not in {"grand", "casino", "swiss"}]
    return "".join(w[0] for w in words[:2]).upper() or "CG"

def shell(title, description, body, canonical):
    return f"""<!doctype html>
<html lang="de-CH">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{escape(canonical)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{escape(canonical)}">
<meta property="og:site_name" content="Helvetic Poker">
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#f4f6f8;color:#13263a;font-family:Arial,Helvetica,sans-serif}}
a{{color:inherit}}
header{{background:#0c1b27;border-top:4px solid #e21b35}}
.nav{{max-width:1120px;margin:auto;padding:12px 18px;display:flex;justify-content:space-between;align-items:center;gap:20px}}
.logo{{width:205px;max-height:55px;object-fit:contain;object-position:left}}
.links{{display:flex;gap:18px;font-size:13px;font-weight:700;color:#fff}}
.links a{{text-decoration:none}}
main{{max-width:1120px;margin:auto;padding:26px 18px 55px}}
.crumb{{font-size:13px;color:#687580;margin-bottom:14px}}
.hero{{background:#fff;border:1px solid #dfe5ea;border-radius:16px;padding:30px;box-shadow:0 8px 24px #10223810}}
h1{{margin:0;font-size:clamp(34px,5vw,52px);line-height:1.05}}
h2{{font-size:25px;margin:30px 0 12px}}
.lead{{color:#5e6b78;font-size:17px;max-width:850px;margin:14px 0 0}}
.stats{{display:flex;gap:8px;margin-top:18px;flex-wrap:wrap}}
.stat{{padding:9px 12px;border:1px solid #e0e5ea;border-radius:10px;background:#fafbfc}}
.stat strong{{display:block;font-size:19px}}
.stat span{{font-size:11px;color:#6c7884}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:14px}}
.card{{background:#fff;border:1px solid #dfe5ea;border-radius:14px;overflow:hidden;box-shadow:0 3px 12px #10223808}}
.card-top{{display:flex;align-items:center;gap:12px;padding:15px 15px 10px}}
.provider-logo{{width:46px;height:46px;border-radius:10px;object-fit:contain;border:1px solid #e3e8ed;background:#fff;padding:5px}}
.provider-logo-fallback{{display:flex;align-items:center;justify-content:center;background:#f0f2f5;color:#26394a;font-size:13px;font-weight:800}}
.provider-name{{font-size:13px;font-weight:800;line-height:1.2}}
.provider-city{{font-size:11px;color:#71808d;margin-top:3px}}
.card-body{{padding:4px 15px 16px}}
.card h3{{margin:0;font-size:22px;line-height:1.1}}
.stakes{{color:#5f6d79;font-size:13px;margin-top:4px;font-weight:700}}
.detail-grid{{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:13px}}
.detail{{border-radius:9px;background:#f7f9fa;padding:9px}}
.detail-label{{font-size:10px;color:#788590;text-transform:uppercase;letter-spacing:.04em}}
.detail-value{{font-size:13px;font-weight:800;margin-top:3px}}
.schedule{{margin-top:9px;padding:10px;border-left:3px solid #e21b35;background:#faf7f8;border-radius:7px;font-size:12px;line-height:1.45}}
.pill{{display:inline-block;border-radius:999px;padding:5px 9px;background:#eaf5ed;font-size:11px;font-weight:800;margin-top:12px}}
a.source{{display:inline-block;margin-top:10px;color:#d21935;font-weight:800;text-decoration:none;font-size:12px}}
.casino-card{{display:flex;align-items:center;gap:13px;padding:15px}}
.casino-card .provider-logo{{width:42px;height:42px}}
.notice{{background:#fff;border:1px solid #dfe5ea;border-radius:14px;padding:20px;margin-top:14px}}
footer{{max-width:1120px;margin:auto;padding:25px 18px;color:#71808d;font-size:13px}}
@media(max-width:850px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(max-width:650px){{.links{{display:none}}main{{padding:20px 10px}}.hero{{padding:24px 20px}}.grid{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<header><div class="nav"><a href="{BASE}/"><img class="logo" src="{LOGO}" alt="Helvetic Poker"></a><nav class="links"><a href="{BASE}/">Cash Games</a><a href="{TOURNAMENTS}">Pokerturniere</a><a href="{BASE}/#casinos">Casinos</a></nav></div></header>
<main>{body}</main>
<footer>Helvetic Poker · <a href="{TOURNAMENTS}" style="color:inherit">Pokerturniere Schweiz</a> · <a href="{BASE}/" style="color:inherit">Cash Games Schweiz</a> · Offizielle Quellen · tägliche Quellenprüfung.</footer>
</body></html>"""

def logo_img(name, source_url, provider_id=None, cls="provider-logo"):
    return f'<img class="{cls}" src="{escape(provider_logo(provider_id, source_url))}" alt="{escape(name)} Logo" loading="lazy">'

def provider_by_id(provider_id):
    return next((s for s in sources if s["id"] == provider_id), None)

def schedule_html(g):
    schedule = str(g.get("schedule") or "—")
    return f'<div class="schedule"><strong>Spielzeit</strong><br>{escape(schedule)}</div>'

def card(g):
    s = provider_by_id(g.get("provider_id"))
    provider = g.get("provider") or (s["name"] if s else "")
    city = g.get("city") or (s["city"] if s else "")
    canton = g.get("canton") or (s["canton"] if s else "")
    buy = "—"
    if g.get("buy_in_note"):
        buy = g.get("buy_in_note")
    elif g.get("min_buy_in") is not None or g.get("max_buy_in") is not None:
        buy = f"{money(g.get('min_buy_in'))} – {money(g.get('max_buy_in'))}"
    source_url = g.get("source_url") or (s["source_url"] if s else BASE)
    return f"""<article class="card">
<div class="card-top">{logo_img(provider, source_url, s.get("id") if s else g.get("provider_id"))}<div><div class="provider-name">{escape(provider)}</div><div class="provider-city">{escape(city)} · {escape(canton)}</div></div></div>
<div class="card-body">
<h3>{escape(g.get("variant",""))} <span class="stakes">{escape(g.get("stakes",""))}</span></h3>
<div class="detail-grid"><div class="detail"><div class="detail-label">Buy-in</div><div class="detail-value">{escape(buy)}</div></div><div class="detail"><div class="detail-label">Status</div><div class="detail-value">Bestätigt</div></div></div>
{schedule_html(g)}
<a class="source" href="{escape(source_url)}" rel="noopener" target="_blank">Offizielle Quelle →</a>
</div></article>"""

def casino_card(s):
    return f"""<a class="card casino-card" href="{BASE}/anbieter/{escape(s["id"])}/">
{logo_img(s["name"], s["source_url"], s["id"])}
<div><div class="provider-name">{escape(s["name"])}</div><div class="provider-city">{escape(s["city"])} · {escape(s["canton"])}</div></div>
</a>"""

OUT.mkdir(exist_ok=True)
# Keep the Search Console verification file in the published root.
verification_file = ROOT / "google7842e2a0234e258b.html"
if verification_file.exists():
    (OUT / verification_file.name).write_text(verification_file.read_text(encoding="utf-8"), encoding="utf-8")
(OUT / "index.html").write_text(shell(
    "Cash Games Schweiz | Helvetic Poker",
    "Aktuelle Poker-Cash-Games in Schweizer Casinos mit Limits, Buy-ins, Spielzeiten und offiziellen Quellen.",
    f"""<div class="crumb">Helvetic Poker › Cash Games Schweiz</div>
<section class="hero"><h1>Cash Games Schweiz</h1>
<p class="lead">Aktuelle Poker-Cash-Games in Schweizer Casinos – getrennt vom Turnierkalender.</p>
<div class="stats"><div class="stat"><strong>{len(confirmed)}</strong><span>bestätigte Angebote</span></div><div class="stat"><strong>{len(paused)}</strong><span>pausierte Angebote</span></div><div class="stat"><strong>{len(sources)}</strong><span>geprüfte Anbieter</span></div></div></section>
<h2>Aktuelle Cash Games</h2>
<div class="grid">{''.join(card(g) for g in confirmed)}</div>
<h2 id="casinos">Schweizer Casinos</h2>
<div class="grid">{''.join(casino_card(s) for s in sources)}</div>""",
    BASE + "/"
), encoding="utf-8")

for s in sources:
    sgames = [g for g in games if g.get("provider_id") == s["id"] and g.get("status") == "confirmed"]
    body = f"""<div class="crumb"><a href="{BASE}/">Cash Games Schweiz</a> › {escape(s["name"])}</div>
<section class="hero"><div class="card-top" style="padding:0 0 14px">{logo_img(s["name"], s["source_url"], s["id"])}<div><h1 style="font-size:clamp(30px,4vw,46px)">{escape(s["name"])}</h1><p class="lead">{escape(s["city"])} · Kanton {escape(s["canton"])}</p></div></div>
<a class="source" href="{escape(s["source_url"])}" rel="noopener" target="_blank">Offizielle Website →</a></section>"""
    if sgames:
        body += '<h2>Bestätigte Cash Games</h2><div class="grid">' + ''.join(card(g) for g in sgames) + '</div>'
    else:
        body += '<div class="notice"><strong>Aktuell keine bestätigten Cash-Game-Daten.</strong><p>Die offizielle Quelle wird täglich geprüft. Nicht bestätigte Informationen werden bewusst nicht als aktiv dargestellt.</p></div>'
    path = OUT / "anbieter" / s["id"] / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(shell(f'Cash Games {s["name"]} | Helvetic Poker', f'Cash-Game-Informationen für {s["name"]} in {s["city"]}.', body, f'{BASE}/anbieter/{s["id"]}/'), encoding="utf-8")

print(f"Generated homepage and {len(sources)} provider pages.")
