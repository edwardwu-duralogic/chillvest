"""Generate segment-versioned ChillVest intro pages for outreach emails.

Reads product ingredients (specs, certs, expo proof, demo video, images) and
writes one HTML one-pager per outreach client segment into /docs so the pages
publish via GitHub Pages and can be linked from cold emails.

Design follows docs/chillvest.html (How It Works steps, spec table, labeled
certification table, selling-point card grid).

Segments (from "ChillVest - Outreach Strategy & Contact Segments" doc):
  A + E -> hse          (end corporate users: oil & gas, energy, utilities)
  B     -> procurement  (buyers, category managers, sourcing leads)
  C     -> partner      (VP-level strategic partners)
  D     -> distributor  (safety distribution channel)
  F     -> oem          (OEM, private label, apparel partners)
"""

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
IMG_DIR = DOCS / "img"

VIDEO_URL = "https://drive.google.com/file/d/1yKCWeUDbsyA_6mFEs7U-3kfguiNkogm5/view"
FORM_URL = "https://docs.google.com/forms/d/1xP78a-Gph2JwS-bNTbZkW42qcwMo9A8t8uYNvN8mjto/viewform"

IMAGES = [
    # (source file, published name, caption)
    (ROOT / "data" / "Product1.JPG", "vest_front_back.jpg",
     "ChillVest worn — front and back. Total weight 1.3 kg / 2.85 lb."),
    (ROOT / "data" / "output" / "chillvest_imgs" / "p1_img2_959x724.jpeg", "vest_weight.jpg",
     "Low-profile harness with belt-mounted ColdBank — 1.4 kg / 3 lb configuration."),
]

HOW_IT_WORKS = [
    ("Pre-Cool", "Place ColdBank cells in a standard freezer or ice cooler for "
                 "1&ndash;2 hours before the shift."),
    ("Wear", "Put on the vest. Gel cells sit against the body, separated by a thin "
             "comfort fabric layer."),
    ("Sustained Cooling", "Body heat conducts into the cold gel, which absorbs it evenly "
                          "&mdash; no cold spike, steady release over hours."),
    ("Swap, Don't Stop", "When a ColdBank warms up, swap in a fresh one in seconds "
                         "&mdash; all-day cooling with no mid-shift freezer trips."),
    ("Airflow Assist", "USB-powered DC 5V motor enhances air circulation in "
                       "low-wind conditions."),
]

SPECS = [
    ("Model", "ChillVest-C01"),
    ("Manufacturer", "Duralogic (Holding) Limited &mdash; Global Representative in Phoenix, AZ"),
    ("Weight (worn)", "1.3&ndash;1.4 kg / 2.85&ndash;3.0 lb"),
    ("Coolant", "CB2026 (sodium polyacrylate + propylene glycol, 50/50)"),
    ("Physical State", "Colorless, odorless gel &mdash; density 1.11 g/mL"),
    ("Boiling Point", "170&ndash;180&deg;C"),
    ("Flammability", "Flash point &gt;100&deg;C (non-flammable)"),
    ("Motor Power", "DC 5V, USB-rechargeable, low noise"),
    ("Runtime", "All-day via ColdBank swap &mdash; no 2&ndash;3 hr re-freeze cycle"),
    ("Target Environment", "&ge;35&deg;C / 95&deg;F"),
]

CERTIFICATIONS = [
    # (certificate, standard, cert number, issued, significance)
    ("RoHS Certificate", "EU Directive 2011/65/EU", "HTT2026041001R", "May 19, 2026",
     "All 55 material components pass limits for the 10 restricted hazardous substances."),
    ("EMC / CE Certificate", "EU Directive 2014/30/EU", "HTT2026041001E", "Apr 22, 2026",
     "Electronic unit passes emission and immunity testing; authorizes CE marking."),
    ("MSDS &mdash; CB2026 Coolant", "GHS / REACH", "&mdash;", "Apr 24, 2026",
     "Safety data sheet accepted by US Customs, carriers, and OSHA HazCom programs."),
]

