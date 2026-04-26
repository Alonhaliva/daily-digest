#!/usr/bin/env python3
"""
Daily Digest — auto news updater
Runs every day at 8am PST via GitHub Actions.
"""
import os, json, random, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

API_KEY = os.environ.get("NEWS_API_KEY", "")
PST     = timezone(timedelta(hours=-8))
TODAY   = datetime.now(PST).strftime("%B %d, %Y")
SEED    = int(datetime.now(PST).strftime("%Y%m%d"))
random.seed(SEED)

ALL_IMAGES = {
    "tech": [
        "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&q=80",
        "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=800&q=80",
        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800&q=80",
        "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&q=80",
        "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80",
        "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&q=80",
        "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=800&q=80",
        "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=800&q=80",
    ],
    "stocks": [
        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
        "https://images.unsplash.com/photo-1559526324-593bc073d938?w=800&q=80",
        "https://images.unsplash.com/photo-1640340434855-6084b1f4901c?w=800&q=80",
        "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&q=80",
        "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800&q=80",
        "https://images.unsplash.com/photo-1579621970795-87facc2f976d?w=800&q=80",
        "https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=800&q=80",
        "https://images.unsplash.com/photo-1631897642057-8f1e9bed28e6?w=800&q=80",
    ],
    "geo": [
        "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=800&q=80",
        "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=800&q=80",
        "https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=800&q=80",
        "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=80",
        "https://images.unsplash.com/photo-1522661067900-ab829854a57f?w=800&q=80",
        "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800&q=80",
        "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80",
        "https://images.unsplash.com/photo-1568515045052-f9a854d70bfd?w=800&q=80",
    ],
    "fashion": [
        "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=800&q=80",
        "https://images.unsplash.com/photo-1445205170230-053b83016050?w=800&q=80",
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&q=80",
        "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=800&q=80",
        "https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=800&q=80",
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=800&q=80",
        "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=800&q=80",
        "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=800&q=80",
    ],
}

QUERIES = {
    "tech":    {"q": "artificial intelligence OR technology", "language": "en", "sortBy": "publishedAt", "pageSize": "4"},
    "stocks":  {"q": "stock market OR economy OR finance OR tariffs", "language": "en", "sortBy": "publishedAt", "pageSize": "4"},
    "geo":     {"q": "geopolitics OR war OR diplomacy OR world news", "language": "en", "sortBy": "publishedAt", "pageSize": "4"},
    "fashion": {"q": "fashion OR style OR luxury OR clothing", "language": "en", "sortBy": "publishedAt", "pageSize": "4"},
}

FALLBACK = {
    "tech": [
        {"title": "Meta's Muse Spark arrives — ending the company's open-source AI era",
         "description": "Meta's first proprietary AI model since its $14.3B Scale AI deal rolls out across Facebook, Instagram, WhatsApp and Ray-Ban glasses with a deep-reasoning Contemplating mode.",
         "url": "https://www.cnbc.com/2026/04/08/meta-debuts-first-major-ai-model-since-14-billion-deal-to-bring-in-alexandr-wang.html",
         "source": {"name": "CNBC"}, "read_time": "5 min read"},
        {"title": "Big Tech races to lock in nuclear power deals for AI data centers",
         "description": "Microsoft, Google and Amazon are signing long-term nuclear energy contracts as AI infrastructure demand outpaces grid capacity.",
         "url": "#", "source": {"name": "Wired"}, "read_time": "3 min read"},
        {"title": "Gucci and Google announce luxury AI smart glasses launching 2027",
         "description": "Kering CEO confirmed the Gucci-branded device will combine the house's iconic aesthetics with Google AI, intensifying rivalry with Meta's Ray-Ban line.",
         "url": "#", "source": {"name": "Logos Press"}, "read_time": "3 min read"},
    ],
    "stocks": [
        {"title": "Markets tumble as Iran shuts Strait of Hormuz — oil surges 4%",
         "description": "Wall Street fell sharply after Iran closed the vital shipping lane following a US Navy seizure of an Iranian cargo ship. Gold hit fresh highs as investors sought safe havens.",
         "url": "#", "source": {"name": "Bloomberg"}, "read_time": "5 min read"},
        {"title": "Trump ceasefire with Iran expires Wednesday — markets brace for volatility",
         "description": "President Trump said it is highly unlikely he will extend the ceasefire, raising the prospect of renewed conflict and sustained energy price pressure.",
         "url": "https://www.cnn.com/2026/04/20/world/live-news/iran-war-us-trump-israel",
         "source": {"name": "CNN"}, "read_time": "4 min read"},
        {"title": "OpenAI targets $1 trillion IPO — retail investors will get a slice",
         "description": "CFO Sarah Friar confirmed OpenAI is laying groundwork for a US listing after individual investors committed more than $3B in its latest funding round.",
         "url": "#", "source": {"name": "Reuters"}, "read_time": "3 min read"},
    ],
    "geo": [
        {"title": "Iran shuts Strait of Hormuz again after US seizes Iranian cargo ship",
         "description": "Tehran closed the vital waterway one day after reopening it. Trump insists a deal is very close but Iran's Foreign Ministry says there are no active negotiations.",
         "url": "https://www.democracynow.org/2026/4/20/headlines",
         "source": {"name": "CNN / Democracy Now"}, "read_time": "5 min read"},
        {"title": "Magnitude 7.7 earthquake strikes northern Japan — tsunami warning issued then lifted",
         "description": "A powerful quake off Iwate prefecture shook buildings as far away as Tokyo before the tsunami alert was downgraded as waves stayed below 1 metre.",
         "url": "https://www.aljazeera.com/news/2026/4/20/powerful-7-4-earthquake-strikes-northern-japan-tsunami-warning-issued",
         "source": {"name": "Al Jazeera"}, "read_time": "3 min read"},
        {"title": "Orban concedes as Hungary opposition heads for historic supermajority",
         "description": "Opposition leader Peter Magyar surged to a landslide result, signalling a major political realignment in one of the EU's most contested democracies.",
         "url": "#", "source": {"name": "Fox News"}, "read_time": "4 min read"},
    ],
    "fashion": [
        {"title": "AI is finally cracking fashion's biggest problem — the dreaded return",
         "description": "AI startups including Catches are using physics-based digital twins to let shoppers see exactly how clothes fit, targeting a 20-30x ROI for luxury brands.",
         "url": "https://www.cnbc.com/2026/04/05/ai-retail-start-ups-virtual-try-on-tech-margins.html",
         "source": {"name": "CNBC"}, "read_time": "4 min read"},
        {"title": "LVMH, Kering and Richemont re-examine brand portfolios amid margin squeeze",
         "description": "The three luxury conglomerates are restructuring store networks as rising tariffs, volatile demand, and AI disruption reshape the industry.",
         "url": "#", "source": {"name": "Business of Fashion"}, "read_time": "5 min read"},
        {"title": "Quiet luxury holds firm as maximalism fades from the global runway",
         "description": "Milan and Paris confirmed precision tailoring, neutral palettes and understated silhouettes as the decade's defining aesthetic this season.",
         "url": "#", "source": {"name": "Vogue"}, "read_time": "3 min read"},
    ],
}

