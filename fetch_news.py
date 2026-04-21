#!/usr/bin/env python3
import os, json, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

API_KEY = os.environ.get("NEWS_API_KEY", "")
PST     = timezone(timedelta(hours=-8))
TODAY   = datetime.now(PST).strftime("%B %d, %Y")

IMAGES = {
    "tech":    ["https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&q=80","https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=800&q=80","https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800&q=80"],
    "stocks":  ["https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80","https://images.unsplash.com/photo-1559526324-593bc073d938?w=800&q=80","https://images.unsplash.com/photo-1640340434855-6084b1f4901c?w=800&q=80"],
    "geo":     ["https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=800&q=80","https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=800&q=80","https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=800&q=80"],
    "fashion": ["https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=800&q=80","https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&q=80","https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80"],
}
SMALL_IMAGES = {
    "tech":    ["https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&q=80","https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600&q=80"],
    "stocks":  ["https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&q=80","https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&q=80"],
    "geo":     ["https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=600&q=80","https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=600&q=80"],
    "fashion": ["https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=600&q=80","https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=600&q=80"],
}
QUERIES = {
    "tech":    {"q":"artificial intelligence OR technology","language":"en","sortBy":"publishedAt","pageSize":"3"},
    "stocks":  {"q":"stock market OR economy OR finance","language":"en","sortBy":"publishedAt","pageSize":"3"},
    "geo":     {"q":"geopolitics OR world news OR war","language":"en","sortBy":"publishedAt","pageSize":"3"},
    "fashion": {"q":"fashion OR style OR luxury","language":"en","sortBy":"publishedAt","pageSize":"3"},
}
FALLBACK = {
    "tech": [
        {"title":"AI race intensifies as major labs release competing models","description":"OpenAI, Google, and Anthropic are locked in fierce competition to define the next generation of AI.","url":"#","source":{"name":"TechCrunch"},"read_time":"4 min read"},
        {"title":"Big Tech doubles down on nuclear energy for AI data centers","description":"Microsoft, Google, and Amazon are signing long-term nuclear deals to power AI infrastructure.","url":"#","source":{"name":"Wired"},"read_time":"3 min read"},
        {"title":"Open-source AI models close gap with proprietary frontier systems","description":"Community-built models are now competitive on benchmarks previously dominated by closed labs.","url":"#","source":{"name":"The Verge"},"read_time":"3 min read"},
    ],
    "stocks": [
        {"title":"Markets volatile as tariff uncertainty rattles Wall Street","description":"Investors are watching Fed policy and trade developments as earnings season gets underway.","url":"#","source":{"name":"Bloomberg"},"read_time":"5 min read"},
        {"title":"Gold hits record high as investors seek safe haven assets","description":"The precious metal surged past $3,200 as global uncertainty drove demand for defensive positions.","url":"#","source":{"name":"Reuters"},"read_time":"3 min read"},
        {"title":"Tech stocks rebound as AI spending projections hold strong","description":"Analysts maintain bullish outlook on semiconductor and cloud infrastructure names into Q2.","url":"#","source":{"name":"WSJ"},"read_time":"4 min read"},
    ],
    "geo": [
        {"title":"G7 nations coordinate response to escalating trade tensions","description":"Foreign ministers met in emergency session to align strategy on economic coercion.","url":"#","source":{"name":"The Guardian"},"read_time":"5 min read"},
        {"title":"UN Security Council calls emergency session on Middle East situation","description":"Diplomats gathered as regional tensions continue to mount following a series of exchanges.","url":"#","source":{"name":"BBC News"},"read_time":"3 min read"},
        {"title":"European elections reshape political landscape across the continent","description":"Centrist parties face pressure from both left and right as voters signal frustration.","url":"#","source":{"name":"FT"},"read_time":"4 min read"},
    ],
    "fashion": [
        {"title":"Quiet luxury dominates runways as maximalism fades","description":"Designers across Paris, Milan, and New York embraced understated elegance this season.","url":"#","source":{"name":"Vogue"},"read_time":"4 min read"},
        {"title":"Gen Z reshapes luxury through circular fashion platforms","description":"Resale, rental, and repair are now mainstream as younger consumers redefine fashion ownership.","url":"#","source":{"name":"Harper's Bazaar"},"read_time":"3 min read"},
        {"title":"Luxury goods outperform traditional investments for third year","description":"Rare handbags, vintage watches, and limited sneakers deliver double-digit annual returns.","url":"#","source":{"name":"FT"},"read_time":"3 min read"},
    ],
}
READ_TIMES = ["2 min read","3 min read","4 min read","5 min read","6 min read"]