SELLING_POINTS = [
    ("&#128167;", "Non-Disruptive",
     "No hoses, no dripping ice, no soaked clothing. Workers stay dry and mobile "
     "throughout the shift."),
    ("&#9851;", "Reusable &amp; Rechargeable",
     "Low ongoing cost versus single-use cooling products. Recharges in any standard "
     "freezer or cooler."),
    ("&#128263;", "Quiet Operation",
     "Low-noise motor suitable for customer-facing roles, offices, and noise-sensitive "
     "environments."),
    ("&#129514;", "Safe Materials",
     "Food-adjacent ingredients. Non-flammable, non-carcinogenic, California Prop 65 "
     "safe. Full MSDS available."),
    ("&#128203;", "Certified",
     "EU RoHS and CE certifications demonstrate rigorous material safety and "
     "electronics manufacturing standards."),
    ("&#127959;", "Versatile Use Cases",
     "Construction, oil &amp; gas, agriculture, warehousing, events, military, and "
     "emergency response."),
]

EXPOS = [
    ("Osaka Expo 2025", "Exhibited"),
    ("NSC Safety Congress &amp; Expo 2026 &mdash; Sept 14&ndash;16, Indianapolis, IN "
     "&middot; Booth #409", "Exhibiting"),
    ("TOOL JAPAN 2026 &mdash; Oct 7&ndash;9, Makuhari Messe, Chiba, Japan", "Exhibiting"),
]