READ_TIMES = ["2 min read", "3 min read", "4 min read", "5 min read"]


def get_images(cat):
    pool = ALL_IMAGES[cat][:]
    random.shuffle(pool)
    return pool[:3]


def fetch_articles(cat, params):
    if not API_KEY:
        print(f"    No API key — using fallback for {cat}")
        return FALLBACK[cat]
    try:
        p = dict(params)
        p["apiKey"] = API_KEY
        url = "https://newsapi.org/v2/everything?" + urllib.parse.urlencode(p)
        req = urllib.request.Request(url, headers={"User-Agent": "DailyDigest/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        articles = [
            a for a in data.get("articles", [])
            if a.get("title") and a.get("description")
            and "[Removed]" not in a.get("title", "")
            and len(a.get("description", "")) > 40
        ]
        result = []
        for i, a in enumerate(articles[:3]):
            result.append({
                "title":       a["title"].split(" - ")[0][:120],
                "description": (a.get("description") or "")[:220],
                "url":         a.get("url", "#"),
                "source":      a.get("source", {"name": "News"}),
                "read_time":   READ_TIMES[i % len(READ_TIMES)],
            })
        return result if len(result) >= 2 else FALLBACK[cat]
    except Exception as e:
        print(f"    API error ({cat}): {e} — using fallback")
        return FALLBACK[cat]


def card_hero(art, img, bdg_cls, bdg_txt):
    src   = art.get("source", {}).get("name", "News")
    rt    = art.get("read_time", "4 min read")
    url   = art.get("url", "#")
    tgt   = 'target="_blank" rel="noopener"' if url != "#" else ""
    title = art["title"].replace('"', "&quot;").replace("'", "&#39;")
    desc  = art["description"].replace('"', "&quot;").replace("'", "&#39;")
    return (
        '<article class="card-hero fi-card">'
        f'<div class="iw"><img src="{img}" alt="{bdg_txt}" loading="lazy"/>'
        f'<span class="bdg {bdg_cls}">{bdg_txt}</span></div>'
        '<div class="cb"><div>'
        f'<div class="cmeta"><span class="src">{src}</span><span class="rt">&#9201; {rt}</span></div>'
        f'<h3 class="ctitle">{title}</h3>'
        f'<p class="cex">{desc}</p>'
        '</div>'
        f'<div class="cfoot"><a href="{url}" class="rl" {tgt}>Read Article &#8594;</a>'
        '<button class="sbtn" onclick="save(this)">&#128278;</button></div>'
        '</div></article>'
    )


def card_small(art, img, bdg_cls, bdg_txt):
    src   = art.get("source", {}).get("name", "News")
    rt    = art.get("read_time", "3 min read")
    url   = art.get("url", "#")
    tgt   = 'target="_blank" rel="noopener"' if url != "#" else ""
    title = art["title"].replace('"', "&quot;").replace("'", "&#39;")
    desc  = (art["description"][:160]).replace('"', "&quot;").replace("'", "&#39;")
    return (
        '<article class="cs fi-card">'
        f'<div class="iw"><img src="{img}" alt="{bdg_txt}" loading="lazy"/>'
        f'<span class="bdg {bdg_cls}">{bdg_txt}</span></div>'
        '<div class="cb">'
        f'<div class="cmeta"><span class="src">{src}</span><span class="rt">&#9201; {rt}</span></div>'
        f'<h3 class="ctitle">{title}</h3>'
        f'<p class="cex">{desc}</p>'
        f'<div class="cfoot"><a href="{url}" class="rl" {tgt}>Read &#8594;</a>'
        '<button class="sbtn" onclick="save(this)">&#128278;</button></div>'
        '</div></article>'
    )


def make_ticker(all_articles):
    emojis = {"tech": "&#129302;", "stocks": "&#128200;", "geo": "&#127758;", "fashion": "&#10024;"}
    items = ""
    for cat, arts in all_articles.items():
        for a in arts[:2]:
            t = a["title"][:80]
            items += f'<span class="ticker-item"><em>{emojis[cat]}</em>{t}</span>'
    return items + items


def make_trending(all_articles):
    labels = {"tech": "AI & Tech", "stocks": "Markets", "geo": "Geopolitics", "fashion": "Fashion"}
    html = ""
    n = 1
    for cat, arts in all_articles.items():
        for a in arts[:2]:
            t = a["title"][:68]
            num = "0" + str(n)
            html += (
                f'<li class="ti"><span class="tnum">{num}</span>'
                f'<div><div class="tcat">{labels[cat]}</div>'
                f'<div class="th">{t}</div></div></li>'
            )
            n += 1
            if n > 5:
                break
        if n > 5:
            break
    return html


def build_html(all_articles):
    imgs   = {cat: get_images(cat) for cat in all_articles}
    tech   = all_articles["tech"]
    stocks = all_articles["stocks"]
    geo    = all_articles["geo"]
    fashion = all_articles["fashion"]

    ticker   = make_ticker(all_articles)
    trending = make_trending(all_articles)

    t_hero  = card_hero(tech[0],    imgs["tech"][0],    "t", "AI &amp; TECH")
    t_s1    = card_small(tech[1],   imgs["tech"][1],    "t", "TECH")
    t_s2    = card_small(tech[2] if len(tech) > 2 else tech[1], imgs["tech"][2], "t", "TECH")

    m_hero  = card_hero(stocks[0],  imgs["stocks"][0],  "m", "MARKETS")
    m_s1    = card_small(stocks[1], imgs["stocks"][1],  "m", "MARKETS")
    m_s2    = card_small(stocks[2] if len(stocks) > 2 else stocks[1], imgs["stocks"][2], "m", "MARKETS")

    g_hero  = card_hero(geo[0],     imgs["geo"][0],     "g", "WORLD")
    g_s1    = card_small(geo[1],    imgs["geo"][1],     "g", "GLOBAL")
    g_s2    = card_small(geo[2] if len(geo) > 2 else geo[1], imgs["geo"][2], "g", "GLOBAL")

    f_hero  = card_hero(fashion[0], imgs["fashion"][0], "f", "FASHION")
    f_s1    = card_small(fashion[1],imgs["fashion"][1], "f", "STYLE")
    f_s2    = card_small(fashion[2] if len(fashion) > 2 else fashion[1], imgs["fashion"][2], "f", "STYLE")

    # Write CSS and JS without f-string to avoid double-brace issues
    css = """
    *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
    :root{--navy:#0d1117;--pink:#ff2d78;--violet:#7c3aed;--vl:#a78bfa;--bg:#f0f2f7;--sur:#fff;--sur2:#f8f9fc;--bdr:#e5e7eb;--tx:#0d1117;--tx2:#6b7280;--tx3:#9ca3af;--sh:0 4px 24px rgba(0,0,0,.07);--sh2:0 16px 48px rgba(0,0,0,.14)}
    [data-theme=dark]{--bg:#0a0d14;--sur:#131720;--sur2:#1a2030;--bdr:#252d3d;--tx:#e8eaf0;--tx2:#8892a4;--tx3:#4b5568;--sh:0 4px 24px rgba(0,0,0,.3);--sh2:0 16px 48px rgba(0,0,0,.5)}
    html{scroll-behavior:smooth}
    body{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--tx);min-height:100vh;transition:background .3s,color .3s}
    #prog{position:fixed;top:0;left:0;height:3px;background:linear-gradient(to right,var(--pink),var(--violet));width:0%;z-index:9999;pointer-events:none}
    header{background:var(--navy);padding:16px 24px;position:sticky;top:0;z-index:200;box-shadow:0 2px 20px rgba(0,0,0,.45)}
    .hi{max-width:1280px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:14px}
    .logo{display:inline-flex;align-items:center;gap:10px;text-decoration:none}
    .logo-sq{width:28px;height:28px;background:var(--pink);border-radius:6px;flex-shrink:0}
    .logo-txt{font-family:'Bebas Neue',sans-serif;font-size:1.9rem;letter-spacing:.06em;color:var(--pink);line-height:1}
    .hr{display:flex;align-items:center;gap:9px}
    .tagline{color:#9ca3af;font-size:.74rem;letter-spacing:.04em}
    @media(max-width:580px){.tagline{display:none}}
    .date-badge{background:rgba(255,255,255,.1);color:#9ca3af;font-size:.7rem;padding:4px 10px;border-radius:999px;border:1px solid rgba(255,255,255,.12);white-space:nowrap}
    @media(max-width:640px){.date-badge{display:none}}
    .btn-sub{background:var(--pink);color:#fff;border:none;border-radius:999px;padding:7px 16px;font-family:'DM Sans',sans-serif;font-size:.78rem;font-weight:700;cursor:pointer;transition:opacity .18s,transform .18s}
    .btn-sub:hover{opacity:.88;transform:translateY(-1px)}
    @media(max-width:400px){.btn-sub{display:none}}
    .btn-theme{background:rgba(255,255,255,.08);border:1.5px solid rgba(255,255,255,.14);border-radius:50%;color:#fff;width:36px;height:36px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:.95rem;transition:background .2s,transform .25s;flex-shrink:0}
    .btn-theme:hover{background:rgba(255,255,255,.16);transform:rotate(22deg)}
    .ticker-wrap{background:var(--navy);height:36px;display:flex;align-items:center;overflow:hidden;width:100%}
    [data-theme=dark] .ticker-wrap{background:#0d0f17;border-bottom:1px solid var(--bdr)}
    .ticker-label{background:var(--pink);color:#fff;font-size:.65rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;padding:0 14px;height:36px;line-height:36px;white-space:nowrap;flex-shrink:0}
    .ticker-outer{flex:1;overflow:hidden;height:36px;display:flex;align-items:center}
    .ticker-track{display:flex;animation:tick 60s linear infinite;white-space:nowrap;align-items:center}
    .ticker-track:hover{animation-play-state:paused}
    .ticker-item{color:#d1d5db;font-size:.72rem;padding:0 28px;line-height:36px}
    .ticker-item em{color:var(--pink);font-style:normal;margin-right:6px}
    @keyframes tick{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
    .fbar{background:var(--sur);border-bottom:1px solid var(--bdr);padding:10px 24px;display:flex;align-items:center;gap:8px;overflow-x:auto;scrollbar-width:none;transition:background .3s}
    .fbar::-webkit-scrollbar{display:none}
    .flbl{font-weight:600;font-size:.77rem;color:var(--tx2);white-space:nowrap;margin-right:3px}
    .pill{display:inline-flex;align-items:center;gap:5px;padding:5px 14px;border-radius:999px;border:1.5px solid var(--bdr);background:transparent;font-family:'DM Sans',sans-serif;font-size:.78rem;font-weight:500;cursor:pointer;white-space:nowrap;transition:all .18s;color:var(--tx)}
    .pill:hover{border-color:var(--violet);color:var(--violet);transform:translateY(-1px)}
    .pill.on{background:var(--navy);border-color:var(--navy);color:#fff}
    [data-theme=dark] .pill.on{background:var(--pink);border-color:var(--pink)}
    .wrap{max-width:1280px;margin:0 auto;padding:30px 24px 80px;display:grid;grid-template-columns:1fr 296px;gap:34px;align-items:start}
    @media(max-width:1024px){.wrap{grid-template-columns:1fr}.sidebar{display:none}}
    .sh{display:flex;align-items:center;gap:11px;margin-bottom:16px}
    .si{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.25rem}
    .si.tech{background:linear-gradient(135deg,#6366f1,#8b5cf6)}.si.mkt{background:linear-gradient(135deg,#f59e0b,#ef4444)}.si.geo{background:linear-gradient(135deg,#10b981,#3b82f6)}.si.fash{background:linear-gradient(135deg,#f472b6,#a78bfa)}
    .stitle{font-family:'Bebas Neue',sans-serif;font-size:1.75rem;letter-spacing:.05em;color:var(--tx)}
    .cgrid{display:grid;gap:17px;margin-bottom:44px}
    .crow{display:grid;grid-template-columns:1fr 1fr;gap:17px}
    @media(max-width:540px){.crow{grid-template-columns:1fr}}
    .card-hero{display:grid;grid-template-columns:1fr 1fr;background:var(--sur);border-radius:18px;overflow:hidden;box-shadow:var(--sh);transition:transform .22s,box-shadow .22s;border:1px solid var(--bdr)}
    .card-hero:hover{transform:translateY(-4px);box-shadow:var(--sh2)}
    @media(max-width:600px){.card-hero{grid-template-columns:1fr}}
    .iw{position:relative;overflow:hidden}
    .card-hero .iw{min-height:280px}
    @media(max-width:600px){.card-hero .iw{min-height:200px}}
    .cs .iw{height:170px}
    .iw img{width:100%;height:100%;object-fit:cover;display:block;transition:transform .45s}
    .card-hero:hover .iw img,.cs:hover .iw img{transform:scale(1.05)}
    .bdg{position:absolute;top:12px;left:12px;color:#fff;font-size:.62rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:3px 9px;border-radius:5px}
    .bdg.t{background:var(--violet)}.bdg.m{background:#d97706}.bdg.g{background:#059669}.bdg.f{background:#db2777}
    .cb{padding:26px 26px 20px;display:flex;flex-direction:column;justify-content:space-between}
    @media(max-width:600px){.cb{padding:16px}}
    .cs .cb{padding:16px 18px 14px}
    .cmeta{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
    .src{font-size:.64rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:var(--tx2)}
    .rt{font-size:.63rem;color:var(--tx3);background:var(--sur2);padding:2px 7px;border-radius:999px;border:1px solid var(--bdr)}
    .ctitle{font-family:'DM Serif Display',serif;font-size:1.32rem;line-height:1.28;color:var(--tx);margin-bottom:10px;transition:color .18s}
    .card-hero:hover .ctitle,.cs:hover .ctitle{color:var(--violet)}
    [data-theme=dark] .card-hero:hover .ctitle,[data-theme=dark] .cs:hover .ctitle{color:var(--vl)}
    .cs .ctitle{font-size:.98rem}
    .cex{font-size:.83rem;line-height:1.68;color:var(--tx2);flex-grow:1}
    .cfoot{display:flex;align-items:center;justify-content:space-between;margin-top:18px;padding-top:13px;border-top:1px solid var(--bdr)}
    .rl{display:inline-flex;align-items:center;gap:5px;color:var(--violet);font-weight:600;font-size:.8rem;text-decoration:none;transition:gap .18s}
    [data-theme=dark] .rl{color:var(--vl)}
    .rl:hover{gap:9px}
    .sbtn{background:none;border:1.5px solid var(--bdr);border-radius:7px;width:28px;height:28px;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:.8rem;transition:all .18s;color:var(--tx2)}
    .sbtn:hover{border-color:var(--pink);color:var(--pink);transform:scale(1.1)}
    .sbtn.saved{background:var(--pink);border-color:var(--pink);color:#fff}
    .cs{background:var(--sur);border-radius:18px;overflow:hidden;box-shadow:var(--sh);display:flex;flex-direction:column;transition:transform .22s,box-shadow .22s;border:1px solid var(--bdr)}
    .cs:hover{transform:translateY(-4px);box-shadow:var(--sh2)}
    .divider{height:1px;background:linear-gradient(to right,transparent,var(--bdr),transparent);margin:0 0 38px}
    .nlband{background:linear-gradient(135deg,#0d1117,#1e1060);border-radius:20px;padding:36px 32px;text-align:center;margin-bottom:44px;position:relative;overflow:hidden}
    .nlband::before{content:'';position:absolute;top:-48px;right:-48px;width:160px;height:160px;background:var(--pink);border-radius:50%;opacity:.12}
    .nlband::after{content:'';position:absolute;bottom:-32px;left:-32px;width:120px;height:120px;background:var(--violet);border-radius:50%;opacity:.16}
    .nley{font-size:.65rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--pink);margin-bottom:7px}
    .nlt{font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:.04em;color:#fff;margin-bottom:8px}
    .nls{color:#9ca3af;font-size:.84rem;margin-bottom:22px;max-width:380px;margin-left:auto;margin-right:auto;line-height:1.6}
    .nlf{display:flex;gap:8px;max-width:400px;margin:0 auto;position:relative;z-index:1}
    @media(max-width:460px){.nlf{flex-direction:column}}
    .nli{flex:1;padding:10px 15px;border-radius:999px;border:1.5px solid rgba(255,255,255,.14);background:rgba(255,255,255,.07);color:#fff;font-family:'DM Sans',sans-serif;font-size:.84rem;outline:none}
    .nli::placeholder{color:#6b7280}
    .nlb{background:var(--pink);color:#fff;border:none;border-radius:999px;padding:10px 20px;font-family:'DM Sans',sans-serif;font-size:.84rem;font-weight:700;cursor:pointer;position:relative;z-index:1}
    .nlnote{color:#4b5568;font-size:.68rem;margin-top:9px;position:relative;z-index:1}
    .sidebar{position:sticky;top:70px;display:flex;flex-direction:column;gap:18px}
    .scard{background:var(--sur);border-radius:16px;padding:18px;box-shadow:var(--sh);border:1px solid var(--bdr)}
    .sc-title{font-family:'Bebas Neue',sans-serif;font-size:1.05rem;letter-spacing:.06em;color:var(--tx);margin-bottom:12px}
    .mkt-row{display:flex;align-items:center;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--bdr)}
    .mkt-row:last-child{border-bottom:none}
    .mn{font-size:.8rem;font-weight:600;color:var(--tx)}.mt{font-size:.66rem;color:var(--tx3)}
    .mv{font-size:.83rem;font-weight:600;color:var(--tx);text-align:right}
    .mc{font-size:.68rem;font-weight:700;text-align:right}.mc.up{color:#10b981}.mc.dn{color:#ef4444}
    .tlist{list-style:none;display:flex;flex-direction:column;gap:12px}
    .ti{display:flex;align-items:flex-start;gap:10px;cursor:pointer}
    .tnum{font-family:'Bebas Neue',sans-serif;font-size:1.28rem;color:var(--bdr);line-height:1;flex-shrink:0;width:20px;transition:color .18s}
    .ti:hover .tnum{color:var(--pink)}
    .tcat{font-size:.6rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--violet);margin-bottom:2px}
    [data-theme=dark] .tcat{color:var(--vl)}
    .th{font-size:.77rem;font-weight:600;color:var(--tx);line-height:1.35;transition:color .18s}
    .ti:hover .th{color:var(--pink)}
    footer{background:var(--navy);padding:34px 24px 22px}
    .fi{max-width:1280px;margin:0 auto}
    .ft{display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:26px;margin-bottom:26px;padding-bottom:26px;border-bottom:1px solid #1f2937}
    @media(max-width:580px){.ft{grid-template-columns:1fr}}
    .fb p{color:#6b7280;font-size:.78rem;margin-top:7px;line-height:1.6}
    .fct{font-weight:700;font-size:.74rem;letter-spacing:.11em;text-transform:uppercase;color:#9ca3af;margin-bottom:11px}
    .flinks{list-style:none;display:flex;flex-direction:column;gap:6px}
    .flinks a{color:#6b7280;font-size:.8rem;text-decoration:none;transition:color .18s}.flinks a:hover{color:var(--pink)}
    .fbot{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:9px}
    .fcopy{color:#4b5568;font-size:.74rem}.fcopy span{color:var(--pink)}
    .soc{display:flex;gap:7px}
    .socbtn{width:30px;height:30px;border-radius:7px;background:rgba(255,255,255,.05);border:1px solid #1f2937;display:flex;align-items:center;justify-content:center;color:#6b7280;font-size:.78rem;text-decoration:none;transition:all .18s}
    .socbtn:hover{background:var(--pink);color:#fff;border-color:var(--pink);transform:translateY(-2px)}
    .toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%) translateY(60px);background:#1f2937;color:#fff;font-size:.8rem;font-weight:500;padding:9px 18px;border-radius:999px;box-shadow:0 8px 32px rgba(0,0,0,.35);z-index:998;transition:transform .3s cubic-bezier(.34,1.56,.64,1);pointer-events:none;border:1px solid rgba(255,255,255,.08);white-space:nowrap}
    .toast.show{transform:translateX(-50%) translateY(0)}
    .moverlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.6);backdrop-filter:blur(5px);z-index:500;align-items:center;justify-content:center;padding:14px}
    .moverlay.open{display:flex}
    .modal{background:var(--sur);border-radius:20px;padding:32px;max-width:440px;width:100%;position:relative;box-shadow:0 32px 80px rgba(0,0,0,.45);animation:minIn .32s cubic-bezier(.34,1.3,.64,1);border:1px solid var(--bdr)}
    @keyframes minIn{from{transform:scale(.88) translateY(16px);opacity:0}to{transform:scale(1) translateY(0);opacity:1}}
    .mcls{position:absolute;top:12px;right:12px;background:var(--sur2);border:none;border-radius:50%;width:28px;height:28px;cursor:pointer;font-size:.85rem;display:flex;align-items:center;justify-content:center;color:var(--tx2)}
    .mem{font-size:2rem;margin-bottom:9px}
    .modal h2{font-family:'DM Serif Display',serif;font-size:1.5rem;color:var(--tx);margin-bottom:7px}
    .modal p{color:var(--tx2);font-size:.84rem;line-height:1.6;margin-bottom:18px}
    .minp{width:100%;padding:10px 15px;border-radius:10px;border:1.5px solid var(--bdr);background:var(--sur2);color:var(--tx);font-family:'DM Sans',sans-serif;font-size:.86rem;outline:none;margin-bottom:9px}
    .mbtn{width:100%;background:var(--pink);color:#fff;border:none;border-radius:10px;padding:11px;font-family:'DM Sans',sans-serif;font-weight:700;font-size:.86rem;cursor:pointer}
    .fi-card{opacity:0;transform:translateY(14px);animation:fup .46s forwards}
    @keyframes fup{to{opacity:1;transform:translateY(0)}}
    .fi-card:nth-child(1){animation-delay:.04s}.fi-card:nth-child(2){animation-delay:.09s}.fi-card:nth-child(3){animation-delay:.14s}
    .nsec{display:none}.nsec.vis{display:block}
    .nlsec{display:none}.nlsec.vis{display:block}
    """

    js = """
    const t=localStorage.getItem('dd-theme')||'light';
    document.documentElement.setAttribute('data-theme',t);
    document.getElementById('themeBtn').textContent=t==='dark'?'☀️':'🌙';
    function toggleTheme(){const n=document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark';document.documentElement.setAttribute('data-theme',n);localStorage.setItem('dd-theme',n);document.getElementById('themeBtn').textContent=n==='dark'?'☀️':'🌙';toast(n==='dark'?'🌙 Dark mode on':'☀️ Light mode on')}
    function filter(cat,btn){document.querySelectorAll('.pill').forEach(p=>p.classList.remove('on'));btn.classList.add('on');document.querySelectorAll('.nsec').forEach(s=>s.classList.toggle('vis',cat==='all'||s.dataset.cat===cat));const nl=document.querySelector('.nlsec');if(nl)nl.classList.toggle('vis',cat==='all')}
    function save(b){b.classList.toggle('saved');toast(b.classList.contains('saved')?'🔖 Article saved!':'Removed from saved')}
    function subscribe(){closeModal();toast('🎉 You are subscribed! Check your inbox.')}
    function openModal(){document.getElementById('mo').classList.add('open')}
    function closeModal(){document.getElementById('mo').classList.remove('open')}
    function cmo(e){if(e.target.id==='mo')closeModal()}
    document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()});
    let tt;
    function toast(m){const el=document.getElementById('toast');el.textContent=m;el.classList.add('show');clearTimeout(tt);tt=setTimeout(()=>el.classList.remove('show'),2800)}
    window.addEventListener('scroll',()=>{const h=document.documentElement.scrollHeight-window.innerHeight;document.getElementById('prog').style.width=(h>0?(scrollY/h)*100:0)+'%'});
    """

    return """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Daily Digest – """ + TODAY + """</title>
  <meta name="description" content="Today's top stories in AI, Markets, Geopolitics and Fashion — updated every morning at 8am PST."/>
  <meta property="og:title" content="Daily Digest – """ + TODAY + """"/>
  <meta property="og:description" content="Today's top stories in AI, Markets, Geopolitics and Fashion — beautifully illustrated."/>
  <meta property="og:image" content="https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&q=80"/>
  <meta property="og:url" content="https://alonhaliva.github.io/daily-digest/"/>
  <meta property="og:type" content="website"/>
  <meta name="twitter:card" content="summary_large_image"/>
  <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;600&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet"/>
  <style>""" + css + """</style>
</head>
<body>
<div id="prog"></div>
<header>
  <div class="hi">
    <a href="#" class="logo"><div class="logo-sq"></div><span class="logo-txt">Daily Digest</span></a>
    <div class="hr">
      <span class="tagline">Your news, beautifully illustrated</span>
      <span class="date-badge">&#128197; """ + TODAY + """</span>
      <button class="btn-sub" onclick="openModal()">Subscribe Free</button>
      <button class="btn-theme" id="themeBtn" onclick="toggleTheme()">&#127769;</button>
    </div>
  </div>
</header>
<div class="ticker-wrap">
  <div class="ticker-label">&#128293; Breaking</div>
  <div class="ticker-outer"><div class="ticker-track">""" + ticker + """</div></div>
</div>
<nav class="fbar">
  <span class="flbl">Filter:</span>
  <button class="pill on" onclick="filter('all',this)">&#128240; All News</button>
  <button class="pill" onclick="filter('tech',this)">&#129302; AI &amp; Tech</button>
  <button class="pill" onclick="filter('mkt',this)">&#128200; Markets</button>
  <button class="pill" onclick="filter('geo',this)">&#127758; Geopolitics</button>
  <button class="pill" onclick="filter('fash',this)">&#10024; Fashion</button>
</nav>
<div class="wrap">
<div class="feed">
  <section class="nsec vis" data-cat="tech">
    <div class="sh"><div class="si tech">&#129302;</div><h2 class="stitle">AI &amp; Tech</h2></div>
    <div class="cgrid">""" + t_hero + """<div class="crow">""" + t_s1 + t_s2 + """</div></div>
  </section>
  <div class="divider"></div>
  <div class="nlsec vis nlband">
    <p class="nley">&#128236; Free Daily Newsletter</p>
    <h2 class="nlt">Stay ahead of the story</h2>
    <p class="nls">Top 5 stories every morning at 8am PST. No noise — just what matters.</p>
    <div class="nlf"><input class="nli" type="email" placeholder="your@email.com"/><button class="nlb" onclick="subscribe()">Subscribe &#8594;</button></div>
    <p class="nlnote">Join 42,000+ readers &middot; Unsubscribe anytime</p>
  </div>
  <section class="nsec vis" data-cat="mkt">
    <div class="sh"><div class="si mkt">&#128200;</div><h2 class="stitle">Markets</h2></div>
    <div class="cgrid">""" + m_hero + """<div class="crow">""" + m_s1 + m_s2 + """</div></div>
  </section>
  <div class="divider"></div>
  <section class="nsec vis" data-cat="geo">
    <div class="sh"><div class="si geo">&#127758;</div><h2 class="stitle">Geopolitics</h2></div>
    <div class="cgrid">""" + g_hero + """<div class="crow">""" + g_s1 + g_s2 + """</div></div>
  </section>
  <div class="divider"></div>
  <section class="nsec vis" data-cat="fash">
    <div class="sh"><div class="si fash">&#10024;</div><h2 class="stitle">Fashion</h2></div>
    <div class="cgrid">""" + f_hero + """<div class="crow">""" + f_s1 + f_s2 + """</div></div>
  </section>
</div>
<aside class="sidebar">
  <div class="scard">
    <h3 class="sc-title">&#128202; Markets Snapshot</h3>
    <div>
      <div class="mkt-row"><div><div class="mn">S&amp;P 500</div><div class="mt">SPX</div></div><div><div class="mv">5,282</div><div class="mc dn">&#9660; &minus;2.1%</div></div></div>
      <div class="mkt-row"><div><div class="mn">NASDAQ</div><div class="mt">COMP</div></div><div><div class="mv">16,104</div><div class="mc dn">&#9660; &minus;2.6%</div></div></div>
      <div class="mkt-row"><div><div class="mn">Bitcoin</div><div class="mt">BTC</div></div><div><div class="mv">$84,200</div><div class="mc up">&#9650; +0.9%</div></div></div>
      <div class="mkt-row"><div><div class="mn">Gold</div><div class="mt">XAU</div></div><div><div class="mv">$3,341</div><div class="mc up">&#9650; +2.3%</div></div></div>
      <div class="mkt-row"><div><div class="mn">Oil (WTI)</div><div class="mt">crude</div></div><div><div class="mv">$65.40</div><div class="mc up">&#9650; +4.1%</div></div></div>
    </div>
  </div>
  <div class="scard">
    <h3 class="sc-title">&#128293; Most Read Today</h3>
    <ul class="tlist">""" + trending + """</ul>
  </div>
  <div class="scard" style="background:linear-gradient(135deg,#0d1117,#1e1060);border-color:transparent">
    <p style="font-size:.63rem;font-weight:700;letter-spacing:.13em;text-transform:uppercase;color:var(--pink);margin-bottom:5px">&#128236; Newsletter</p>
    <p style="font-family:'DM Serif Display',serif;font-size:1rem;color:#fff;margin-bottom:5px">5 stories. Every morning.</p>
    <p style="font-size:.74rem;color:#6b7280;margin-bottom:13px;line-height:1.5">Updated daily at 8am PST.</p>
    <input type="email" placeholder="your@email.com" style="width:100%;padding:8px 12px;border-radius:8px;border:1.5px solid rgba(255,255,255,.1);background:rgba(255,255,255,.06);color:#fff;font-family:'DM Sans',sans-serif;font-size:.78rem;outline:none;margin-bottom:7px"/>
    <button onclick="subscribe()" style="width:100%;background:var(--pink);color:#fff;border:none;border-radius:8px;padding:8px;font-family:'DM Sans',sans-serif;font-weight:700;font-size:.78rem;cursor:pointer">Subscribe Free &#8594;</button>
  </div>
</aside>
</div>
<footer>
  <div class="fi">
    <div class="ft">
      <div class="fb">
        <a href="#" class="logo"><div class="logo-sq"></div><span class="logo-txt">Daily Digest</span></a>
        <p>Your news, beautifully illustrated. AI, markets, geopolitics &amp; fashion — refreshed every morning at 8am PST.</p>
      </div>
      <div><p class="fct">Sections</p><ul class="flinks"><li><a href="#">&#129302; AI &amp; Tech</a></li><li><a href="#">&#128200; Markets</a></li><li><a href="#">&#127758; Geopolitics</a></li><li><a href="#">&#10024; Fashion</a></li></ul></div>
      <div><p class="fct">Company</p><ul class="flinks"><li><a href="#">About</a></li><li><a href="#">Newsletter</a></li><li><a href="#">Privacy</a></li><li><a href="#">Contact</a></li></ul></div>
    </div>
    <div class="fbot">
      <p class="fcopy">&copy; 2026 <span>Daily Digest</span> &middot; Updated daily at 8am PST</p>
      <div class="soc"><a class="socbtn" href="#">&#120143;</a><a class="socbtn" href="#">&#128248;</a><a class="socbtn" href="#">in</a><a class="socbtn" href="#">&#128225;</a></div>
    </div>
  </div>
</footer>
<div class="moverlay" id="mo" onclick="cmo(event)">
  <div class="modal">
    <button class="mcls" onclick="closeModal()">&#10005;</button>
    <div class="mem">&#128236;</div>
    <h2>Get the Daily Digest</h2>
    <p>5 hand-picked stories every morning. Join 42,000+ readers.</p>
    <input class="minp" type="email" placeholder="your@email.com"/>
    <button class="mbtn" onclick="subscribe()">Subscribe for Free &#8594;</button>
    <p style="font-size:.68rem;color:var(--tx3);margin-top:9px;text-align:center">No spam. Unsubscribe anytime.</p>
  </div>
</div>
<div class="toast" id="toast"></div>
<script>""" + js + """</script>
</body>
</html>"""


if __name__ == "__main__":
    print(f"Daily Digest update — {TODAY}")
    all_articles = {}
    for cat, params in QUERIES.items():
        print(f"  Fetching {cat}...")
        all_articles[cat] = fetch_articles(cat, params)
    print("Building HTML...")
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_html(all_articles))
    print(f"Done! index.html rebuilt for {TODAY}")