def fetch_articles(cat, params):
    if not API_KEY:
        return FALLBACK[cat]
    try:
        params["apiKey"] = API_KEY
        url = "https://newsapi.org/v2/everything?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent":"DailyDigest/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        articles = [a for a in data.get("articles",[]) if a.get("title") and a.get("description") and "[Removed]" not in a.get("title","")]
        result = []
        for i, a in enumerate(articles[:3]):
            result.append({"title":a["title"].split(" - ")[0][:120],"description":a["description"][:220],"url":a.get("url","#"),"source":a.get("source",{"name":"News"}),"read_time":READ_TIMES[i % len(READ_TIMES)]})
        return result if len(result) >= 2 else FALLBACK[cat]
    except Exception as e:
        print(f"API error for {cat}: {e}")
        return FALLBACK[cat]

def card_hero(art, img, badge_cls, badge_txt):
    src = art.get("source",{}).get("name","News")
    rt  = art.get("read_time","4 min read")
    url = art.get("url","#")
    tgt = 'target="_blank" rel="noopener"' if url != "#" else ""
    return f"""<article class="card-hero fi-card"><div class="iw"><img src="{img}" alt="{badge_txt}" loading="lazy"/><span class="bdg {badge_cls}">{badge_txt}</span></div><div class="cb"><div><div class="cmeta"><span class="src">{src}</span><span class="rt">⏱ {rt}</span></div><h3 class="ctitle">{art['title']}</h3><p class="cex">{art['description']}</p></div><div class="cfoot"><a href="{url}" class="rl" {tgt}>Read Article →</a><button class="sbtn" onclick="save(this)">🔖</button></div></div></article>"""

def card_small(art, img, badge_cls, badge_txt):
    src = art.get("source",{}).get("name","News")
    rt  = art.get("read_time","3 min read")
    url = art.get("url","#")
    tgt = 'target="_blank" rel="noopener"' if url != "#" else ""
    return f"""<article class="cs fi-card"><div class="iw"><img src="{img}" alt="{badge_txt}" loading="lazy"/><span class="bdg {badge_cls}">{badge_txt}</span></div><div class="cb"><div class="cmeta"><span class="src">{src}</span><span class="rt">⏱ {rt}</span></div><h3 class="ctitle">{art['title']}</h3><p class="cex">{art['description'][:160]}</p><div class="cfoot"><a href="{url}" class="rl" {tgt}>Read →</a><button class="sbtn" onclick="save(this)">🔖</button></div></div></article>"""

def ticker_items(all_articles):
    emojis = {"tech":"🤖","stocks":"📈","geo":"🌍","fashion":"✨"}
    items = ""
    for cat, arts in all_articles.items():
        for a in arts[:2]:
            t = a["title"][:80]
            items += f'<span class="ticker-item"><em>{emojis[cat]}</em>{t}</span>\n    '
    return items + items

def trending_html(all_articles):
    labels = {"tech":"AI & Tech","stocks":"Markets","geo":"Geopolitics","fashion":"Fashion"}
    html = ""
    n = 1
    for cat, arts in all_articles.items():
        for a in arts[:2]:
            html += f'<li class="ti"><span class="tnum">0{n}</span><div><div class="tcat">{labels[cat]}</div><div class="th">{a["title"][:70]}</div></div></li>'
            n += 1
            if n > 5: break
        if n > 5: break
    return html

