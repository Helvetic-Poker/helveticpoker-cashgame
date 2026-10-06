from pathlib import Path
from html import escape
from urllib.parse import urlparse
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "public"
BASE = "https://cashgame.helveticpoker.ch"
LOGO = "https://pokerturniere.helveticpoker.ch/assets/helvetic-poker-logo.png?v=7"
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
    # Verified logo assets / official site favicons only. Do not use unrelated
    # sponsor, voucher-shop or logo-aggregator images as casino logos.
    "casino-baden": "https://www.grandcasinobaden.ch/favicon.ico",
    "casino-bad-ragaz": "https://www.casinoragaz.ch/favicon.ico",
    "casino-basel": "https://media.jobs.ch/media/cfcf4c22-f90e-4525-a202-85ed807c5e53",
    "casino-bern": "https://media.jobs.ch/images/a9efa51a-1c0e-4e26-94b7-018547a987b9/3379x1734.png",
    "casino-courrendlin": "https://www.casinosbarriere.com/favicon.ico",
    "casino-crans-montana": "https://www.casino-crans-montana.ch/favicon.ico",
    "casino-davos": "https://www.casinodavos.ch/wp-content/uploads/2025/03/cda-logo-circle-2-150x150.jpg",
    "casino-granges-paccot": "https://www.casinosbarriere.com/favicon.ico",
    "casino-interlaken": "https://www.casino-interlaken.ch/favicon.ico",
    "casino-locarno": "https://www.casinolocarno.ch/favicon.ico",
    "casino-lugano": "https://www.casinolugano.ch/favicon.ico",
    "casino-luzern": "https://www.lucerne-business.com/company/logo/Grand%20Casino%20Luzern%20AG.png",
    "casino-mendrisio": "https://www.admiral.ch/favicon.ico",
    "casino-meyrin": "https://www.pasino.ch/favicon.ico",
    "casino-montreux": "https://www.casinosbarriere.com/favicon.ico",
    "casino-neuenburg": "https://www.casino-neuchatel.ch/favicon.ico",
    "casino-pfaeffikon": "https://www.swisscasinos.ch/favicon.ico",
    "casino-prilly": "https://grandcasinoprilly.com/wp-content/uploads/2026/09/Grand-casino-prilly-logo-scaled.png",
    "casino-st-gallen": "https://www.swisscasinos.ch/favicon.ico",
    "casino-winterthur": "https://www.swisscasinos.ch/sites/default/files/2025-10/Swiss_Casino_Casino_Winterthur_1farbig_black_zentriert.png",
    "casino-zuerich": "https://www.swisscasinos.ch/favicon.ico",
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
@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap");\nhtml{{font-family:Montserrat,Arial,sans-serif}}body{{font-family:Montserrat,Arial,sans-serif;-webkit-font-smoothing:antialiased;text-rendering:geometricPrecision}}\n:root{{--nav:#0c1b27;--nav2:#143244;--red:#e21b35;--red2:#ff4055;--ink:#13263a;--muted:#6f7c8b;--line:#dfe5ea;--bg:#f3f5f7;--green:#16884b;--max:1180px}}\nbody{{margin:0;background:var(--bg);color:var(--ink);font-family:Montserrat,system-ui,sans-serif}}
a{{color:inherit}}
.top{{height:4px;background:var(--red)}}\nheader{{height:88px;background:linear-gradient(100deg,var(--nav),var(--nav2));color:#fff;position:sticky;top:0;z-index:20;box-shadow:0 2px 8px #00101825}}
.nav{{max-width:1180px;height:100%;margin:auto;padding:0 18px;display:flex;align-items:center;gap:28px}}
.brand{{display:flex;align-items:center;text-decoration:none;min-width:92px}}
.brandLogo{{display:block;width:82px;height:82px;object-fit:contain;background:transparent;border:0;border-radius:0;padding:0}}
.links{{display:flex;gap:29px;margin-left:auto;font-size:15px;font-weight:300;letter-spacing:-.015em;text-transform:uppercase}}
.links a{{text-decoration:none;opacity:.94}}
.links a.active{{position:relative}}
.links a.active:after{{content:"";position:absolute;left:0;right:0;bottom:-23px;height:3px;background:#ff4055;border-radius:3px}}
.menuBtn{{display:none;margin-left:auto;width:44px;height:44px;border:1px solid #ffffff35;border-radius:9px;background:#ffffff10;color:#fff;font-size:25px;line-height:1;cursor:pointer}}
main{{max-width:1120px;margin:auto;padding:26px 18px 55px}}
.crumb{{font-size:13px;color:#687580;margin-bottom:14px}}
.hero{{color:#13263a;background:#fff;border:1px solid #dfe5ea;border-radius:16px;padding:30px;box-shadow:0 8px 24px #10223810}}
h1{{margin:0;font-size:clamp(38px,6vw,60px);line-height:1;margin:0 0 9px;letter-spacing:-.045em;font-weight:600}}
h2{{font-size:25px;margin:30px 0 12px}}
.lead{{color:#5e6b78;font-size:17px;max-width:850px;margin:14px 0 0}}
.stats{{display:flex;gap:8px;margin-top:18px;flex-wrap:wrap}}
.stat{{padding:9px 12px;border:1px solid #e0e5ea;border-radius:10px;background:#fafbfc}}
.stat strong{{display:block;font-size:19px}}
.stat span{{font-size:11px;color:#6c7884}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:14px}}
.card{{background:#fff;border:1px solid #dfe5ea;border-radius:14px;overflow:hidden;box-shadow:0 3px 12px #10223808}}
.card-top{{display:flex;align-items:center;gap:14px;padding:15px 15px 10px}}
.provider-logo{{width:58px;height:58px;min-width:58px;box-sizing:border-box;display:block;border-radius:10px;object-fit:contain;object-position:center;border:1px solid #e3e8ed;background:#fff;padding:7px}}
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
.casino-card .provider-logo{{width:58px;height:58px;min-width:58px}}
.notice{{background:#fff;border:1px solid #dfe5ea;border-radius:14px;padding:20px;margin-top:14px}}
footer{{max-width:1180px;margin:auto;padding:25px 18px;color:#71808d;font-size:13px}}
@media(max-width:1100px){{.links{{display:none}}.menuBtn{{display:block}}}}
@media(max-width:850px){{.grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(max-width:720px){{
header{{height:64px}}.nav{{padding:0 12px;gap:12px}}.menuBtn{{display:block}}
.links.open{{display:flex;position:absolute;top:64px;left:10px;right:10px;margin:0;padding:8px;background:#102b3b;border:1px solid #ffffff18;border-radius:0 0 12px 12px;box-shadow:0 8px 18px #00101830;flex-direction:column;gap:0;z-index:30}}
.links.open a{{padding:14px 12px;font-size:13px;border-bottom:1px solid #ffffff12}}.links.open a:last-child{{border-bottom:0}}.links.open a.active:after{{display:none}}
.brandLogo{{width:58px;height:58px}}main{{padding:20px 10px}}.hero{{padding:24px 20px}}.grid{{grid-template-columns:1fr}}
}}
</style>
</head>
<body>
<div class="top"></div><header><div class="nav"><a class="brand" href="https://www.helveticpoker.ch/" target="_blank" rel="noopener"><img class="brandLogo" src="{LOGO}" alt="Helvetic Poker"></a><button class="menuBtn" id="menuBtn" aria-label="Menü öffnen" aria-expanded="false">☰</button><nav class="links" id="mobileNav"><a href="https://www.helveticpoker.ch/blog" target="_blank" rel="noopener">News</a><a href="{TOURNAMENTS}">Pokerturniere</a><a class="active" href="{BASE}/">Cash Games</a><a href="https://www.helveticpoker.ch/pokerclubs-schweiz" target="_blank" rel="noopener">Poker Rooms Schweiz</a><a href="https://www.helveticpoker.ch/anbieter" target="_blank" rel="noopener">Online-Anbieter</a><a href="https://www.helveticpoker.ch/recht-sicherheit" target="_blank" rel="noopener">Recht &amp; Sicherheit</a></nav></div></header>
<main>{body}</main>
<footer>Helvetic Poker · <a href="{TOURNAMENTS}" style="color:inherit">Pokerturniere Schweiz</a> · <a href="{BASE}/" style="color:inherit">Cash Games Schweiz</a> · Offizielle Quellen · tägliche Quellenprüfung.</footer>
<script>const menuBtn=document.getElementById("menuBtn"),mobileNav=document.getElementById("mobileNav");if(menuBtn&&mobileNav){{menuBtn.onclick=()=>{{const open=mobileNav.classList.toggle("open");menuBtn.setAttribute("aria-expanded",open?"true":"false");menuBtn.textContent=open?"×":"☰"}};mobileNav.querySelectorAll("a").forEach(a=>a.addEventListener("click",()=>{{mobileNav.classList.remove("open");menuBtn.setAttribute("aria-expanded","false");menuBtn.textContent="☰"}}));}}</script>
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