SEGMENTS = {
    "hse": {
        "edition": "For HSE &amp; Safety Leaders",
        "tagline": "Keep field crews safe and productive through peak heat &mdash; "
                   "all-day core cooling without ice, hoses, or freezer cycles.",
        "intro_title": "Heat Stress Is a Safety Metric You Can Move",
        "intro": "Heat incidents drive recordables, lost hours, and early shift stops. "
                 "ChillVest keeps a worker's core temperature in the safe range even at "
                 "100&deg;F+ by holding cold gel cells against the body and swapping in a "
                 "fresh ColdBank when needed &mdash; no freezer trips mid-shift, no soaked "
                 "clothing, no downtime. Field teams stay on task through the hottest part "
                 "of the day.",
        "value_title": "Why HSE Teams Pick ChillVest",
        "values": [
            "All-day cooling: swappable ColdBank vs. phase-change vests that quit after "
            "2&ndash;3 hours and need a freezer",
            "3 lb worn weight &mdash; doesn't interfere with harnesses, FR clothing, or tools",
            "No dripping ice or hoses; workers stay dry and presentable",
            "Quiet USB-rechargeable airflow unit for enclosed or customer-facing work",
            "Free evaluation sample program for HSE pilot teams",
        ],
        "cta_label": "Request an Evaluation Sample",
    },
    "procurement": {
        "edition": "Supplier Introduction &mdash; Procurement &amp; Sourcing",
        "tagline": "A cooling-PPE supplier ready for your qualification process: "
                   "certified, documented, with US representation.",
        "intro_title": "Ready for Supplier Qualification",
        "intro": "Duralogic (Holding) Ltd manufactures ChillVest in Asia and supports US "
                 "customers through its Global Representative in Phoenix, AZ. Compliance documentation "
                 "&mdash; CE (EMC), RoHS, and MSDS for customs and OSHA HazCom &mdash; is "
                 "ready to submit with your supplier paperwork, and evaluation samples ship "
                 "on request so your stakeholders can test before a PO.",
        "value_title": "What You Get as a Buyer",
        "values": [
            "Compliance pack ready: CE / EMC certificate, RoHS certificate, MSDS (GHS / REACH)",
            "Global Representative in Phoenix, AZ for domestic coordination and fulfillment",
            "Fast sample-to-order pipeline &mdash; evaluation units ship before commitments",
            "Competitive factory-direct pricing with wholesale tiers",
            "Spec sheet and pricing sheet available on request",
        ],
        "cta_label": "Request Sample &amp; Documentation",
    },
    "partner": {
        "edition": "Strategic Partnership Briefing",
        "tagline": "Co-develop the next generation of worker cooling &mdash; including a "
                   "no-freezer chemical cooling system for remote operations.",
        "intro_title": "A Lighthouse Partnership, Not a Product Sale",
        "intro": "For organizations operating in extreme heat at scale, we offer a "
                 "partnership track: site pilots, preferential bulk pricing, co-branding "
                 "with your safety program, and a direct line into product development. "
                 "Our newest extension activates cooling chemically &mdash; reaching "
                 "~0&deg;C in seconds with just tap water, no freezer infrastructure "
                 "anywhere in the field &mdash; built for the most remote worksites.",
        "value_title": "Partnership Tracks",
        "values": [
            "Site pilot programs with on-site demonstration by our team",
            "Early co-development access to the no-freezer chemical cooling kit",
            "Preferential pricing on bulk and multi-site orders",
            "Co-branding options aligned to your internal safety program",
            "Direct input into sizing, configuration, and deployment workflow",
        ],
        "cta_label": "Explore a Pilot Program",
    },
    "distributor": {
        "edition": "For Safety Distributors &amp; Channel Partners",
        "tagline": "A differentiated cooling-PPE line for a category your customers are "
                   "actively sourcing right now.",
        "intro_title": "The Cooling PPE Category Is Moving",
        "intro": "OSHA heat-stress enforcement is pushing corporate safety teams to source "
                 "cooling PPE &mdash; and most of what's on the market is phase-change "
                 "vests that quit after 2&ndash;3 hours and need a freezer. ChillVest's "
                 "swappable ColdBank system delivers all-day cooling, giving your line a "
                 "premium tier above existing PCM products rather than another me-too SKU.",
        "value_title": "Why Carry ChillVest",
        "values": [
            "Clear differentiation: all-day swappable cooling vs. 2&ndash;3 hour PCM re-freeze cycles",
            "Certified and documented: CE (EMC), RoHS, MSDS &mdash; clean supplier onboarding",
            "Factory-direct wholesale pricing with our Global Representative in Phoenix, AZ",
            "Meet us at NSC Safety Congress &amp; Expo 2026 in Indianapolis (Sept 14&ndash;16, Booth #409)",
            "Complementary to FR workwear lines &mdash; bundling opportunity, not channel conflict",
        ],
        "cta_label": "Request Sample &amp; Wholesale Pricing",
    },
    "oem": {
        "edition": "OEM &amp; Private Label Partnership",
        "tagline": "A proven, certified cooling system ready for private-label "
                   "manufacturing, co-branding, or US customization.",
        "intro_title": "Build With a Proven Cooling Platform",
        "intro": "ChillVest pairs a field-tested vest design with the swappable ColdBank "
                 "cooling system &mdash; certified (CE, RoHS, MSDS) and in production "
                 "today. For apparel manufacturers and brands, that opens private-label "
                 "production, co-branded distribution into your existing channels, or "
                 "US-based customization and fulfillment partnerships.",
        "value_title": "Partnership Models",
        "values": [
            "Private label: your brand on a certified, production-ready cooling vest",
            "Co-distribution: add a cooling category to your existing apparel channels",
            "US customization and fulfillment partnership opportunities",
            "Certified platform &mdash; CE (EMC), RoHS, MSDS documentation transfers cleanly",
            "Flexible MOQs while the US line ramps",
        ],
        "cta_label": "Start a Partnership Conversation",
    },
}

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChillVest &mdash; {edition_plain} | Duralogic</title>
<style>
  *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
  :root {{
    --navy: #0a2342; --blue: #1a4a7a; --mid: #2563a8; --light-blue: #7ab3e0;
    --teal: #4fc3a1; --amber: #f59e0b; --bg: #f0f4f8; --text: #1a1a2e; --muted: #64748b;
  }}
  body {{ font-family: 'Segoe UI', system-ui, -apple-system, Arial, sans-serif;
         background: var(--bg); color: var(--text); line-height: 1.6; }}
  .header {{ background: linear-gradient(135deg, var(--navy) 0%, var(--blue) 100%);
             color: white; padding: 40px 24px 30px; }}
  .header-inner {{ max-width: 920px; margin: 0 auto; display: flex;
                   align-items: flex-start; justify-content: space-between;
                   gap: 24px; flex-wrap: wrap; }}
  .brand-label {{ font-size: 11px; letter-spacing: 3px; text-transform: uppercase;
                  color: var(--light-blue); margin-bottom: 10px; }}
  .header h1 {{ font-size: 40px; font-weight: 800; letter-spacing: -1px; line-height: 1.1; }}
  .header h1 span {{ color: var(--teal); }}
  .edition {{ display: inline-block; margin-top: 10px; background: rgba(79,195,161,0.15);
              border: 1px solid var(--teal); border-radius: 6px; padding: 4px 14px;
              font-size: 12px; letter-spacing: 1.5px; text-transform: uppercase; color: var(--teal); }}
  .tagline {{ margin-top: 14px; font-size: 15px; color: #b8d4ef; max-width: 560px; }}
  .header-badge-group {{ display: flex; flex-direction: column; gap: 8px;
                         flex-shrink: 0; padding-top: 4px; }}
  .header-badge {{ background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15);
                   border-radius: 6px; padding: 6px 14px; font-size: 11px;
                   color: var(--light-blue); letter-spacing: 1.5px; text-transform: uppercase;
                   display: flex; align-items: center; gap: 6px; }}
  .header-badge .check {{ color: var(--teal); font-size: 13px; }}
  .cert-strip {{ background: var(--navy); padding: 10px 24px; }}
  .cert-strip-inner {{ max-width: 920px; margin: 0 auto; display: flex; gap: 24px; flex-wrap: wrap; }}
  .cert-item {{ font-size: 11px; color: var(--light-blue); letter-spacing: 1px;
                text-transform: uppercase; display: flex; align-items: center; gap: 6px; }}
  .cert-item .dot {{ width: 7px; height: 7px; border-radius: 50%; background: var(--teal); }}
  .page {{ max-width: 920px; margin: 0 auto; padding: 36px 24px 64px; }}
  .section-title {{ font-size: 11px; font-weight: 700; letter-spacing: 3px;
                    text-transform: uppercase; color: var(--mid); margin: 36px 0 16px;
                    padding-bottom: 8px; border-bottom: 2px solid #dde7f2; }}
  .card {{ background: white; border-radius: 12px; padding: 28px;
           box-shadow: 0 2px 12px rgba(10,35,66,0.07); border: 1px solid #e2eaf4; }}
  .card h3 {{ font-size: 16px; font-weight: 700; color: var(--navy); margin-bottom: 14px; }}
  .intro-card h2 {{ font-size: 22px; color: var(--navy); margin-bottom: 10px; }}
  .intro-card p {{ font-size: 15px; color: #334155; line-height: 1.75; }}
  .video-card {{ display: flex; align-items: center; gap: 20px; background:
                 linear-gradient(135deg, var(--navy) 0%, var(--mid) 100%); border-radius: 12px;
                 padding: 24px 28px; margin-top: 24px; text-decoration: none;
                 transition: transform 0.15s ease; }}
  .video-card:hover {{ transform: translateY(-2px); }}
  .play-btn {{ width: 58px; height: 58px; border-radius: 50%; background: var(--teal);
               display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
  .play-btn::after {{ content: ''; border-left: 18px solid var(--navy);
                      border-top: 11px solid transparent; border-bottom: 11px solid transparent;
                      margin-left: 5px; }}
  .video-card h3 {{ color: white; font-size: 16px; margin-bottom: 4px; }}
  .video-card p {{ color: #b8d4ef; font-size: 13px; }}
  .img-row {{ display: flex; gap: 16px; flex-wrap: wrap; margin-top: 6px; }}
  .img-card {{ flex: 1; min-width: 260px; background: white; border-radius: 12px;
               overflow: hidden; box-shadow: 0 2px 12px rgba(10,35,66,0.07);
               border: 1px solid #e2eaf4; }}
  .img-card img {{ width: 100%; display: block; }}
  .img-card p {{ font-size: 12px; color: var(--muted); padding: 10px 14px; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
  @media (max-width: 680px) {{ .two-col {{ grid-template-columns: 1fr; }} }}
  .steps {{ display: flex; flex-direction: column; }}
  .step {{ display: flex; gap: 18px; align-items: flex-start; padding: 14px 0;
           border-bottom: 1px solid #f0f4f8; }}
  .step:last-child {{ border-bottom: none; }}
  .step-num {{ width: 30px; height: 30px; border-radius: 50%;
               background: linear-gradient(135deg, var(--mid), var(--blue)); color: white;
               font-weight: 700; font-size: 13px; display: flex; align-items: center;
               justify-content: center; flex-shrink: 0; margin-top: 2px; }}
  .step-content h4 {{ font-size: 13.5px; font-weight: 700; color: var(--navy); margin-bottom: 3px; }}
  .step-content p {{ font-size: 13px; color: var(--muted); line-height: 1.55; }}
  .specs-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  .specs-table td {{ padding: 9px 10px; border-bottom: 1px solid #f0f4f8; vertical-align: top; }}
  .specs-table td:first-child {{ color: var(--muted); font-weight: 600; width: 44%; }}
  .specs-table td:last-child {{ color: var(--navy); font-weight: 500; }}
  .specs-table tr:last-child td {{ border-bottom: none; }}
  .cert-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  .cert-table th {{ background: #f0f4f8; color: var(--muted); font-size: 11px;
                    letter-spacing: 1px; text-transform: uppercase; padding: 8px 12px;
                    text-align: left; font-weight: 600; }}
  .cert-table td {{ padding: 10px 12px; border-bottom: 1px solid #f0f4f8;
                    vertical-align: top; color: var(--text); }}
  .cert-table tr:last-child td {{ border-bottom: none; }}
  .cert-table td:first-child {{ font-weight: 600; color: var(--navy); }}
  .cert-table .held {{ display: inline-block; background: rgba(79,195,161,0.14);
                       color: #1d8a6b; font-size: 10px; font-weight: 700;
                       letter-spacing: 1px; text-transform: uppercase;
                       border-radius: 4px; padding: 2px 8px; margin-left: 6px; }}
  .points-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
  @media (max-width: 680px) {{ .points-grid {{ grid-template-columns: 1fr; }} }}
  .point-card {{ background: white; border-radius: 10px; padding: 20px;
                 border: 1px solid #e2eaf4; box-shadow: 0 1px 6px rgba(10,35,66,0.05); }}
  .point-icon {{ font-size: 22px; margin-bottom: 8px; }}
  .point-card h4 {{ font-size: 13px; font-weight: 700; color: var(--navy); margin-bottom: 5px; }}
  .point-card p {{ font-size: 12.5px; color: var(--muted); line-height: 1.55; }}
  ul.values {{ background: white; border-radius: 12px; padding: 20px 28px 20px 46px;
               box-shadow: 0 2px 12px rgba(10,35,66,0.07); border: 1px solid #e2eaf4; }}
  ul.values li {{ font-size: 14px; padding: 6px 0; }}
  ul.values li::marker {{ color: var(--teal); }}
  .expo-strip {{ display: flex; gap: 14px; flex-wrap: wrap; }}
  .expo-card {{ flex: 1; min-width: 220px; background: white; border-left: 4px solid var(--teal);
                border-radius: 8px; padding: 14px 18px; box-shadow: 0 1px 6px rgba(10,35,66,0.05);
                border-top: 1px solid #e2eaf4; border-right: 1px solid #e2eaf4;
                border-bottom: 1px solid #e2eaf4; }}
  .expo-card .status {{ font-size: 10px; letter-spacing: 1.5px; text-transform: uppercase;
                        color: var(--teal); font-weight: 700; }}
  .expo-card .name {{ font-size: 13px; color: var(--text); margin-top: 3px; }}
  .cta {{ background: linear-gradient(135deg, var(--navy) 0%, var(--blue) 100%);
          border-radius: 12px; padding: 32px 28px; margin-top: 40px; text-align: center; }}
  .cta h2 {{ color: white; font-size: 22px; margin-bottom: 8px; }}
  .cta p {{ color: #b8d4ef; font-size: 14px; margin-bottom: 18px; }}
  .cta a.button {{ display: inline-block; background: var(--teal); color: var(--navy);
                   font-weight: 700; font-size: 15px; padding: 13px 34px; border-radius: 8px;
                   text-decoration: none; }}
  .contact {{ margin-top: 22px; font-size: 13px; color: #b8d4ef; line-height: 1.7; }}
  .contact a {{ color: var(--teal); text-decoration: none; }}
  .footer {{ text-align: center; font-size: 11px; color: var(--muted); padding: 18px; }}
</style>
</head>
<body>

<div class="header"><div class="header-inner">
  <div>
    <div class="brand-label">Duralogic (Holding) Ltd</div>
    <h1>Chill<span>Vest</span></h1>
    <div class="edition">{edition}</div>
    <p class="tagline">{tagline}</p>
  </div>
  <div class="header-badge-group">
    <div class="header-badge"><span class="check">&#10003;</span> RoHS Certified</div>
    <div class="header-badge"><span class="check">&#10003;</span> CE / EMC Certified</div>
    <div class="header-badge"><span class="check">&#10003;</span> GHS / REACH MSDS</div>
  </div>
</div></div>

<div class="cert-strip"><div class="cert-strip-inner">
  <div class="cert-item"><span class="dot"></span>Model: ChillVest-C01</div>
  <div class="cert-item"><span class="dot"></span>Coolant: CB2026</div>
  <div class="cert-item"><span class="dot"></span>Power: DC 5V USB</div>
  <div class="cert-item"><span class="dot"></span>Global Representative: Phoenix, AZ</div>
</div></div>

<div class="page">

  <div class="card intro-card">
    <h2>{intro_title}</h2>
    <p>{intro}</p>
  </div>

  <a class="video-card" href="{video_url}" target="_blank" rel="noopener">
    <div class="play-btn"></div>
    <div>
      <h3>Watch ChillVest in Action &mdash; Short Product Demo</h3>
      <p>Vest operation, ColdBank setup, and real-world wear. Click to play.</p>
    </div>
  </a>

  <div class="section-title">Product</div>
  <div class="img-row">
{image_cards}
  </div>

  <div class="section-title">How It Works &amp; Key Specifications</div>
  <div class="two-col">
    <div class="card">
      <h3>How It Works</h3>
      <div class="steps">
{steps}
      </div>
    </div>
    <div class="card">
      <h3>Key Specifications</h3>
      <table class="specs-table"><tbody>
{spec_rows}
      </tbody></table>
    </div>
  </div>

  <div class="section-title">Certifications</div>
  <div class="card">
    <table class="cert-table">
      <thead><tr>
        <th>Certificate</th><th>Standard</th><th>Certificate No.</th>
        <th>Issued</th><th>What It Means</th>
      </tr></thead>
      <tbody>
{cert_rows}
      </tbody>
    </table>
  </div>

  <div class="section-title">Key Selling Points</div>
  <div class="points-grid">
{point_cards}
  </div>

  <div class="section-title">{value_title}</div>
  <ul class="values">
{value_items}
  </ul>

  <div class="section-title">Where You Can Find Us</div>
  <div class="expo-strip">
{expo_cards}
  </div>

  <div class="cta">
    <h2>{cta_label}</h2>
    <p>Tell us about your team and use case &mdash; samples and documentation ship promptly.</p>
    <a class="button" href="{form_url}" target="_blank" rel="noopener">Request a Sample</a>
    <div class="contact">
      Edward Wu &middot; Global Representative | Duralogic (Holding) Ltd<br>
      Phoenix, AZ &middot; USA &middot; Mobile: +1 (469) 515-2507<br>
      <a href="mailto:edward.duralogic@gmail.com">edward.duralogic@gmail.com</a> &middot;
      <a href="https://www.duranheat.com">www.duranheat.com</a>
    </div>
  </div>

</div>

<div class="footer">&copy; 2026 Duralogic (Holding) Ltd &mdash; ChillVest&trade; Personal Cooling System</div>

</body>
</html>
"""


def copy_images():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    for src, name, _caption in IMAGES:
        shutil.copyfile(src, IMG_DIR / name)


def build_image_cards():
    return "\n".join(
        f'    <div class="img-card"><img src="img/{name}" '
        f'alt="{caption}"><p>{caption}</p></div>'
        for _src, name, caption in IMAGES
    )


def build_steps():
    rows = []
    for i, (title, desc) in enumerate(HOW_IT_WORKS, start=1):
        rows.append(
            f'        <div class="step"><div class="step-num">{i}</div>'
            f'<div class="step-content"><h4>{title}</h4><p>{desc}</p></div></div>'
        )
    return "\n".join(rows)


def build_spec_rows():
    return "\n".join(
        f"        <tr><td>{label}</td><td>{value}</td></tr>" for label, value in SPECS
    )


def build_cert_rows():
    return "\n".join(
        f'        <tr><td>{cert}<span class="held">Held</span></td><td>{std}</td>'
        f"<td>{num}</td><td>{issued}</td><td>{meaning}</td></tr>"
        for cert, std, num, issued, meaning in CERTIFICATIONS
    )


def build_point_cards():
    return "\n".join(
        f'    <div class="point-card"><div class="point-icon">{icon}</div>'
        f"<h4>{title}</h4><p>{desc}</p></div>"
        for icon, title, desc in SELLING_POINTS
    )


def build_expo_cards():
    return "\n".join(
        f'    <div class="expo-card"><div class="status">{status}</div>'
        f'<div class="name">{name}</div></div>'
        for name, status in EXPOS
    )


def render_page(content):
    edition_plain = content["edition"].replace("&amp;", "&").replace("&mdash;", "-")
    return PAGE_TEMPLATE.format(
        edition=content["edition"],
        edition_plain=edition_plain,
        tagline=content["tagline"],
        intro_title=content["intro_title"],
        intro=content["intro"],
        value_title=content["value_title"],
        value_items="\n".join(f"    <li>{v}</li>" for v in content["values"]),
        cta_label=content["cta_label"],
        image_cards=build_image_cards(),
        steps=build_steps(),
        spec_rows=build_spec_rows(),
        cert_rows=build_cert_rows(),
        point_cards=build_point_cards(),
        expo_cards=build_expo_cards(),
        video_url=VIDEO_URL,
        form_url=FORM_URL,
    )


def main():
    # Optional CLI args limit generation to named segments, e.g.
    #   python gen_segment_pages.py hse
    # No args regenerates all five pages.
    keys = sys.argv[1:] or list(SEGMENTS)
    unknown = [k for k in keys if k not in SEGMENTS]
    if unknown:
        raise SystemExit(f"unknown segment(s): {unknown} — valid: {list(SEGMENTS)}")
    copy_images()
    for key in keys:
        out_path = DOCS / f"chillvest_{key}.html"
        out_path.write_text(render_page(SEGMENTS[key]), encoding="utf-8")
        print(f"wrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
