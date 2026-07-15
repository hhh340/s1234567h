#!/usr/bin/env python3
"""Static site generator for Second Story Vintage.

Reads assets/data/*.json, renders every page from Python-composed HTML
fragments, and writes fully static .html files to the site root. No
server, no client-side content fetching for page content (SEO-first);
JS only adds interactivity on top of already-rendered markup.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # site/
DATA_DIR = os.path.join(ROOT, "assets", "data")

with open(os.path.join(DATA_DIR, "products.json")) as f:
    PRODUCTS = json.load(f)
with open(os.path.join(DATA_DIR, "collections.json")) as f:
    COLLECTIONS = json.load(f)

PRODUCTS_BY_ID = {p["id"]: p for p in PRODUCTS}
COLLECTIONS_BY_ID = {c["id"]: c for c in COLLECTIONS}
for c in COLLECTIONS:
    c["products"] = [p for p in PRODUCTS if p["collection"] == c["id"]]

SITE = {
    "name": "Second Story Vintage",
    "short": "Second Story",
    "tagline": "Every Piece Has A Story.",
    "description": "A boutique thrift and vintage clothing store for considered, one-of-one pieces — editorial fashion with a warm, sustainable heart.",
    "url": "https://www.secondstoryvintage.com",
    "email": "hello@secondstoryvintage.com",
    "phone": "+15035550176",
    "phone_display": "(503) 555-0176",
    "address_line": "128 Alder Street",
    "city": "Portland, OR 97204",
    "instagram": "https://instagram.com/secondstoryvintage",
    "instagram_handle": "@secondstoryvintage",
    "pinterest": "https://pinterest.com/secondstoryvintage",
    "facebook": "https://facebook.com/secondstoryvintage",
    "hours": [
        ("Tuesday – Friday", "11:00 AM – 7:00 PM"),
        ("Saturday", "10:00 AM – 6:00 PM"),
        ("Sunday", "12:00 PM – 5:00 PM"),
        ("Monday", "Closed"),
    ],
}

NAV_LINKS = [
    ("home", "/", "Home"),
    ("shop", "/shop.html", "Shop"),
    ("collections", "/collections.html", "Collections"),
    ("lookbook", "/lookbook.html", "Lookbook"),
    ("sustainability", "/sustainability.html", "Sustainability"),
    ("about", "/about.html", "About"),
    ("faq", "/faq.html", "FAQ"),
    ("contact", "/contact.html", "Contact"),
]


def img(photo_id, w=1200, q=78):
    if photo_id.startswith("http"):
        return photo_id
    return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w={w}&q={q}"


ICONS = {
    "heart": '<path d="M12 21s-7.5-4.6-10-9.3C.5 8 2 4 6 4c2.2 0 3.7 1.2 6 3.6C14.3 5.2 15.8 4 18 4c4 0 5.5 4 4 7.7C19.5 16.4 12 21 12 21Z"/>',
    "bag": '<path d="M6 8h12l-1 12H7L6 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    "close": '<path d="M5 5l14 14M19 5 5 19"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "arrow-right": '<path d="M4 12h16M14 6l6 6-6 6"/>',
    "leaf": '<path d="M5 21c8-1 14-7 15-16-9 1-15 7-16 16Z"/><path d="M5 21c1-4 3-7 6-9"/>',
    "recycle": '<path d="M7 3l3 3-3 3"/><path d="M4 6h9a5 5 0 0 1 5 5v1"/><path d="M17 21l-3-3 3-3"/><path d="M20 18h-9a5 5 0 0 1-5-5v-1"/>',
    "mail": '<path d="M4 5h16v14H4Z"/><path d="M4 5l8 7 8-7"/>',
    "phone": '<path d="M6.5 3h3l1.2 4.2-2.4 1.8c1 2.6 2.7 4.3 5.3 5.3l1.8-2.4L19.6 13v3c0 1.1-.9 2-2 2C10.8 18 6 13.2 6 6.5c0-1.1.9-2 2-2Z"/>',
    "pin": '<path d="M12 21s7-6.5 7-11a7 7 0 1 0-14 0c0 4.5 7 11 7 11Z"/><circle cx="12" cy="10" r="2.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>',
    "star": '<path d="M12 2l2.9 6.6 7.1.6-5.4 4.7 1.7 7-6.3-3.8L5.7 21l1.7-7L2 9.2l7.1-.6L12 2Z"/>',
    "check": '<path d="M5 12l5 5L19 7"/>',
    "funnel": '<path d="M4 4h16l-6 8.5V19l-4 2v-8.5L4 4Z"/>',
    "droplet": '<path d="M12 3s6 7 6 11a6 6 0 1 1-12 0c0-4 6-11 6-11Z"/>',
    "shirt": '<path d="M8 4 4 7l2.3 3L8 9v11h8V9l1.7 1L20 7l-4-3-2 2h-4l-2-2Z"/>',
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="3.6"/><path d="M17.2 6.8h.01"/>',
    "truck": '<path d="M3 7h11v8H3z"/><path d="M14 10h4l3 3v2h-7z"/><circle cx="7" cy="18" r="1.6"/><circle cx="18" cy="18" r="1.6"/>',
    "shield": '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3Z"/><path d="M9 12l2 2 4-4"/>',
    "map": '<path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2Z"/><path d="M9 4v14M15 6v14"/>',
}


def icon(name, cls=""):
    body = ICONS.get(name, "")
    cls_attr = f' class="{cls}"' if cls else ""
    return (
        f'<svg{cls_attr} viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


def money(n):
    return f"${n:,.0f}"


# --------------------------------------------------------------------------
# Shared chrome: header, mobile menu, drawers, footer
# --------------------------------------------------------------------------

CURRENT = ' aria-current="page"'


def render_header(active):
    desktop_links = "".join(
        f'<a href="{href}"{CURRENT if key == active else ""}>{label}</a>'
        for key, href, label in NAV_LINKS
    )
    mobile_links = "".join(
        f'<a href="{href}"{CURRENT if key == active else ""}>{label}</a>'
        for key, href, label in NAV_LINKS
    )
    return f"""
<a class="skip-link" href="#main">Skip to content</a>
<div class="announce">Free local pickup in Portland · New drops every Friday</div>
<header class="site-header">
  <div class="container site-header__inner">
    <a href="/" class="wordmark">{SITE['short']}<small>Vintage Goods</small></a>
    <nav class="nav-desktop" aria-label="Primary">{desktop_links}</nav>
    <div class="header-actions">
      <a href="/shop.html" class="icon-btn" aria-label="Search the shop">{icon('search')}</a>
      <button class="icon-btn" type="button" data-drawer-open="wishlist" aria-label="Open wishlist">
        {icon('heart')}<span class="count" data-count="wishlist">0</span>
      </button>
      <button class="icon-btn" type="button" data-drawer-open="bag" aria-label="Open bag">
        {icon('bag')}<span class="count" data-count="bag">0</span>
      </button>
      <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false">
        <span class="bars"><span></span><span></span><span></span></span>
      </button>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu">
  <div class="mobile-menu__top">
    <a href="/" class="wordmark">{SITE['short']}<small>Vintage Goods</small></a>
    <button class="icon-btn" type="button" data-drawer-close aria-label="Close menu" onclick="document.documentElement.classList.remove('nav-open')">{icon('close')}</button>
  </div>
  <nav aria-label="Mobile">{mobile_links}</nav>
  <div class="mobile-menu__foot">
    <a href="{SITE['instagram']}" class="link">Instagram</a>
    <a href="/contact.html" class="link">Contact</a>
  </div>
</div>
"""


def render_drawers():
    return f"""
<div class="drawer" data-drawer="wishlist" aria-label="Wishlist" role="dialog" aria-modal="true">
  <div class="drawer__head">
    <h2>Wishlist</h2>
    <button class="icon-btn" type="button" data-drawer-close aria-label="Close wishlist">{icon('close')}</button>
  </div>
  <div class="drawer__body" data-drawer-body="wishlist"></div>
</div>
<div class="drawer" data-drawer="bag" aria-label="Bag" role="dialog" aria-modal="true">
  <div class="drawer__head">
    <h2>Your Bag</h2>
    <button class="icon-btn" type="button" data-drawer-close aria-label="Close bag">{icon('close')}</button>
  </div>
  <div class="drawer__body" data-drawer-body="bag"></div>
  <div class="drawer__foot" data-drawer-foot="bag" style="display:none">
    <div class="drawer-summary-row"><span>Subtotal</span><span data-bag-total>$0</span></div>
    <p class="cursor-note" style="margin-bottom:1rem">Shipping calculated at checkout · Free local pickup in Portland</p>
    <a href="/checkout.html" class="btn btn-primary btn-block">Checkout</a>
  </div>