def build_html(all_articles):
    tech=all_articles["tech"]; stocks=all_articles["stocks"]; geo=all_articles["geo"]; fashion=all_articles["fashion"]
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Daily Digest – {TODAY}</title>
  <meta name="description" content="Today's top stories in AI, Markets, Geopolitics and Fashion — updated every morning at 8am PST."/>
  <meta property="og:title" content="Daily Digest – {TODAY}"/>
  <meta property="og:description" content="Today's top stories in AI, Markets, Geopolitics and Fashion."/>
  <meta property="og:image" content="https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&q=80"/>
  <meta property="og:url" content="https://alonhaliva.github.io/daily-digest/"/>
  <meta property="og:type" content="website"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;600&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet"/>
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    :root{{--navy:#0d1117;--pink:#ff2d78;--violet:#7c3aed;--vl:#a78bfa;--bg:#f0f2f7;--sur:#fff;--sur2:#f8f9fc;--bdr:#e5e7eb;--tx:#0d1117;--tx2:#6b7280;--tx3:#9ca3af;--sh:0 4px 24px rgba(0,0,0,.07);--sh2:0 16px 48px rgba(0,0,0,.14)}}
    [data-theme=dark]{{--bg:#0a0d14;--sur:#131720;--sur2:#1a2030;--bdr:#252d3d;--tx:#e8eaf0;--tx2:#8892a4;--tx3:#4b5568;--sh:0 4px 24px rgba(0,0,0,.3);--sh2:0 16px 48px rgba(0,0,0,.5)}}
    html{{scroll-behavior:smooth}}
    body{{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--tx);min-height:100vh;transition:background .3s,color .3s}}
    #prog{{position:fixed;top:0;left:0;height:3px;background:linear-gradient(to right,var(--pink),var(--violet));width:0%;z-index:9999;pointer-events:none}}
    .ticker-wrap{{background:var(--navy);height:34px;display:flex;align-items:center;overflow:hidden}}
    [data-theme=dark] .ticker-wrap{{background:#0d0f17;border-bottom:1px solid var(--bdr)}}
    .ticker-label{{background:var(--pink);color:#fff;font-size:.66rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;padding:0 13px;height:100%;display:flex;align-items:center;white-space:nowrap;flex-shrink:0}}
    .ticker-track{{display:flex;animation:tick 55s linear infinite;white-space:nowrap}}
    .ticker-track:hover{{animation-play-state:paused}}
    .ticker-item{{color:#d1d5db;font-size:.73rem;padding:0 30px}}
    .ticker-item em{{color:var(--pink);font-style:normal;margin-right:6px}}
    @keyframes tick{{0%{{transform:translateX(0)}}100%{{transform:translateX(-50%)}}}}
    header{{background:var(--navy);padding:16px 24px;position:sticky;top:0;z-index:200;box-shadow:0 2px 20px rgba(0,0,0,.45)}}
    .hi{{max-width:1280px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:14px}}
    .logo{{display:inline-flex;align-items:center;gap:10px;text-decoration:none}}
    .logo-sq{{width:28px;height:28px;background:var(--pink);border-radius:6px;flex-shrink:0}}
    .logo-txt{{font-family:'Bebas Neue',sans-serif;font-size:1.9rem;letter-spacing:.06em;color:var(--pink);line-height:1}}
    .hr{{display:flex;align-items:center;gap:9px}}
    .tagline{{color:#9ca3af;font-size:.74rem;letter-spacing:.04em}}
    @media(max-width:580px){{.tagline{{display:none}}}}
    .btn-sub{{background:var(--pink);color:#fff;border:none;border-radius:999px;padding:7px 16px;font-family:'DM Sans',sans-serif;font-size:.78rem;font-weight:700;cursor:pointer;transition:opacity .18s,transform .18s}}
    .btn-sub:hover{{opacity:.88;transform:translateY(-1px)}}
    @media(max-width:400px){{.btn-sub{{display:none}}}}
    .btn-theme{{background:rgba(255,255,255,.08);border:1.5px solid rgba(255,255,255,.14);border-radius:50%;color:#fff;width:36px;height:36px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:.95rem;transition:background .2s,transform .25s;flex-shrink:0}}
    .btn-theme:hover{{background:rgba(255,255,255,.16);transform:rotate(22deg)}}
    .date-badge{{background:rgba(255,255,255,.1);color:#9ca3af;font-size:.7rem;padding:4px 10px;border-radius:999px;border:1px solid rgba(255,255,255,.12);white-space:nowrap}}
    @media(max-width:640px){{.date-badge{{display:none}}}}
    .fbar{{background:var(--sur);border-bottom:1px solid var(--bdr);padding:10px 24px;display:flex;align-items:center;gap:8px;overflow-x:auto;scrollbar-width:none;transition:background .3s}}
    .fbar::-webkit-scrollbar{{display:none}}
    .flbl{{font-weight:600;font-size:.77rem;color:var(--tx2);white-space:nowrap;margin-right:3px}}
    .pill{{display:inline-flex;align-items:center;gap:5px;padding:5px 14px;border-radius:999px;border:1.5px solid var(--bdr);background:transparent;font-family:'DM Sans',sans-serif;font-size:.78rem;font-weight:500;cursor:pointer;white-space:nowrap;transition:all .18s;color:var(--tx)}}
    .pill:hover{{border-color:var(--violet);color:var(--violet);transform:translateY(-1px)}}
    .pill.on{{background:var(--navy);border-color:var(--navy);color:#fff}}
    [data-theme=dark] .pill.on{{background:var(--pink);border-color:var(--pink)}}
    .wrap{{max-width:1280px;margin:0 auto;padding:30px 24px 80px;display:grid;grid-template-columns:1fr 296px;gap:34px;align-items:start}}
    @media(max-width:1024px){{.wrap{{grid-template-columns:1fr}}.sidebar{{display:none}}}}
    .sh{{display:flex;align-items:center;gap:11px;margin-bottom:16px}}
    .si{{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.25rem}}
    .si.tech{{background:linear-gradient(135deg,#6366f1,#8b5cf6)}}.si.mkt{{background:linear-gradient(135deg,#f59e0b,#ef4444)}}.si.geo{{background:linear-gradient(135deg,#10b981,#3b82f6)}}.si.fash{{background:linear-gradient(135deg,#f472b6,#a78bfa)}}
    .stitle{{font-family:'Bebas Neue',sans-serif;font-size:1.75rem;letter-spacing:.05em;color:var(--tx)}}
    .cgrid{{display:grid;gap:17px;margin-bottom:44px}}
    .crow{{display:grid;grid-template-columns:1fr 1fr;gap:17px}}
    @media(max-width:540px){{.crow{{grid-template-columns:1fr}}}}
    .card-hero{{display:grid;grid-template-columns:1fr 1fr;background:var(--sur);border-radius:18px;overflow:hidden;box-shadow:var(--sh);transition:transform .22s,box-shadow .22s;border:1px solid var(--bdr)}}
    .card-hero:hover{{transform:translateY(-4px);box-shadow:var(--sh2)}}
    @media(max-width:600px){{.card-hero{{grid-template-columns:1fr}}}}
    .iw{{position:relative;overflow:hidden}}
    .card-hero .iw{{min-height:280px}}
    @media(max-width:600px){{.card-hero .iw{{min-height:200px}}}}
    .cs .iw{{height:170px}}
    .iw img{{width:100%;height:100%;object-fit:cover;display:block;transition:transform .45s}}
    .card-hero:hover .iw img,.cs:hover .iw img{{transform:scale(1.05)}}
    .bdg{{position:absolute;top:12px;left:12px;color:#fff;font-size:.62rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:3px 9px;border-radius:5px}}
    .bdg.t{{background:var(--violet)}}.bdg.m{{background:#d97706}}.bdg.g{{background:#059669}}.bdg.f{{background:#db2777}}
    .cb{{padding:26px 26px 20px;display:flex;flex-direction:column;justify-content:space-between}}
    @media(max-width:600px){{.cb{{padding:16px}}}}
    .cs .cb{{padding:16px 18px 14px}}
    .cmeta{{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}}
    .src{{font-size:.64rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:var(--tx2)}}
    .rt{{font-size:.63rem;color:var(--tx3);background:var(--sur2);padding:2px 7px;border-radius:999px;border:1px solid var(--bdr)}}
    .ctitle{{font-family:'DM Serif Display',serif;font-size:1.32rem;line-height:1.28;color:var(--tx);margin-bottom:10px;transition:color .18s}}
    .card-hero:hover .ctitle,.cs:hover .ctitle{{color:var(--violet)}}
    [data-theme=dark] .card-hero:hover .ctitle,[data-theme=dark] .cs:hover .ctitle{{color:var(--vl)}}
    .cs .ctitle{{font-size:.98rem}}
    .cex{{font-size:.83rem;line-height:1.68;color:var(--tx2);flex-grow:1}}
    .cfoot{{display:flex;align-items:center;justify-content:space-between;margin-top:18px;padding-top:13px;border-top:1px solid var(--bdr)}}
    .rl{{display:inline-flex;align-items:center;gap:5px;color:var(--violet);font-weight:600;font-size:.8rem;text-decoration:none;transition:gap .18s}}
    [data-theme=dark] .rl{{color:var(--vl)}}
    .rl:hover{{gap:9px}}
    .sbtn{{background:none;border:1.5px solid var(--bdr);border-radius:7px;width:28px;height:28px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:.8rem;transition:all .18s;color:var(--tx2)}}
    .sbtn:hover{{border-color:var(--pink);color:var(--pink);transform:scale(1.1)}}
    .sbtn.saved{{background:var(--pink);border-color:var(--pink);color:#fff}}
    .cs{{background:var(--sur);border-radius:18px;overflow:hidden;box-shadow:var(--sh);display:flex;flex-direction:column;transition:transform .22s,box-shadow .22s;border:1px solid var(--bdr)}}
    .cs:hover{{transform:translateY(-4px);box-shadow:var(--sh2)}}
    .divider{{height:1px;background:linear-gradient(to right,transparent,var(--bdr),transparent);margin:0 0 38px}}
    .nlband{{background:linear-gradient(135deg,#0d1117,#1e1060);border-radius:20px;padding:36px 32px;text-align:center;margin-bottom:44px;position:relative;overflow:hidden}}
    .nlband::before{{content:'';position:absolute;top:-48px;right:-48px;width:160px;height:160px;background:var(--pink);border-radius:50%;opacity:.12}}
    .nlband::after{{content:'';position:absolute;bottom:-32px;left:-32px;width:120px;height:120px;background:var(--violet);border-radius:50%;opacity:.16}}
    .nley{{font-size:.65rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--pink);margin-bottom:7px}}
    .nlt{{font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:.04em;color:#fff;margin-bottom:8px}}
    .nls{{color:#9ca3af;font-size:.84rem;margin-bottom:22px;max-width:380px;margin-left:auto;margin-right:auto;line-height:1.6}}
    .nlf{{display:flex;gap:8px;max-width:400px;margin:0 auto;position:relative;z-index:1}}
    @media(max-width:460px){{.nlf{{flex-direction:column}}}}
    .nli{{flex:1;padding:10px 15px;border-radius:999px;border:1.5px solid rgba(255,255,255,.14);background:rgba(255,255,255,.07);color:#fff;font-family:'DM Sans',sans-serif;font-size:.84rem;outline:none}}
    .nli::placeholder{{color:#6b7280}}
    .nlb{{background:var(--pink);color:#fff;border:none;border-radius:999px;padding:10px 20px;font-family:'DM Sans',sans-serif;font-size:.84rem;font-weight:700;cursor:pointer;position:relative;z-index:1}}
    .nlnote{{color:#4b5568;font-size:.68rem;margin-top:9px;position:relative;z-index:1}}
    .sidebar{{position:sticky;top:70px;display:flex;flex-direction:column;gap:18px}}
    .scard{{background:var(--sur);border-radius:16px;padding:18px;box-shadow:var(--sh);border:1px solid var(--bdr)}}
    .sc-title{{font-family:'Bebas Neue',sans-serif;font-size:1.05rem;letter-spacing:.06em;color:var(--tx);margin-bottom:12px}}
    .mkt-row{{display:flex;align-items:center;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--bdr)}}
    .mkt-row:last-child{{border-bottom:none}}
    .mn{{font-size:.8rem;font-weight:600;color:var(--tx)}}.mt{{font-size:.66rem;color:var(--tx3)}}
    .mv{{font-size:.83rem;font-weight:600;color:var(--tx);text-align:right}}
    .mc{{font-size:.68rem;font-weight:700;text-align:right}}.mc.up{{color:#10b981}}.mc.dn{{color:#ef4444}}
    .tlist{{list-style:none;display:flex;flex-direction:column;gap:12px}}
    .ti{{display:flex;align-items:flex-start;gap:10px;cursor:pointer}}
    .tnum{{font-family:'Bebas Neue',sans-serif;font-size:1.28rem;color:var(--bdr);line-height:1;flex-shrink:0;width:20px;transition:color .18s}}
    .ti:hover .tnum{{color:var(--pink)}}
    .tcat{{font-size:.6rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--violet);margin-bottom:2px}}
    .th{{font-size:.77rem;font-weight:600;color:var(--tx);line-height:1.35;transition:color .18s}}
    .ti:hover .th{{color:var(--pink)}}
    footer{{background:var(--navy);padding:34px 24px 22px}}
    .fi{{max-width:1280px;margin:0 auto}}
    .ft{{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:26px;margin-bottom:26px;padding-bottom:26px;border-bottom:1px solid #1f2937}}
    @media(max-width:580px){{.ft{{grid-template-columns:1fr}}}}
    .fb p{{color:#6b7280;font-size:.78rem;margin-top:7px;line-height:1.6}}
    .fct{{font-weight:700;font-size:.74rem;letter-spacing:.11em;text-transform:uppercase;color:#9ca3af;margin-bottom:11px}}
    .flinks{{list-style:none;display:flex;flex-direction:column;gap:6px}}
    .flinks a{{color:#6b7280;font-size:.8rem;text-decoration:none;transition:color .18s}}.flinks a:hover{{color:var(--pink)}}
    .fbot{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:9px}}
    .fcopy{{color:#4b5568;font-size:.74rem}}.fcopy span{{color:var(--pink)}}
    .soc{{display:flex;gap:7px}}
    .socbtn{{width:30px;height:30px;border-radius:7px;background:rgba(255,255,255,.05);border:1px solid #1f2937;display:flex;align-items:center;justify-content:center;color:#6b7280;font-size:.78rem;text-decoration:none;transition:all .18s}}
    .socbtn:hover{{background:var(--pink);color:#fff;border-color:var(--pink);transform:translateY(-2px)}}
    .toast{{position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(60px);background:#1f2937;color:#fff;font-size:.8rem;font-weight:500;padding:9px 18px;border-radius:999px;box-shadow:0 8px 32px rgba(0,0,0,.35);z-index:998;transition:transform .3s cubic-bezier(.34,1.56,.64,1);pointer-events:none;border:1px solid rgba(255,255,255,.08);white-space:nowrap}}
    .toast.show{{transform:translateX(-50%) translateY(0)}}
    .moverlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);backdrop-filter:blur(5px);z-index:500;align-items:center;justify-content:center;padding:14px}}
    .moverlay.open{{display:flex}}
    .modal{{background:var(--sur);border-radius:20px;padding:32px;max-width:440px;width:100%;position:relative;box-shadow:0 32px 80px rgba(0,0,0,.45);animation:min .32s cubic-bezier(.34,1.3,.64,1);border:1px solid var(--bdr)}}
    @keyframes min{{from{{transform:scale(.88) translateY(16px);opacity:0}}to{{transform:scale(1) translateY(0);opacity:1}}}}
    .mcls{{position:absolute;top:12px;right:12px;background:var(--sur2);border:none;border-radius:50%;width:28px;height:28px;cursor:pointer;font-size:.85rem;display:flex;align-items:center;justify-content:center;color:var(--tx2)}}
    .mem{{font-size:2rem;margin-bottom:9px}}
    .modal h2{{font-family:'DM Serif Display',serif;font-size:1.5rem;color:var(--tx);margin-bottom:7px}}
    .modal p{{color:var(--tx2);font-size:.84rem;line-height:1.6;margin-bottom:18px}}
    .minp{{width:100%;padding:10px 15px;border-radius:10px;border:1.5px solid var(--bdr);background:var(--sur2);color:var(--tx);font-family:'DM Sans',sans-serif;font-size:.86rem;outline:none;margin-bottom:9px}}
    .mbtn{{width:100%;background:var(--pink);color:#fff;border:none;border-radius:10px;padding:11px;font-family:'DM Sans',sans-serif;font-weight:700;font-size:.86rem;cursor:pointer}}
    .fi-card{{opacity:0;transform:translateY(14px);animation:fup .46s forwards}}
    @keyframes fup{{to{{opacity:1;transform:translateY(0)}}}}
    .fi-card:nth-child(1){{animation-delay:.04s}}.fi-card:nth-child(2){{animation-delay:.09s}}.fi-card:nth-child(3){{animation-delay:.14s}}
    .nsec{{display:none}}.nsec.vis{{display:block}}
    .nlsec{{display:none}}.nlsec.vis{{display:block}}
  </style>
</head>
<body>
<div id="prog"></div>
<header>
  <div class="hi">
    <a href="#" class="logo"><div class="logo-sq"></div><span class="logo-txt">Daily Digest</span></a>
    <div class="hr">
      <span class="tagline">Your news, beautifully illustrated</span>
      <span class="date-badge">📅 {TODAY}</span>
      <button class="btn-sub" onclick="openModal()">Subscribe Free</button>
      <button class="btn-theme" id="themeBtn" onclick="toggleTheme()">🌙</button>
    </div>
  </div>
</header>
<div class="ticker-wrap">
  <div class="ticker-label">🔥 Breaking</div>
  <div class="ticker-track">{ticker_items(all_articles)}</div>
</div>
<nav class="fbar">
  <span class="flbl">Filter:</span>
  <button class="pill on" onclick="filter('all',this)">🗞️ All News</button>
  <button class="pill" onclick="filter('tech',this)">🤖 AI &amp; Tech</button>
  <button class="pill" onclick="filter('mkt',this)">📈 Markets</button>
  <button class="pill" onclick="filter('geo',this)">🌍 Geopolitics</button>
  <button class="pill" onclick="filter('fash',this)">✨ Fashion</button>
</nav>
<div class="wrap">
<div class="feed">
  <section class="nsec vis" data-cat="tech">
    <div class="sh"><div class="si tech">🤖</div><h2 class="stitle">AI &amp; Tech</h2></div>
    <div class="cgrid">
      {card_hero(tech[0],IMAGES['tech'][0],'t','AI & TECH')}
      <div class="crow">{card_small(tech[1],SMALL_IMAGES['tech'][0],'t','TECH')}{card_small(tech[2] if len(tech)>2 else tech[1],SMALL_IMAGES['tech'][1],'t','TECH')}</div>
    </div>
  </section>
  <div class="divider"></div>
  <div class="nlsec vis nlband">
    <p class="nley">📬 Free Daily Newsletter</p>
    <h2 class="nlt">Stay ahead of the story</h2>
    <p class="nls">Top 5 stories every morning at 8am PST. No noise — just what matters.</p>
    <div class="nlf"><input class="nli" type="email" placeholder="your@email.com"/><button class="nlb" onclick="subscribe()">Subscribe →</button></div>
    <p class="nlnote">Join 42,000+ readers · Unsubscribe anytime</p>
  </div>
  <section class="nsec vis" data-cat="mkt">
    <div class="sh"><div class="si mkt">📈</div><h2 class="stitle">Markets</h2></div>
    <div class="cgrid">
      {card_hero(stocks[0],IMAGES['stocks'][0],'m','MARKETS')}
      <div class="crow">{card_small(stocks[1],SMALL_IMAGES['stocks'][0],'m','MARKETS')}{card_small(stocks[2] if len(stocks)>2 else stocks[1],SMALL_IMAGES['stocks'][1],'m','MARKETS')}</div>
    </div>
  </section>
  <div class="divider"></div>
  <section class="nsec vis" data-cat="geo">
    <div class="sh"><div class="si geo">🌍</div><h2 class="stitle">Geopolitics</h2></div>
    <div class="cgrid">
      {card_hero(geo[0],IMAGES['geo'][0],'g','WORLD')}
      <div class="crow">{card_small(geo[1],SMALL_IMAGES['geo'][0],'g','GLOBAL')}{card_small(geo[2] if len(geo)>2 else geo[1],SMALL_IMAGES['geo'][1],'g','GLOBAL')}</div>
    </div>
  </section>
  <div class="divider"></div>
  <section class="nsec vis" data-cat="fash">
    <div class="sh"><div class="si fash">✨</div><h2 class="stitle">Fashion</h2></div>
    <div class="cgrid">
      {card_hero(fashion[0],IMAGES['fashion'][0],'f','FASHION')}
      <div class="crow">{card_small(fashion[1],SMALL_IMAGES['fashion'][0],'f','STYLE')}{card_small(fashion[2] if len(fashion)>2 else fashion[1],SMALL_IMAGES['fashion'][1],'f','STYLE')}</div>
    </div>
  </section>
</div>
<aside class="sidebar">
  <div class="scard">
    <h3 class="sc-title">📊 Markets Snapshot</h3>
    <div>
      <div class="mkt-row"><div><div class="mn">S&amp;P 500</div><div class="mt">SPX</div></div><div><div class="mv">5,363</div><div class="mc dn">▼ −3.5%</div></div></div>
      <div class="mkt-row"><div><div class="mn">NASDAQ</div><div class="mt">COMP</div></div><div><div class="mv">16,387</div><div class="mc dn">▼ −4.1%</div></div></div>
      <div class="mkt-row"><div><div class="mn">Bitcoin</div><div class="mt">BTC</div></div><div><div class="mv">$82,400</div><div class="mc dn">▼ −1.8%</div></div></div>
      <div class="mkt-row"><div><div class="mn">Gold</div><div class="mt">XAU</div></div><div><div class="mv">$3,238</div><div class="mc up">▲ +1.9%</div></div></div>
      <div class="mkt-row"><div><div class="mn">Oil (WTI)</div><div class="mt">crude</div></div><div><div class="mv">$61.10</div><div class="mc dn">▼ −2.1%</div></div></div>
    </div>
  </div>
  <div class="scard">
    <h3 class="sc-title">🔥 Most Read Today</h3>
    <ul class="tlist">{trending_html(all_articles)}</ul>
  </div>
  <div class="scard" style="background:linear-gradient(135deg,#0d1117,#1e1060);border-color:transparent">
    <p style="font-size:.63rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:var(--pink);margin-bottom:5px">📬 Newsletter</p>
    <p style="font-family:'DM Serif Display',serif;font-size:1rem;color:#fff;margin-bottom:5px">5 stories. Every morning.</p>
    <p style="font-size:.74rem;color:#6b7280;margin-bottom:13px;line-height:1.5">Updated daily at 8am PST.</p>
    <input type="email" placeholder="your@email.com" style="width:100%;padding:8px 12px;border-radius:8px;border:1.5px solid rgba(255,255,255,.1);background:rgba(255,255,255,.06);color:#fff;font-family:'DM Sans',sans-serif;font-size:.78rem;outline:none;margin-bottom:7px"/>
    <button onclick="subscribe()" style="width:100%;background:var(--pink);color:#fff;border:none;border-radius:8px;padding:8px;font-family:'DM Sans',sans-serif;font-weight:700;font-size:.78rem;cursor:pointer">Subscribe Free →</button>
  </div>
</aside>
</div>
<footer>
  <div class="fi">
    <div class="ft">
      <div class="fb">
        <a href="#" class="logo"><div class="logo-sq"></div><span class="logo-txt">Daily Digest</span></a>
        <p>Your news, beautifully illustrated. AI, markets, geopolitics & fashion — refreshed every morning at 8am PST.</p>
      </div>
      <div><p class="fct">Sections</p><ul class="flinks"><li><a href="#">🤖 AI &amp; Tech</a></li><li><a href="#">📈 Markets</a></li><li><a href="#">🌍 Geopolitics</a></li><li><a href="#">✨ Fashion</a></li></ul></div>
      <div><p class="fct">Company</p><ul class="flinks"><li><a href="#">About</a></li><li><a href="#">Newsletter</a></li><li><a href="#">Privacy</a></li><li><a href="#">Contact</a></li></ul></div>
    </div>
    <div class="fbot">
      <p class="fcopy">© 2026 <span>Daily Digest</span> · Updated daily at 8am PST</p>
      <div class="soc"><a class="socbtn" href="#">𝕏</a><a class="socbtn" href="#">📸</a><a class="socbtn" href="#">in</a><a class="socbtn" href="#">📡</a></div>
    </div>
  </div>
</footer>
<div class="moverlay" id="mo" onclick="cmo(event)">
  <div class="modal">
    <button class="mcls" onclick="closeModal()">✕</button>
    <div class="mem">📬</div>
    <h2>Get the Daily Digest</h2>
    <p>5 hand-picked stories every morning. Join 42,000+ readers.</p>
    <input class="minp" type="email" placeholder="your@email.com"/>
    <button class="mbtn" onclick="subscribe()">Subscribe for Free →</button>
    <p style="font-size:.68rem;color:var(--tx3);margin-top:9px;text-align:center">No spam. Unsubscribe anytime.</p>
  </div>
</div>
<div class="toast" id="toast"></div>
<script>
  const t=localStorage.getItem('dd-theme')||'light';
  document.documentElement.setAttribute('data-theme',t);
  document.getElementById('themeBtn').textContent=t==='dark'?'☀️':'🌙';
  function toggleTheme(){{const n=document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',n);localStorage.setItem('dd-theme',n);document.getElementById('themeBtn').textContent=n==='dark'?'☀️':'🌙';toast(n==='dark'?'🌙 Dark mode on':'☀️ Light mode on')}}
  function filter(cat,btn){{document.querySelectorAll('.pill').forEach(p=>p.classList.remove('on'));btn.classList.add('on');document.querySelectorAll('.nsec').forEach(s=>s.classList.toggle('vis',cat==='all'||s.dataset.cat===cat));const nl=document.querySelector('.nlsec');if(nl)nl.classList.toggle('vis',cat==='all')}}
  function save(b){{b.classList.toggle('saved');toast(b.classList.contains('saved')?'🔖 Article saved!':'Removed from saved')}}
  function subscribe(){{closeModal();toast('🎉 You\'re subscribed! Check your inbox.')}}
  function openModal(){{document.getElementById('mo').classList.add('open')}}
  function closeModal(){{document.getElementById('mo').classList.remove('open')}}
  function cmo(e){{if(e.target.id==='mo')closeModal()}}
  document.addEventListener('keydown',e=>{{if(e.key==='Escape')closeModal()}});
  let tt;
  function toast(m){{const el=document.getElementById('toast');el.textContent=m;el.classList.add('show');clearTimeout(tt);tt=setTimeout(()=>el.classList.remove('show'),2800)}}
  window.addEventListener('scroll',()=>{{const h=document.documentElement.scrollHeight-window.innerHeight;document.getElementById('prog').style.width=(h>0?(scrollY/h)*100:0)+'%'}});
</script>
</body>
</html>"""

if __name__ == "__main__":
    print("Fetching news...")
    all_articles = {}
    for cat, params in QUERIES.items():
        print(f"  → {cat}")
        all_articles[cat] = fetch_articles(cat, params)
    print("Building HTML...")
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_html(all_articles))
    print(f"✅ Done — {TODAY}")  