</div>
"""


def render_footer():
    cols = f"""
    <div class="footer-col">
      <h4>Shop</h4>
      <ul>
        <li><a href="/shop.html?gender=women">Women</a></li>
        <li><a href="/shop.html?gender=men">Men</a></li>
        <li><a href="/shop.html?type=outerwear">Outerwear</a></li>
        <li><a href="/shop.html?type=denim">Denim</a></li>
        <li><a href="/shop.html?tier=luxury">Luxury Vintage</a></li>
        <li><a href="/shop.html?tier=designer">Designer Finds</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Explore</h4>
      <ul>
        <li><a href="/collections.html">Collections</a></li>
        <li><a href="/lookbook.html">Lookbook</a></li>
        <li><a href="/sustainability.html">Sustainability</a></li>
        <li><a href="/about.html">About</a></li>
        <li><a href="/faq.html">FAQ</a></li>
      </ul>
    </div>
    <div class="footer-col">
      <h4>Visit</h4>
      <ul>
        <li>{SITE['address_line']}<br>{SITE['city']}</li>
        <li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
        <li><a href="tel:{SITE['phone']}">{SITE['phone_display']}</a></li>
        <li><a href="/contact.html">Get Directions</a></li>
      </ul>
    </div>
    """
    return f"""
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="/" class="wordmark">{SITE['short']}<small>Vintage Goods</small></a>
        <p>{SITE['description']}</p>
        <div class="footer-social">
          <a href="{SITE['instagram']}" class="icon-btn" aria-label="Instagram" style="border:1px solid var(--line-strong)">{icon('instagram')}</a>
          <a href="{SITE['facebook']}" class="icon-btn" aria-label="Facebook" style="border:1px solid var(--line-strong)">{icon('bag')}</a>
        </div>
      </div>
      {cols}
    </div>
    <div class="footer-bottom">
      <span>&copy; <span id="year">2026</span> {SITE['name']}. All rights reserved.</span>
      <span>Made with care in Portland, Oregon</span>
    </div>
  </div>
</footer>
<button class="back-to-top" type="button" aria-label="Back to top">{icon('arrow-right', 'rotate-up')}</button>
"""


# --------------------------------------------------------------------------
# Product / collection components
# --------------------------------------------------------------------------

def render_price(p):
    was = f'<span class="was">{money(p["originalPrice"])}</span>' if p.get("originalPrice") else ""
    return f'{was}{money(p["price"])}'


def render_badges(p):
    out = []
    if p.get("isNew"):
        out.append('<span class="badge badge--new">New In</span>')
    if p["tier"] == "luxury":
        out.append('<span class="badge badge--luxury">Luxury Vintage</span>')
    if p["tier"] == "designer":
        out.append(f'<span class="badge badge--designer">{p["brand"] or "Designer"}</span>')
    return "".join(out)


def render_card(p, reveal=True):
    href = f"/product/{p['id']}.html"
    img_a = img(p["images"][0], 700)
    img_b = img(p["images"][1] if len(p["images"]) > 1 else p["images"][0], 700)
    reveal_cls = " reveal" if reveal else ""
    return f"""
<article class="card{reveal_cls}" data-id="{p['id']}" data-gender="{p['gender']}" data-type="{p['type']}" data-tier="{p['tier']}" data-price="{p['price']}" data-new="{1 if p.get('isNew') else 0}" data-featured="{1 if p.get('featured') else 0}" data-name="{p['name'].lower()}">
  <div class="card__frame">
    <a href="{href}" aria-label="{p['name']}, {money(p['price'])}">
      <img class="img-a" src="{img_a}" alt="{p['name']} — {p['era']} {p['color']}, {p['condition']} condition" loading="lazy" width="700" height="875">
      <img class="img-b" src="{img_b}" alt="" loading="lazy" width="700" height="875" aria-hidden="true">
    </a>
    <div class="card__badges">{render_badges(p)}</div>
    <button class="card__wish" type="button" data-wish-id="{p['id']}" aria-label="Save {p['name']} to wishlist">{icon('heart')}</button>
    <div class="card__quickadd"><button class="btn btn-secondary btn-sm btn-block" type="button" data-add-to-bag="{p['id']}" data-size="{p['size']}">Add to Bag</button></div>
  </div>
  <div class="card__body">
    <div class="card__top">
      <a href="{href}" class="card__name link">{p['name']}</a>
      <div class="card__price">{render_price(p)}</div>
    </div>
    <div class="card__meta">{p['era']} · {p['condition']} · Size {p['size']}</div>
  </div>
</article>
"""


def render_grid(products, reveal=True):
    return "".join(render_card(p, reveal) for p in products)


PRODUCT_MAP_CACHE = None


def product_map_json():
    global PRODUCT_MAP_CACHE
    if PRODUCT_MAP_CACHE is None:
        m = {}
        for p in PRODUCTS:
            m[p["id"]] = {
                "name": p["name"],
                "price": p["price"],
                "img": img(p["images"][0], 200),
                "href": f"/product/{p['id']}.html",
                "era": p["era"],
            }
        PRODUCT_MAP_CACHE = json.dumps(m, separators=(",", ":"))
    return PRODUCT_MAP_CACHE


# --------------------------------------------------------------------------
# Base template
# --------------------------------------------------------------------------

BASE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESCRIPTION__">
<link rel="canonical" href="__CANONICAL__">
<meta name="theme-color" content="#f7f1e6">
<meta name="robots" content="__ROBOTS__">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/favicon.svg">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<meta property="og:type" content="website">
<meta property="og:site_name" content="__SITE_NAME__">
<meta property="og:title" content="__OG_TITLE__">
<meta property="og:description" content="__DESCRIPTION__">
<meta property="og:image" content="__OG_IMAGE__">
<meta property="og:url" content="__CANONICAL__">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="__OG_TITLE__">
<meta name="twitter:description" content="__DESCRIPTION__">
<meta name="twitter:image" content="__OG_IMAGE__">
<link rel="stylesheet" href="/assets/css/style.css">
__JSONLD__
</head>
<body class="__BODY_CLASS__">
__HEADER__
__DRAWERS__
<main id="main">
__CONTENT__
</main>
__FOOTER__
<script type="application/json" id="ssv-data">__PRODUCT_MAP__</script>
<script src="/assets/js/img.js"></script>
<script src="/assets/js/cart.js"></script>
<script src="/assets/js/main.js"></script>
__EXTRA_SCRIPTS__
</body>
</html>
"""


def ldjson(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, separators=(",", ":"))}</script>'


def base_business_ld():
    return {
        "@context": "https://schema.org",
        "@type": "ClothingStore",
        "name": SITE["name"],
        "description": SITE["description"],
        "url": SITE["url"],
        "telephone": SITE["phone"],
        "email": SITE["email"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": SITE["address_line"],
            "addressLocality": "Portland",
            "addressRegion": "OR",
            "postalCode": "97204",
            "addressCountry": "US",
        },
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "11:00", "closes": "19:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "10:00", "closes": "18:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Sunday", "opens": "12:00", "closes": "17:00"},
        ],
        "sameAs": [SITE["instagram"], SITE["facebook"]],
    }


def render_page(path, active, title, description, content, og_image=None, extra_ld=None, extra_scripts="", body_class="", noindex=False):
    canonical = SITE["url"] + path
    og = og_image or img(PRODUCTS[0]["images"][0], 1200)
    ld_list = [base_business_ld()]
    if extra_ld:
        ld_list.extend(extra_ld if isinstance(extra_ld, list) else [extra_ld])
    jsonld_html = "\n".join(ldjson(x) for x in ld_list)
    html = (
        BASE.replace("__TITLE__", title)
        .replace("__DESCRIPTION__", description)
        .replace("__ROBOTS__", "noindex, nofollow" if noindex else "index, follow")
        .replace("__CANONICAL__", canonical)
        .replace("__SITE_NAME__", SITE["name"])
        .replace("__OG_TITLE__", title)
        .replace("__OG_IMAGE__", og)
        .replace("__JSONLD__", jsonld_html)
        .replace("__BODY_CLASS__", body_class)
        .replace("__HEADER__", render_header(active))
        .replace("__DRAWERS__", render_drawers())
        .replace("__CONTENT__", content)
        .replace("__FOOTER__", render_footer())
        .replace("__PRODUCT_MAP__", product_map_json())
        .replace("__EXTRA_SCRIPTS__", extra_scripts)
    )
    return html


def write(path, html):
    full = os.path.join(ROOT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(html)


def page_header(eyebrow, title, deck, crumbs):
    crumb_html = " <span>/</span> ".join(
        f'<a href="{href}" class="link">{label}</a>' if href else f"<span>{label}</span>" for label, href in crumbs
    )
    return f"""
<div class="page-header">
  <div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb">{crumb_html}</nav>
    <p class="eyebrow">{eyebrow}</p>
    <h1>{title}</h1>
    <p>{deck}</p>
  </div>
</div>
"""


# --------------------------------------------------------------------------
# Shared marketing blocks (reused across pages)
# --------------------------------------------------------------------------

VALUES = [
    ("shield", "Authenticated & Graded", "Every luxury or designer piece is checked for authenticity and hand-graded for condition before it ever reaches the rail."),
    ("recycle", "Slow Fashion, On Purpose", "We buy less, choose carefully, and restore what's worth restoring. No overproduction, no landfill-bound deadstock."),
    ("heart", "Give Every Piece A Second Story", "A portion of every sale funds textile recycling programs and local community clothing drives across Portland."),
]


def render_values():
    cards = "".join(
        f"""<div class="value-card reveal reveal-d{i+1}">
              <div class="value-card__icon">{icon(name, '')}</div>
              <h3>{title}</h3>
              <p>{body}</p>
            </div>"""
        for i, (name, title, body) in enumerate(VALUES)
    )
    return f"""
<section class="section">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Why Second Story</p>
        <h2>Considered pieces, <em style="font-style:italic">honestly</em> sourced.</h2>
      </div>
      <p>We hand-select every piece from estate sales, mill closeouts, and private archives — nothing arrives here by accident.</p>
    </div>
    <div class="value-grid">{cards}</div>
  </div>
</section>
"""


STATS = [
    ("14208", 0, "Garments", "Rescued From Landfill"),
    ("2.6", 1, "M Liters", "Water Saved Vs. New"),
    ("86", 0, "Tons CO₂e", "Emissions Avoided"),
    ("9400", 0, "Members", "In Our Repeat-Wear Community"),
]


def render_stats(compact=False):
    items = "".join(
        f"""<div class="stat reveal reveal-d{i+1}">
              <div class="stat__num"><span data-count-to="{val}" data-decimals="{dec}">0</span><span class="stat__unit">{suffix}</span></div>
              <p class="stat__label">{label}</p>
            </div>"""
        for i, (val, dec, suffix, label) in enumerate(STATS)
    )
    if compact:
        head = """<div class="section-head"><div><p class="eyebrow">Impact, Measured</p><h2>Small shop. Real numbers.</h2></div><a href="/sustainability.html" class="link-arrow">Read Our Full Impact """ + icon('arrow-right') + "</a></div>"
    else:
        head = """<div class="section-head"><div><p class="eyebrow">Impact, Measured</p><h2>What Leaving Fast Fashion Actually Saves</h2></div><p>Updated quarterly, no rounding up — every number here is tracked back to an actual garment that came through our door.</p></div>"""
    return f"""
<section class="section grain" style="background:var(--surface-alt)">
  <div class="container">
    {head}
    <div class="stat-grid">{items}</div>
  </div>
</section>
"""


INSTAGRAM_POSTS = [
    ("1637228393246-c38a4b3d2011", "42"), ("1652904872936-f85e04e26a97", "108"),
    ("1727515192207-3dc860bfd773", "76"), ("1611312449408-fcece27cdbb7", "63"),
    ("1735508533799-3df68495a69a", "91"), ("1718622795525-2295971921ba", "54"),
]


def render_instagram():
    tiles = "".join(
        f"""<a class="insta-tile" href="{SITE['instagram']}" target="_blank" rel="noopener">
              <img src="{img(pid, 500)}" alt="Styled vintage look shared on Instagram" loading="lazy" width="500" height="500">
              {icon('instagram')}
            </a>"""
        for pid, likes in INSTAGRAM_POSTS
    )
    return f"""
<section class="section--tight">
  <div class="container">
    <div class="section-head" style="margin-bottom:2.5rem">
      <div><p class="eyebrow">Follow Along</p><h2>{SITE['instagram_handle']}</h2></div>
      <a href="{SITE['instagram']}" class="link-arrow" target="_blank" rel="noopener">View Profile {icon('arrow-right')}</a>
    </div>
  </div>
  <div class="insta-grid">{tiles}</div>
</section>
"""


def render_newsletter():
    return f"""
<section class="newsletter section grain">
  <div class="container">
    <div class="two-col" style="align-items:center">
      <div class="reveal">
        <p class="eyebrow" style="color:var(--sand)">Stay In The Loop</p>
        <h2>New drops land<br>every Friday.</h2>
        <p>Join the list for first access to new arrivals, restocks on archive pieces, and the occasional styling note.</p>
        <form class="newsletter-form" data-newsletter-form novalidate>
          <label class="visually-hidden" for="nl-email">Email address</label>
          <input id="nl-email" type="email" name="email" placeholder="you@email.com" required autocomplete="email">
          <button class="btn btn-outline-light" type="submit">Subscribe</button>
        </form>
        <p class="newsletter-note">No spam. Unsubscribe anytime. We read every reply.</p>
        <div class="newsletter-success" role="status">{icon('check')} <span>You're on the list — welcome in.</span></div>
      </div>
    </div>
  </div>
</section>
"""


def render_visit_teaser():
    hours_rows = "".join(f"<li><span>{d}</span><span>{h}</span></li>" for d, h in SITE["hours"])
    return f"""
<section class="section">
  <div class="container">
    <div class="two-col" style="align-items:center">
      <div class="reveal">
        <div class="gallery__main" style="aspect-ratio:4/3">
          <img src="{img('1632195217465-4f334314762f', 1100)}" alt="Inside the Second Story Vintage storefront, racks of curated clothing" loading="lazy" width="1100" height="825">
        </div>
      </div>
      <div class="reveal reveal-d2">
        <p class="eyebrow">Visit The Shop</p>
        <h2 style="font-size:var(--fs-display-m);margin-top:.6rem">Come try it on before you take it home.</h2>
        <p style="color:var(--text-muted);margin-top:1rem;max-width:44ch">Every piece photographed here is on the floor in Portland. Hold something with the bag, then swing by — or let us know and we'll set it aside.</p>
        <ul class="hours-list">{hours_rows}</ul>
        <div style="margin-top:1.75rem;display:flex;gap:1rem;flex-wrap:wrap">
          <a href="/contact.html" class="btn btn-primary">Get Directions</a>
          <a href="/faq.html" class="btn btn-secondary">Read The FAQ</a>
        </div>
      </div>
    </div>
  </div>
</section>
"""


def build_home():
    hero = f"""
<section class="hero grain">
  <div class="hero__media">
    <img src="{img('1762110109737-b0b9d7ff9d72', 2000, 72)}" alt="Model in a rust-toned vintage coat standing in soft autumn light" fetchpriority="high">
  </div>
  <div class="container hero__content">
    <p class="eyebrow hero__eyebrow">Portland, Est. 2016</p>
    <h1 class="hero__title">Every Piece<br>Has A <em>Story.</em></h1>
    <p class="hero__deck">Second Story Vintage is a boutique of considered secondhand clothing — hand-picked, condition-graded, and restored for whoever's next.</p>
    <div class="hero__actions">
      <a href="/shop.html" class="btn btn-primary">Shop The Edit</a>
      <a href="/lookbook.html" class="btn btn-outline-light">View Lookbook</a>
    </div>
  </div>
  <div class="hero__scroll"><span>Scroll</span><span class="dot">{icon('arrow-right', 'rotate-down')}</span></div>
</section>
"""

    feature_items = "".join(
        f"""<a class="feature-tile reveal" href="/collection/{c['id']}.html">
              <img src="{img(c['image'], 900)}" alt="{c['name']} — {c['tagline']}" loading="lazy" width="900" height="1125">
              <div class="feature-tile__label">
                <p class="eyebrow">Collection</p>
                <h3>{c['name']}</h3>
                <span class="count">{len(c['products'])} Pieces</span>
              </div>
            </a>"""
        for c in COLLECTIONS
    )
    featured_collections = f"""
<section class="section">
  <div class="container">
    <div class="section-head">
      <div><p class="eyebrow">Shop By Story</p><h2>Featured Collections</h2></div>
      <a href="/collections.html" class="link-arrow">View All Collections {icon('arrow-right')}</a>
    </div>
    <div class="feature-grid">{feature_items}</div>
  </div>
</section>
"""

    new_arrivals = [p for p in PRODUCTS if p.get("isNew")][:8]
    newest = f"""
<section class="section" style="background:var(--surface-alt)">
  <div class="container">
    <div class="section-head">
      <div><p class="eyebrow">Fresh On The Rail</p><h2>Newest Arrivals</h2></div>
      <a href="/shop.html?sort=newest" class="link-arrow">Shop New Arrivals {icon('arrow-right')}</a>
    </div>
    <div class="product-grid" data-product-grid>{render_grid(new_arrivals)}</div>
  </div>
</section>
"""

    style_photos = [
        ("1762110109842-f33e96e00f84", "Layered Neutrals", "the-autumn-archive"),
        ("1727515546577-f7d82a47b51d", "Shearling & Denim", "denim-diaries"),
        ("1770733530182-cf94277c3cf7", "The Archive Edit", "the-luxury-edit"),
    ]
    style_tiles = "".join(
        f"""<a class="feature-tile reveal" href="/lookbook.html" style="aspect-ratio:3/4">
              <img src="{img(pid, 800)}" alt="{title} styling inspiration" loading="lazy" width="800" height="1067">
              <div class="feature-tile__label"><h3 style="font-size:1.3rem">{title}</h3></div>
            </a>"""
        for pid, title, _ in style_photos
    )
    style_inspiration = f"""
<section class="section">
  <div class="container">
    <div class="section-head">
      <div><p class="eyebrow">The Edit</p><h2>Style Inspiration</h2></div>
      <a href="/lookbook.html" class="link-arrow">Full Lookbook {icon('arrow-right')}</a>
    </div>
    <div class="feature-grid feature-grid--even">{style_tiles}</div>
  </div>
</section>
"""

    content = (
        hero
        + featured_collections
        + newest
        + style_inspiration
        + render_values()
        + render_stats(compact=True)
        + render_instagram()
        + render_visit_teaser()
        + render_newsletter()
    )

    html = render_page(
        path="/",
        active="home",
        title=f"{SITE['name']} — {SITE['tagline']}",
        description=SITE["description"],
        content=content,
        og_image=img("1762110109737-b0b9d7ff9d72", 1200),
        extra_scripts='<script src="/assets/js/forms.js"></script>',
    )
    write("/index.html", html)


# --------------------------------------------------------------------------
# Shop
# --------------------------------------------------------------------------

FILTER_GROUPS = [
    ("gender", "Gender", [("women", "Women"), ("men", "Men")]),
    ("type", "Category", [("outerwear", "Outerwear"), ("denim", "Denim"), ("accessories", "Accessories"), ("shoes", "Shoes")]),
    ("tier", "Tier", [("luxury", "Luxury Vintage"), ("designer", "Designer Finds")]),
]


def render_filters():
    groups_html = ""
    for key, label, options in FILTER_GROUPS:
        rows = ""
        for value, opt_label in options:
            count = sum(1 for p in PRODUCTS if p[key] == value)
            rows += f"""<label class="check">
                <input type="checkbox" name="{key}" value="{value}" data-filter>
                <span>{opt_label}</span><span class="n">{count}</span>
              </label>"""
        groups_html += f'<div class="filter-group"><h3>{label}</h3>{rows}</div>'
    return f"""
<aside class="filters drawer" data-drawer="filters" aria-label="Filter products">
  <div class="drawer__head">
    <h2>Filters</h2>
    <button class="icon-btn" type="button" data-drawer-close aria-label="Close filters">{icon('close')}</button>
  </div>
  <div class="filters-scroll">
    {groups_html}
    <button class="btn btn-secondary btn-sm btn-block" type="button" data-clear-filters style="margin-top:1.5rem;display:none">Clear All Filters</button>
  </div>
</aside>
"""


def build_shop():
    content = page_header(
        "The Full Rail",
        "Shop The Collection",
        "Every piece is one of one. Filter by category, gender, or tier — or search for exactly what you have in mind.",
        [("Home", "/"), ("Shop", None)],
    )
    content += f"""
<section class="section--tight">
  <div class="container">
    <div class="shop-layout">
      {render_filters()}
      <div>
        <button class="btn btn-secondary filters-toggle" type="button" data-drawer-open="filters">{icon('funnel')} Filters</button>
        <div class="shop-toolbar">
          <div class="search-field">
            {icon('search')}
            <label class="visually-hidden" for="shop-search">Search products</label>
            <input id="shop-search" type="search" placeholder="Search pieces…" data-shop-search autocomplete="off">
          </div>
          <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
            <span class="result-count" data-result-count>{len(PRODUCTS)} pieces</span>
            <div class="sort-field">
              <label class="visually-hidden" for="shop-sort">Sort by</label>
              <select id="shop-sort" data-shop-sort>
                <option value="featured">Featured</option>
                <option value="newest">Newest</option>
                <option value="price-asc">Price: Low to High</option>
                <option value="price-desc">Price: High to Low</option>
              </select>
            </div>
          </div>
        </div>
        <div class="active-filters-bar">
          <div class="active-filters" data-active-filters></div>
          <button class="chip-clear" type="button" data-clear-filters>Clear all</button>
        </div>
        <div class="product-grid" data-product-grid>{render_grid(PRODUCTS, reveal=False)}</div>
        <div class="empty-state" data-empty-state style="display:none">
          {icon('search')}
          <p>No pieces match those filters yet.<br>Try clearing a filter or searching something else.</p>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    html = render_page(
        path="/shop.html",
        active="shop",
        title=f"Shop All — {SITE['name']}",
        description="Browse the full rail: women's and men's vintage outerwear, denim, accessories, and shoes, plus authenticated luxury vintage and designer finds.",
        content=content,
        og_image=img(PRODUCTS[0]["images"][0], 1200),
        extra_scripts='<script src="/assets/js/shop.js"></script>',
    )
    write("/shop.html", html)


# --------------------------------------------------------------------------
# Product detail
# --------------------------------------------------------------------------

def care_tip(material):
    m = material.lower()
    if "suede" in m:
        return "Spot clean only with a suede brush. Keep away from water and direct heat."
    if "shearling" in m:
        return "Spot clean only. We recommend a professional shearling cleaner for deep cleans."
    if "leather" in m:
        return "Condition every few months with a leather balm. Wipe clean with a soft, dry cloth."
    if "denim" in m or "duck" in m:
        return "Machine wash cold, inside out, with like colors. Hang to dry to preserve the fade."
    if "wool" in m:
        return "Dry clean recommended. Steam to refresh the fabric between wears."
    if "silk" in m:
        return "Dry clean only. Store away from direct sunlight to protect the print."
    if "straw" in m or "woven" in m:
        return "Wipe clean with a dry cloth. Store flat or upright, away from moisture."
    if "canvas" in m:
        return "Spot clean or machine wash cold. Air dry away from direct heat."
    return "Treat gently — this piece has already survived one lifetime. When in doubt, spot clean."


TYPE_LABELS = {"outerwear": "Outerwear", "denim": "Denim", "accessories": "Accessories", "shoes": "Shoes"}


def render_accordion(items, single=True):
    group_attr = " data-accordion-single" if single else ""
    rows = ""
    for i, (title, body) in enumerate(items):
        rows += f"""<div class="accordion-item{' is-open' if i == 0 else ''}">
          <button class="accordion-trigger" type="button" aria-expanded="{'true' if i == 0 else 'false'}">{title}{icon('plus')}</button>
          <div class="accordion-panel" style="{'max-height:600px' if i == 0 else ''}">
            <div class="accordion-panel__inner">{body}</div>
          </div>
        </div>"""
    return f'<div{group_attr}>{rows}</div>'


def build_product_page(p):
    href = f"/product/{p['id']}.html"
    gallery_imgs = [img(pid, 1100) for pid in p["images"]]
    thumbs = "".join(
        f"""<button type="button" class="{'is-active' if i == 0 else ''}" data-gallery-thumb="{url}" aria-label="View image {i+1}">
              <img src="{img(p['images'][i], 200)}" alt="" loading="lazy" width="200" height="250">
            </button>"""
        for i, url in enumerate(gallery_imgs)
    )

    meta_rows = "".join(
        f"<div><dt>{k}</dt><dd>{v}</dd></div>"
        for k, v in [
            ("Era", p["era"]), ("Condition", p["condition"]), ("Color", p["color"]),
            ("Material", p["material"]), ("Size", p["size"]), ("SKU", p["sku"]),
        ]
    )

    details_list = "<ul>" + "".join(f"<li>{d}</li>" for d in p["details"]) + "</ul>"
    accordion = render_accordion([
        ("Details &amp; Condition", details_list),
        ("Measurements &amp; Fit", f"<p>This is a genuine one-of-one vintage piece in size {p['size']}, hand-graded as <strong>{p['condition']}</strong>. Fit runs true to its era — if you're unsure how that compares to modern sizing, message us before reserving and we'll walk you through exact measurements.</p>"),
        ("Care Instructions", f"<p>{care_tip(p['material'])}</p>"),
        ("Shipping &amp; Pickup", "<p>Check out securely online — free local pickup on Alder Street in Portland (usually ready within 2 hours), standard tracked shipping in 3–5 business days (free over $200), or express in 1–2. Luxury pieces always ship insured.</p>"),
    ])

    same_collection = [x for x in PRODUCTS if x["collection"] == p["collection"] and x["id"] != p["id"]]
    same_type = [x for x in PRODUCTS if x["type"] == p["type"] and x["id"] != p["id"] and x not in same_collection]
    related = (same_collection + same_type)[:4]

    badges = render_badges(p)
    eyebrow_bits = f'<span class="eyebrow">{p["era"]} · {TYPE_LABELS[p["type"]]}</span>'

    content = page_header_compact_breadcrumb([
        ("Home", "/"), ("Shop", "/shop.html"), (TYPE_LABELS[p["type"]], f"/shop.html?type={p['type']}"), (p["name"], None)
    ])

    content += f"""
<section class="section--tight">
  <div class="container">
    <div class="product-detail">
      <div class="reveal">
        <div class="gallery__main"><img data-gallery-main src="{gallery_imgs[0]}" alt="{p['name']} — {p['era']} {p['color']} {TYPE_LABELS[p['type']]}, {p['condition']} condition" width="1100" height="1375"></div>
        <div class="gallery__thumbs">{thumbs}</div>
      </div>
      <div class="reveal reveal-d2">
        <div class="pd-eyebrow">{eyebrow_bits}{badges}</div>
        <h1 class="pd-title">{p['name']}</h1>
        <div class="pd-price">{render_price(p)}</div>
        <p class="pd-desc">{p['description']}</p>
        <dl class="pd-meta-grid">{meta_rows}</dl>
        <div class="pd-actions">
          <button class="btn btn-primary" type="button" data-add-to-bag="{p['id']}" data-size="{p['size']}">Add to Bag — {money(p['price'])}</button>
          <button class="icon-btn" type="button" data-wish-id="{p['id']}" aria-label="Save {p['name']} to wishlist">{icon('heart')}</button>
        </div>
        <div class="pd-note">{icon('shield')}<span>Authenticity checked and condition-graded by our team. Free local pickup in Portland, or insured, tracked shipping nationwide — free on orders over $200.</span></div>
        <div style="margin-top:2rem">{accordion}</div>
      </div>
    </div>
  </div>
</section>
"""

    if related:
        content += f"""
<section class="section" style="background:var(--surface-alt)">
  <div class="container">
    <div class="section-head"><div><p class="eyebrow">You Might Also Love</p><h2>Related Pieces</h2></div></div>
    <div class="product-grid" data-product-grid>{render_grid(related, reveal=False)}</div>
  </div>
</section>
"""

    product_ld = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": p["name"],
        "image": gallery_imgs,
        "description": p["description"],
        "sku": p["sku"],
        "brand": {"@type": "Brand", "name": p["brand"] or SITE["name"]},
        "offers": {
            "@type": "Offer",
            "priceCurrency": "USD",
            "price": p["price"],
            "availability": "https://schema.org/LimitedAvailability",
            "url": SITE["url"] + href,
        },
    }
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Shop", "item": SITE["url"] + "/shop.html"},
            {"@type": "ListItem", "position": 2, "name": TYPE_LABELS[p["type"]], "item": SITE["url"] + f"/shop.html?type={p['type']}"},
            {"@type": "ListItem", "position": 3, "name": p["name"], "item": SITE["url"] + href},
        ],
    }

    html = render_page(
        path=href,
        active="shop",
        title=f"{p['name']} — {SITE['name']}",
        description=p["description"],
        content=content,
        og_image=gallery_imgs[0],
        extra_ld=[product_ld, breadcrumb_ld],
        extra_scripts='<script src="/assets/js/product.js"></script>',
    )
    write(href, html)


def page_header_compact_breadcrumb(crumbs):
    crumb_html = " <span>/</span> ".join(
        f'<a href="{href}" class="link">{label}</a>' if href else f"<span>{label}</span>" for label, href in crumbs
    )
    return f"""
<div class="container" style="padding-top:calc(var(--sp-8) + 1rem);padding-bottom:1rem">
  <nav class="breadcrumb" aria-label="Breadcrumb">{crumb_html}</nav>
</div>
"""


# --------------------------------------------------------------------------
# Collections
# --------------------------------------------------------------------------

def build_collections_index():
    content = page_header(
        "Shop By Story",
        "Collections",
        "Every collection is a small, hand-curated edit — grouped by era, category, or the story behind how we found it.",
        [("Home", "/"), ("Collections", None)],
    )
    spreads = ""
    for i, c in enumerate(COLLECTIONS):
        reverse = " reverse" if i % 2 else ""
        idx = str(i + 1).zfill(2)
        spreads += f"""
<div class="spread{reverse} reveal">
  <div class="spread__media">
    <img src="{img(c['image'], 1000)}" alt="{c['name']} collection" loading="lazy" width="1000" height="1250">
  </div>
  <div class="spread__copy">
    <span class="spread__index">{idx} / {str(len(COLLECTIONS)).zfill(2)}</span>
    <p class="eyebrow">{c['tagline']}</p>
    <h2>{c['name']}</h2>
    <p>{c['description']}</p>
    <a href="/collection/{c['id']}.html" class="link-arrow">Shop {len(c['products'])} Pieces {icon('arrow-right')}</a>
  </div>
</div>
"""
    content += f'<section class="section--tight"><div class="container">{spreads}</div></section>'

    html = render_page(
        path="/collections.html",
        active="collections",
        title=f"Collections — {SITE['name']}",
        description="Hand-curated vintage collections: The Autumn Archive, Denim Diaries, The Luxury Vintage Edit, and Sunday Market.",
        content=content,
        og_image=img(COLLECTIONS[0]["image"], 1200),
    )
    write("/collections.html", html)


def build_collection_page(c):
    href = f"/collection/{c['id']}.html"
    content = page_header_compact_breadcrumb([("Home", "/"), ("Collections", "/collections.html"), (c["name"], None)])
    content += f"""
<section class="hero grain" style="min-height:56vh">
  <div class="hero__media"><img src="{img(c['image'], 1800, 72)}" alt="{c['name']} collection"></div>
  <div class="container hero__content" style="padding-block:var(--sp-7)">
    <p class="eyebrow hero__eyebrow">{c['tagline']}</p>
    <h1 class="hero__title" style="font-size:var(--fs-display-l)">{c['name']}</h1>
    <p class="hero__deck">{c['description']}</p>
  </div>
</section>
<section class="section--tight">
  <div class="container">
    <div class="shop-toolbar" style="justify-content:flex-end">
      <span class="result-count">{len(c['products'])} piece{'s' if len(c['products']) != 1 else ''}</span>
    </div>
    <div class="product-grid" data-product-grid>{render_grid(c['products'], reveal=False)}</div>
  </div>
</section>
"""
    others = [x for x in COLLECTIONS if x["id"] != c["id"]]
    other_tiles = "".join(
        f"""<a class="feature-tile reveal" href="/collection/{o['id']}.html">
              <img src="{img(o['image'], 700)}" alt="{o['name']}" loading="lazy" width="700" height="933">
              <div class="feature-tile__label"><p class="eyebrow">Collection</p><h3 style="font-size:1.3rem">{o['name']}</h3></div>
            </a>"""
        for o in others
    )
    content += f"""
<section class="section" style="background:var(--surface-alt)">
  <div class="container">
    <div class="section-head"><div><p class="eyebrow">Keep Exploring</p><h2>More Collections</h2></div></div>
    <div class="feature-grid feature-grid--even">{other_tiles}</div>
  </div>
</section>
"""
    breadcrumb_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Collections", "item": SITE["url"] + "/collections.html"},
            {"@type": "ListItem", "position": 2, "name": c["name"], "item": SITE["url"] + href},
        ],
    }
    html = render_page(
        path=href,
        active="collections",
        title=f"{c['name']} — {SITE['name']}",
        description=c["description"],
        content=content,
        og_image=img(c["image"], 1200),
        extra_ld=breadcrumb_ld,
    )
    write(href, html)


# --------------------------------------------------------------------------
# Lookbook
# --------------------------------------------------------------------------

LOOKBOOK_STORIES = [
    {
        "id": "layered-for-longer-days",
        "tag": "Autumn Story",
        "title": "Layered For Longer Days",
        "copy": "Shearling over denim over knit — the archive coats do their best work in the gap between seasons, when one layer isn't enough and three feels right. Start heavy, peel back as the day warms.",
        "image": "1662532577856-e8ee8b138a8b",
        "cta": ("Shop The Autumn Archive", "/collection/the-autumn-archive.html"),
    },
    {
        "id": "denim-every-decade",
        "tag": "Denim Story",
        "title": "Denim, Every Decade",
        "copy": "A 70s flare doesn't dress like a 90s trucker, and that's the point. We keep the cuts distinct instead of ironing out what makes each era recognizable — mix two decades in one outfit and let the contrast do the talking.",
        "image": "1765697638509-4039f783c2cc",
        "cta": ("Shop Denim Diaries", "/collection/denim-diaries.html"),
    },
    {
        "id": "the-archive-find",
        "tag": "Luxury Story",
        "title": "The Archive Find",
        "copy": "Every rack has one piece worth building a whole look around. This season it's a gabardine trench with storm-shield stitching, styled here with almost nothing else — the coat was doing enough work on its own.",
        "image": "1727515192207-3dc860bfd773",
        "cta": ("Shop The Luxury Vintage Edit", "/collection/the-luxury-edit.html"),
    },
    {
        "id": "sunday-market-uniform",
        "tag": "Weekend Story",
        "title": "Sunday Market Uniform",
        "copy": "Loafers that have already broken in, a suede bag sized for exactly what you need, gold-tone sunglasses that catch the light. Nothing here is precious — it's the uniform for a slow morning that turns into an afternoon.",
        "image": "1700223613081-fff47f71f180",
        "cta": ("Shop Sunday Market", "/collection/sunday-market.html"),
    },
    {
        "id": "off-duty-on-point",
        "tag": "Closing Story",
        "title": "Off Duty, On Point",
        "copy": "The best vintage doesn't look styled — it looks found. We photograph every look the way we'd actually wear it: a little undone, mostly comfortable, and better a year from now than it is today.",
        "image": "1762110108956-6d258ba6c5a0",
        "cta": ("Shop All Pieces", "/shop.html"),
    },
]

LOOKBOOK_STRIP = ["1652904871839-2f815f42cb00", "1606987482451-e921cdf74cad", "1554583826-08610bcb6c3a"]


def build_lookbook():
    content = f"""
<section class="lookbook-hero grain">
  <img src="{img('1779161328871-b123c289bbac', 2000, 72)}" alt="Editorial lookbook cover image, model styled in layered vintage pieces">
  <div class="container">
    <p class="eyebrow" style="color:var(--sand)">Season Two — The Archive</p>
    <h1>Style Inspiration,<br>Straight From The Rail.</h1>
  </div>
</section>
"""
    for i, s in enumerate(LOOKBOOK_STORIES):
        reverse = " reverse" if i % 2 else ""
        content += f"""
<section class="container" id="{s['id']}">
  <div class="spread{reverse} reveal">
    <div class="spread__media">
      <img src="{img(s['image'], 1000)}" alt="{s['title']} — styling story" loading="lazy" width="1000" height="1250">
    </div>
    <div class="spread__copy">
      <span class="spread__index">{str(i+1).zfill(2)} / {str(len(LOOKBOOK_STORIES)).zfill(2)}</span>
      <p class="eyebrow">{s['tag']}</p>
      <h2>{s['title']}</h2>
      <p>{s['copy']}</p>
      <a href="{s['cta'][1]}" class="link-arrow">{s['cta'][0]} {icon('arrow-right')}</a>
    </div>
  </div>
</section>
"""
        if i == 1:
            strip_imgs = "".join(f'<img src="{img(pid, 700)}" alt="Vintage styling detail" loading="lazy" width="700" height="933">' for pid in LOOKBOOK_STRIP)
            content += f'<div class="lookbook-strip reveal">{strip_imgs}</div>'

    content += f"""
<section class="newsletter section grain" style="margin-top:var(--sp-8)">
  <div class="container" style="text-align:center">
    <div class="reveal" style="max-width:640px;margin-inline:auto">
      <p class="eyebrow" style="color:var(--sand);justify-content:center">Ready To Shop The Edit?</p>
      <h2 style="margin-top:.6rem">Every look starts<br>with one good find.</h2>
      <div style="margin-top:2rem">
        <a href="/shop.html" class="btn btn-outline-light">Shop All Pieces</a>
      </div>
    </div>
  </div>
</section>
"""
    html = render_page(
        path="/lookbook.html",
        active="lookbook",
        title=f"Lookbook — {SITE['name']}",
        description="Editorial styling stories from Second Story Vintage — five ways to wear the archive this season.",
        content=content,
        og_image=img("1779161328871-b123c289bbac", 1200),
    )
    write("/lookbook.html", html)


# --------------------------------------------------------------------------
# Sustainability
# --------------------------------------------------------------------------

SOURCING_STEPS = [
    ("Sourcing", "We buy directly from estate sales, mill closeouts, and private archives across the Pacific Northwest — never from mass clothing brokers, so we know exactly where a piece has been."),
    ("Authentication &amp; Grading", "Every luxury or designer item is checked against maker's marks, hardware, and construction details, then hand-graded on our five-point condition scale before it's priced."),
    ("Restoration", "Loose buttons get resewn, leather gets conditioned, denim gets patched where it needs it. We restore to extend a piece's life, never to disguise its age."),
    ("Rehoming", "Priced fairly, photographed honestly, and put back into rotation — with the story of its condition and era included, not hidden."),
]

SUSTAINABILITY_VALUES = [
    ("recycle", "Circular By Design", "Every piece we sell is one that didn't go to a landfill or an incinerator. That's the whole business model, not a side initiative."),
    ("droplet", "Fewer New Resources", "A secondhand garment uses zero new water, cotton, or dye. Buying one here instead of new is the single highest-impact swap in your closet."),
    ("pin", "Local First", "We're a Portland shop sourcing largely from the Pacific Northwest — short supply chains, small footprint, real relationships with the people we buy from."),
]


def build_sustainability():
    content = page_header(
        "Our Promise",
        "Sustainability, Measured Honestly",
        "Secondhand is the original sustainable fashion. Here's exactly how we source, restore, and track the impact of every piece that comes through our door.",
        [("Home", "/"), ("Sustainability", None)],
    )

    content += f"""
<section class="section--tight">
  <div class="container">
    <div class="two-col" style="align-items:center">
      <div class="reveal">
        <div class="gallery__main" style="aspect-ratio:4/5">
          <img src="{img('1637228393246-c38a4b3d2011', 1000)}" alt="Racks of curated vintage clothing inside the Second Story Vintage shop" loading="lazy" width="1000" height="1250">
        </div>
      </div>
      <div class="reveal reveal-d2">
        <p class="eyebrow">Why It Matters</p>
        <h2 style="font-size:var(--fs-display-m);margin-top:.6rem">The most sustainable garment is one that already exists.</h2>
        <div class="prose" style="margin-top:1.25rem">
          <p>The fashion industry produces more carbon emissions than international flights and shipping combined. Almost all of it comes from making new things — growing cotton, running mills, dyeing fabric, shipping garments around the world before they're ever worn.</p>
          <p>Every piece on our rail skips that entire process. It's already been made. Our job is just to find the good stuff, make sure it's authentic and sound, and get it back into someone's rotation.</p>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    content += render_stats(compact=False)

    timeline_items = "".join(
        f"""<div class="timeline-item reveal">
              <p class="eyebrow">Step {i+1}</p>
              <h3>{title}</h3>
              <p>{body}</p>
            </div>"""
        for i, (title, body) in enumerate(SOURCING_STEPS)
    )
    content += f"""
<section class="section">
  <div class="container">
    <div class="section-head"><div><p class="eyebrow">Our Process</p><h2>How A Piece Gets To The Rail</h2></div></div>
    <div class="timeline">{timeline_items}</div>
  </div>
</section>
"""

    value_cards = "".join(
        f"""<div class="value-card reveal reveal-d{i+1}">
              <div class="value-card__icon">{icon(name, '')}</div>
              <h3>{title}</h3>
              <p>{body}</p>
            </div>"""
        for i, (name, title, body) in enumerate(SUSTAINABILITY_VALUES)
    )
    content += f"""
<section class="section" style="background:var(--surface-alt)">
  <div class="container">
    <div class="section-head"><div><p class="eyebrow">What We Stand For</p><h2>Sustainability, Not Marketing</h2></div></div>
    <div class="value-grid">{value_cards}</div>
  </div>
</section>
"""
    content += render_newsletter()

    html = render_page(
        path="/sustainability.html",
        active="sustainability",
        title=f"Sustainability — {SITE['name']}",
        description="How Second Story Vintage sources, authenticates, and restores every piece — plus the real, quarterly-tracked impact numbers behind the shop.",
        content=content,
        og_image=img("1637228393246-c38a4b3d2011", 1200),
        extra_scripts='<script src="/assets/js/forms.js"></script>',
    )
    write("/sustainability.html", html)


# --------------------------------------------------------------------------
# About
# --------------------------------------------------------------------------

BRAND_TIMELINE = [
    ("2016", "A Market Stall Begins", "Second Story started as a folding rack at the Portland Sunday market — thirty pieces, hand-picked from estate sales, sold out of the trunk of a car."),
    ("2018", "First Storefront", "We opened the doors on Alder Street: one room, one steamer, and a promise that every piece would be honestly graded before it went on the rail."),
    ("2021", "The Luxury Vintage Program", "We built an authentication process for designer and luxury pieces, working with a third-party verification service so every archive find is genuinely what we say it is."),
    ("2023", "Community Give-Back", "We began funding local textile recycling and clothing-drive partnerships with a share of every sale — turning purchases into pickup and drop-off programs across Portland."),
    ("2026", "Second Story Today", "Still independently owned, still hand-selecting every single piece — now with a wider rail, a bigger community, and the same rule: no two racks are ever the same."),
]


def build_about():
    content = page_header(
        "Our Story",
        "About Second Story",
        "We started with the belief that secondhand shouldn't mean settling — every piece here was chosen the way you'd choose it yourself, if you had the time to look.",
        [("Home", "/"), ("About", None)],
    )
    content += f"""
<section class="section--tight">
  <div class="container">
    <div class="two-col" style="align-items:center">
      <div class="reveal">
        <div class="gallery__main" style="aspect-ratio:4/5">
          <img src="{img('1554350342-84cbb65fd7c6', 1000)}" alt="Portrait styled in vintage clothing from Second Story Vintage" loading="lazy" width="1000" height="1250">
        </div>
      </div>
      <div class="reveal reveal-d2">
        <p class="eyebrow">The Founder</p>
        <h2 style="font-size:var(--fs-display-m);margin-top:.6rem">"I wanted a shop I'd actually want to dig through."</h2>
        <div class="prose" style="margin-top:1.25rem">
          <p>Second Story Vintage started because its founder was tired of thrifting for eight hours to find one good coat. The idea was simple: do that digging once, for everyone, and grade honestly enough that you can trust a piece before you've even tried it on.</p>
          <p>A decade later, that's still the whole job. We're not a chain and we're not trying to be — just a small team in Portland who'd rather spend a Tuesday steaming a 1970s trench than sourcing another pallet of the same five silhouettes.</p>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    timeline_items = "".join(
        f"""<div class="timeline-item reveal">
              <p class="eyebrow">{year}</p>
              <h3>{title}</h3>
              <p>{body}</p>
            </div>"""
        for year, title, body in BRAND_TIMELINE
    )
    content += f"""
<section class="section" style="background:var(--surface-alt)">
  <div class="container">
    <div class="section-head"><div><p class="eyebrow">Ten Years, Give Or Take</p><h2>How We Got Here</h2></div></div>
    <div class="timeline">{timeline_items}</div>
  </div>
</section>
"""
    content += render_values()
    content += render_visit_teaser()

    html = render_page(
        path="/about.html",
        active="about",
        title=f"About Us — {SITE['name']}",
        description="The story behind Second Story Vintage — a Portland boutique built on honest grading, hand-selected pieces, and a decade of doing the digging so you don't have to.",
        content=content,
        og_image=img("1554350342-84cbb65fd7c6", 1200),
    )
    write("/about.html", html)


# --------------------------------------------------------------------------
# FAQ
# --------------------------------------------------------------------------

FAQ_GROUPS = [
    ("reserving", "Ordering &amp; Payment", [
        ("How does ordering work?", "Add pieces to your bag and check out like any other store — enter your contact, shipping, and card details, and you'll get an order confirmation with a delivery estimate right away. We accept all major cards."),
        ("Can I put a piece on hold without paying?", "Yes. Message us from the Contact page with the SKU and we'll hold it for 48 hours at no cost. If we don't hear back to confirm, it goes back on the rail for someone else."),
        ("Do pieces sell out quickly?", "Often, yes — every piece is one-of-one, so once it's gone, it's gone. We don't restock the exact same item, though similar pieces come through regularly."),
        ("Can I visit and buy in person instead?", "Always. Everything online is also on the floor in Portland — see the Contact page for our current hours."),
    ]),
    ("shipping", "Shipping &amp; Pickup", [
        ("Is local pickup free?", "Yes, free for anyone in the Portland area. We'll confirm a pickup window by email once your reservation is set."),
        ("Do you ship nationwide?", "Yes — we ship across the US within 3 business days of a confirmed reservation. Every shipment is tracked, and luxury vintage or designer pieces are insured."),
        ("Do you ship internationally?", "Not yet, but it's on the roadmap. Join the newsletter and we'll announce it there first."),
        ("How are delicate or luxury pieces packaged?", "Garment bags, acid-free tissue, and a rigid box for anything with structure — bags, shoes, boots. No signature piece travels loose."),
    ]),
    ("returns", "Returns &amp; Condition", [
        ("What if a piece doesn't fit?", "Because every item is one-of-one and secondhand, all sales are final — which is exactly why we grade condition honestly and list real measurements. Message us before reserving if you're unsure."),
        ("What does each condition grade mean?", "Excellent (like-new, no visible wear), Very Good (minor, honest signs of wear), and Good — Loved (noticeable vintage wear that adds character — always disclosed upfront, never a surprise)."),
        ("What if an item arrives different than described?", "That's on us. Contact us within 5 days of delivery and we'll make it right with a refund or store credit."),
        ("Are luxury and designer pieces authenticated?", "Yes — every luxury or designer item is checked against maker's marks and construction details before it's ever listed, and comes with an authentication note."),
    ]),
    ("sizing", "Sizing &amp; Fit", [
        ("Do you use modern sizing?", "No — vintage sizing runs differently by era, so we list actual measurements and era on every product page instead of relying on a size label alone."),
        ("Can I ask for measurements before reserving?", "Always. Message us through Contact with the SKU listed on the product page and we'll send exact measurements same-day."),
        ("Do you carry a range of sizes?", "We carry whatever came through the door that week — sizing varies piece to piece since everything is one-of-one. Filter by category and check individual measurements before reserving."),
    ]),
    ("sustainability", "Sustainability", [
        ("Where do your pieces come from?", "Estate sales, mill closeouts, and private archives, mostly across the Pacific Northwest. See our Sustainability page for the full sourcing process."),
        ("What happens to items you don't put on the rail?", "Anything that doesn't meet our bar for resale gets donated or routed to textile recycling partners — nothing we pull in goes to a landfill."),
        ("Do you take clothing donations from customers?", "Not for resale, since we hand-select every piece ourselves — but we can point you to our community textile recycling partners. Just ask at the shop."),
    ]),
    ("care", "Care", [
        ("How should I care for vintage leather or suede?", "Check the Care Instructions accordion on each product page — generally, leather wants conditioning every few months and suede wants a dry brush, never water."),
        ("Can I machine wash vintage denim?", "Usually cold, inside out, hung to dry to preserve the fade — but always check the specific product page, since some pieces are more delicate than others."),
    ]),
]


def build_faq():
    tabs = "".join(
        f'<button class="faq-tab{" is-active" if i == 0 else ""}" type="button" data-tab-trigger="{gid}">{label}</button>'
        for i, (gid, label, _) in enumerate(FAQ_GROUPS)
    )
    groups = ""
    for i, (gid, label, items) in enumerate(FAQ_GROUPS):
        rows = "".join(
            f"""<div class="faq-item accordion-item{' is-open' if j == 0 else ''}">
                  <button class="accordion-trigger" type="button" aria-expanded="{'true' if j == 0 else 'false'}">{q}{icon('plus')}</button>
                  <div class="accordion-panel" style="{'max-height:400px' if j == 0 else ''}"><div class="accordion-panel__inner"><p>{a}</p></div></div>
                </div>"""
            for j, (q, a) in enumerate(items)
        )
        groups += f'<div class="faq-group{" is-active" if i == 0 else ""}" data-tab-panel="{gid}" data-accordion-single>{rows}</div>'

    content = page_header(
        "Questions, Answered",
        "Frequently Asked Questions",
        "Everything about ordering, shipping, sizing, and how a piece earns a spot on our rail. Can't find it here? Reach out — we answer everything ourselves.",
        [("Home", "/"), ("FAQ", None)],
    )
    content += f"""
<section class="section--tight">
  <div class="container container--narrow">
    <div data-tabs>
      <div class="faq-tabs">{tabs}</div>
      {groups}
    </div>
    <div style="text-align:center;margin-top:var(--sp-8);padding-top:var(--sp-7);border-top:1px solid var(--line)">
      <p class="eyebrow" style="justify-content:center">Still Have Questions?</p>
      <h2 style="font-size:var(--fs-display-s);margin-top:.6rem">We answer every message ourselves.</h2>
      <div style="margin-top:1.5rem"><a href="/contact.html" class="btn btn-primary">Contact Us</a></div>
    </div>
  </div>
</section>
"""
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for _, _, items in FAQ_GROUPS for q, a in items
        ],
    }
    html = render_page(
        path="/faq.html",
        active="faq",
        title=f"FAQ — {SITE['name']}",
        description="Answers to common questions about reserving, shipping, returns, sizing, sustainability, and care at Second Story Vintage.",
        content=content,
        extra_ld=faq_ld,
    )
    write("/faq.html", html)


# --------------------------------------------------------------------------
# Contact
# --------------------------------------------------------------------------

def build_contact():
    hours_rows = "".join(f"<dt>{d}</dt><dd>{h}</dd>" for d, h in SITE["hours"])
    content = page_header(
        "Get In Touch",
        "Contact Us",
        "Questions about a piece, a reservation, or just want to say hi? We read and answer every message ourselves.",
        [("Home", "/"), ("Contact", None)],
    )
    content += f"""
<section class="section--tight">
  <div class="container">
    <div class="contact-grid">
      <div class="reveal">
        <form data-contact-form novalidate>
          <div class="two-col" style="gap:1rem">
            <div class="field">
              <label for="c-name">Name</label>
              <input id="c-name" name="name" type="text" required autocomplete="name">
              <p class="field-error">Please enter your name.</p>
            </div>
            <div class="field">
              <label for="c-email">Email</label>
              <input id="c-email" name="email" type="email" required autocomplete="email">
              <p class="field-error">Please enter a valid email.</p>
            </div>
          </div>
          <div class="field">
            <label for="c-subject">Subject</label>
            <select id="c-subject" name="subject">
              <option value="general">General Question</option>
              <option value="reserve">Reserve / Bag Enquiry</option>
              <option value="sizing">Sizing &amp; Measurements</option>
              <option value="press">Press &amp; Wholesale</option>
            </select>
          </div>
          <div class="field">
            <label for="c-message">Message</label>
            <textarea id="c-message" name="message" required></textarea>
            <p class="field-error">Please enter a message.</p>
          </div>
          <button class="btn btn-primary btn-block" type="submit">Send Message</button>
        </form>
        <div class="form-success" data-contact-success role="status">
          {icon('check')}
          <div><strong>Message sent.</strong><br>We'll get back to you within one business day.</div>
        </div>
      </div>
      <div class="reveal reveal-d2">
        <div class="info-card">
          <h3>Visit The Shop</h3>
          <dl>
            <dt>Address</dt><dd>{SITE['address_line']}<br>{SITE['city']}</dd>
            {hours_rows}
          </dl>
        </div>
        <div class="info-card">
          <h3>Reach Us</h3>
          <dl>
            <dt>Email</dt><dd><a href="mailto:{SITE['email']}" class="link">{SITE['email']}</a></dd>
            <dt>Phone</dt><dd><a href="tel:{SITE['phone']}" class="link">{SITE['phone_display']}</a></dd>
            <dt>Instagram</dt><dd><a href="{SITE['instagram']}" class="link" target="_blank" rel="noopener">{SITE['instagram_handle']}</a></dd>
          </dl>
        </div>
        <div class="map-block">
          <iframe src="https://www.openstreetmap.org/export/embed.html?bbox=-122.6870%2C45.5175%2C-122.6790%2C45.5225&amp;layer=mapnik" title="Map showing Second Story Vintage location in Portland, Oregon" loading="lazy"></iframe>
        </div>
      </div>
    </div>
  </div>
</section>
"""
    html = render_page(
        path="/contact.html",
        active="contact",
        title=f"Contact — {SITE['name']}",
        description="Get in touch with Second Story Vintage — questions, reservations, sizing help, or press enquiries. We answer every message ourselves.",
        content=content,
        extra_scripts='<script src="/assets/js/forms.js"></script>',
    )
    write("/contact.html", html)


# --------------------------------------------------------------------------
# 404, sitemap, robots
# --------------------------------------------------------------------------

def build_404():
    content = f"""
<section class="section--lg">
  <div class="container" style="text-align:center">
    <p class="eyebrow" style="justify-content:center">404</p>
    <h1 style="font-size:var(--fs-display-l);margin-top:.6rem">This piece isn't on the rail.</h1>
    <p style="color:var(--text-muted);max-width:46ch;margin:1.25rem auto 0">The page you're looking for may have sold out, moved, or never existed. Let's get you back to shopping.</p>
    <div style="margin-top:2rem;display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">
      <a href="/" class="btn btn-primary">Back To Home</a>
      <a href="/shop.html" class="btn btn-secondary">Shop All Pieces</a>
    </div>
  </div>
</section>
"""
    html = render_page(
        path="/404.html",
        active="",
        title=f"Page Not Found — {SITE['name']}",
        description="This page could not be found.",
        content=content,
    )
    write("/404.html", html)


def build_sitemap():
    urls = ["/", "/shop.html", "/collections.html", "/lookbook.html", "/sustainability.html", "/about.html", "/faq.html", "/contact.html"]
    urls += [f"/product/{p['id']}.html" for p in PRODUCTS]
    urls += [f"/collection/{c['id']}.html" for c in COLLECTIONS]
    items = "".join(f"<url><loc>{SITE['url']}{u}</loc></url>" for u in urls)
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>\n'
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write(xml)


def build_robots():
    txt = f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n"
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write(txt)


# --------------------------------------------------------------------------
# Checkout
# --------------------------------------------------------------------------

def build_checkout():
    content = f"""
<div class="container" style="padding-top:calc(var(--sp-8) + 1rem);padding-bottom:1rem">
  <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/" class="link">Home</a> <span>/</span> <a href="/shop.html" class="link">Shop</a> <span>/</span> <span>Checkout</span></nav>
</div>
<section class="section--tight" style="padding-top:1rem">
  <div class="container">
    <div class="checkout-empty" data-checkout-empty style="display:none">
      {icon('bag')}
      <h1 style="font-size:var(--fs-display-s)">Your bag is empty.</h1>
      <p style="color:var(--text-muted);margin-top:.75rem">Find something one-of-one first — then come back here.</p>
      <div style="margin-top:1.75rem"><a href="/shop.html" class="btn btn-primary">Shop All Pieces</a></div>
    </div>

    <div class="order-success" data-order-success style="display:none">
      <div class="order-success__check">{icon('check')}</div>
      <h1 data-conf-name>Thank you.</h1>
      <p class="lede">Your order is confirmed. A receipt is on its way to <strong data-conf-email></strong>.</p>
      <div class="order-num" data-conf-number>SSV-000000-0000</div>
      <p class="lede" style="font-size:.9rem" data-conf-delivery></p>
      <div class="summary-card">
        <h2>Order Summary</h2>
        <div data-conf-items></div>
        <div class="summary-rows">
          <div class="summary-row"><span>Subtotal</span><span data-conf-subtotal>$0.00</span></div>
          <div class="summary-row"><span>Shipping</span><span data-conf-shipping>$0.00</span></div>
          <div class="summary-row"><span>Sales tax (Oregon)</span><span>$0.00</span></div>
          <div class="summary-row total"><span>Total</span><span data-conf-total>$0.00</span></div>
          <div class="summary-row"><span>Paid with</span><span data-conf-payment></span></div>
        </div>
      </div>
      <div style="margin-top:2rem;display:flex;gap:1rem;justify-content:center;flex-wrap:wrap">
        <a href="/shop.html" class="btn btn-primary">Keep Shopping</a>
        <a href="/" class="btn btn-secondary">Back To Home</a>
      </div>
    </div>

    <div class="checkout-layout" data-checkout-layout>
      <form data-checkout-form novalidate>
        <div class="co-section">
          <div class="co-head"><span class="co-num">1</span><h2>Contact</h2></div>
          <div class="field-row">
            <div class="field">
              <label for="co-first">First Name</label>
              <input id="co-first" name="first-name" type="text" required autocomplete="given-name">
              <p class="field-error">Please enter your first name.</p>
            </div>
            <div class="field">
              <label for="co-last">Last Name</label>
              <input id="co-last" name="last-name" type="text" required autocomplete="family-name">
              <p class="field-error">Please enter your last name.</p>
            </div>
          </div>
          <div class="field-row">
            <div class="field">
              <label for="co-email">Email</label>
              <input id="co-email" name="email" type="email" required autocomplete="email" placeholder="you@email.com">
              <p class="field-error">Please enter a valid email.</p>
            </div>
            <div class="field">
              <label for="co-phone">Phone <span style="text-transform:none;letter-spacing:0">(optional)</span></label>
              <input id="co-phone" name="phone" type="tel" autocomplete="tel">
            </div>
          </div>
        </div>

        <div class="co-section">
          <div class="co-head"><span class="co-num">2</span><h2>Delivery</h2></div>
          <label class="radio-card">
            <input type="radio" name="delivery" value="standard" checked>
            <span class="radio-card__label">
              <span class="radio-card__title">Standard Shipping</span>
              <span class="radio-card__sub">3–5 business days · Tracked · Free over $200</span>
            </span>
            <span class="radio-card__price" data-ship-price="standard">$8.00</span>
          </label>
          <label class="radio-card">
            <input type="radio" name="delivery" value="express">
            <span class="radio-card__label">
              <span class="radio-card__title">Express Shipping</span>
              <span class="radio-card__sub">1–2 business days · Tracked &amp; insured</span>
            </span>
            <span class="radio-card__price">$18.00</span>
          </label>
          <label class="radio-card">
            <input type="radio" name="delivery" value="pickup">
            <span class="radio-card__label">
              <span class="radio-card__title">Free Local Pickup</span>
              <span class="radio-card__sub">{SITE['address_line']}, Portland · Usually ready in 2 hours</span>
            </span>
            <span class="radio-card__price">Free</span>
          </label>
        </div>

        <div class="co-section" data-shipping-fields>
          <div class="co-head"><span class="co-num">3</span><h2>Shipping Address</h2></div>
          <div class="field">
            <label for="co-address">Street Address</label>
            <input id="co-address" name="address" type="text" required autocomplete="street-address">
            <p class="field-error">Please enter your address.</p>
          </div>
          <div class="field-row field-row--3">
            <div class="field">
              <label for="co-city">City</label>
              <input id="co-city" name="city" type="text" required autocomplete="address-level2">
              <p class="field-error">Please enter your city.</p>
            </div>
            <div class="field">
              <label for="co-state">State</label>
              <input id="co-state" name="state" type="text" required autocomplete="address-level1" placeholder="OR">
              <p class="field-error">Required.</p>
            </div>
            <div class="field">
              <label for="co-zip">ZIP</label>
              <input id="co-zip" name="zip" type="text" required autocomplete="postal-code" inputmode="numeric">
              <p class="field-error">Invalid ZIP.</p>
            </div>
          </div>
        </div>

        <div class="co-section">
          <div class="co-head"><span class="co-num" data-pay-step>4</span><h2>Payment</h2></div>
          <div class="field">
            <label for="co-card">Card Number</label>
            <div class="card-input-wrap">
              <input id="co-card" name="card-number" type="text" required autocomplete="cc-number" inputmode="numeric" placeholder="1234 5678 9012 3456">
              <span class="card-brand" data-card-brand></span>
            </div>
            <p class="field-error">Please enter a valid card number.</p>
          </div>
          <div class="field">
            <label for="co-card-name">Name On Card</label>
            <input id="co-card-name" name="card-name" type="text" required autocomplete="cc-name">
            <p class="field-error">Please enter the name on the card.</p>
          </div>
          <div class="field-row">
            <div class="field">
              <label for="co-expiry">Expiry</label>
              <input id="co-expiry" name="card-expiry" type="text" required autocomplete="cc-exp" inputmode="numeric" placeholder="MM/YY">
              <p class="field-error">Enter a valid future date.</p>
            </div>
            <div class="field">
              <label for="co-cvv">Security Code</label>
              <input id="co-cvv" name="card-cvv" type="text" required autocomplete="cc-csc" inputmode="numeric" placeholder="CVC">
              <p class="field-error">3–4 digits.</p>
            </div>
          </div>
          <button class="btn btn-primary btn-block" type="submit" data-pay-btn style="margin-top:.5rem"><span>Pay</span></button>
          <div class="secure-note">{icon('shield')}<span>Demo checkout — no real payment is processed and card details are never stored.</span></div>
        </div>
      </form>

      <aside class="summary-card" aria-label="Order summary">
        <h2>Order Summary</h2>
        <div data-summary-items></div>
        <div class="summary-rows">
          <div class="summary-row"><span>Subtotal</span><span data-sum-subtotal>$0.00</span></div>
          <div class="summary-row"><span>Shipping</span><span data-sum-shipping>$8.00</span></div>
          <div class="summary-row"><span>Sales tax (Oregon)</span><span>$0.00</span></div>
          <div class="summary-row total"><span>Total</span><span data-sum-total>$0.00</span></div>
        </div>
        <div class="secure-note" style="justify-content:flex-start">{icon('recycle')}<span>Every purchase keeps one more garment out of a landfill.</span></div>
      </aside>
    </div>
  </div>
</section>
"""
    html = render_page(
        path="/checkout.html",
        active="shop",
        title=f"Checkout — {SITE['name']}",
        description="Secure checkout for your one-of-one vintage pieces.",
        content=content,
        noindex=True,
        extra_scripts='<script src="/assets/js/checkout.js"></script>',
    )
    write("/checkout.html", html)


if __name__ == "__main__":
    build_home()
    build_shop()
    for _p in PRODUCTS:
        build_product_page(_p)
    build_collections_index()
    for _c in COLLECTIONS:
        build_collection_page(_c)
    build_lookbook()
    build_sustainability()
    build_about()
    build_faq()
    build_contact()
    build_checkout()
    build_404()
    build_sitemap()
    build_robots()
    print(f"Built: Home, Shop, {len(PRODUCTS)} products, Collections index + {len(COLLECTIONS)} collections, "
          f"Lookbook, Sustainability, About, FAQ, Contact, Checkout, 404, sitemap.xml, robots.txt.")
