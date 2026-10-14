import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import altair as alt
import base64
import json
import random

# --------------------------------------------------
# Configuration
# --------------------------------------------------

DATA_FILE = "data/final_risk_segments.csv"
SUMMARY_FILE = "data/risk_tier_summary.csv"

st.set_page_config(
    page_title="Credit Risk Segmentation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# Sidebar: animation toggle
# --------------------------------------------------

st.sidebar.markdown("### Display")
animated_bg = st.sidebar.toggle("Animated background", value=True)
flow_lines = st.sidebar.toggle("Flowing lines", value=True)

# --------------------------------------------------
# Custom CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    /* ==================================================
       GLOBAL BACKGROUND (GREY)
       ================================================== */

    .stApp {
        background:
            radial-gradient(circle at 10% 20%, rgba(59, 130, 246, 0.07), transparent 30%),
            radial-gradient(circle at 90% 35%, rgba(14, 165, 233, 0.05), transparent 30%),
            radial-gradient(circle at 50% 95%, rgba(34, 197, 94, 0.04), transparent 30%),
            linear-gradient(135deg, #1e2227 0%, #292e35 50%, #343a42 100%);
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    /* ==================================================
       ANIMATED DATA-FLOW BACKGROUND (CSS layer)
       ================================================== */

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;

        background-image:
            linear-gradient(90deg, transparent 0%, rgba(59,130,246,0.00) 8%, rgba(96,165,250,0.60) 12%, rgba(59,130,246,0.00) 16%, transparent 24%),
            linear-gradient(90deg, transparent 0%, rgba(14,165,233,0.00) 32%, rgba(56,189,248,0.55) 37%, rgba(14,165,233,0.00) 42%, transparent 50%),
            linear-gradient(90deg, transparent 0%, rgba(34,197,94,0.00) 58%, rgba(74,222,128,0.50) 63%, rgba(34,197,94,0.00) 68%, transparent 76%);

        background-size: 900px 2px, 1100px 2px, 1300px 2px;
        background-repeat: repeat-x;
        background-position: 0 22%, 0 51%, 0 78%;

        animation: dataFlow 8s linear infinite;
    }

    .stApp::after {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;

        background-image:
            linear-gradient(90deg, transparent 0 48%, rgba(148,163,184,0.07) 48.2%, transparent 48.5% 100%),
            linear-gradient(0deg, transparent 0 62%, rgba(148,163,184,0.06) 62.2%, transparent 62.5% 100%);

        background-size: 160px 160px;
        opacity: 0.8;

        animation: circuitMove 14s linear infinite;
    }

    @keyframes dataFlow {
        0% {
            background-position: -900px 22%, -1100px 51%, -1300px 78%;
        }
        100% {
            background-position: 900px 22%, 1100px 51%, 1300px 78%;
        }
    }

    @keyframes circuitMove {
        0% {
            background-position: 0 0, 0 0;
        }
        100% {
            background-position: 160px 0, 0 160px;
        }
    }

    [data-testid="stAppViewContainer"] {
        position: relative;
        z-index: 1;
    }

    .main .block-container {
        position: relative;
        z-index: 2;
    }

    /* ==================================================
       TITLE
       ================================================== */

    .main-title {
        font-size: 44px;
        font-weight: 850;
        color: #f8fafc;
        margin-bottom: 4px;
        letter-spacing: -1.2px;
    }

    .subtitle {
        font-size: 16px;
        color: #94a3b8;
        margin-bottom: 28px;
    }

    /* ==================================================
       ARCHITECTURE PIPELINE
       Each box glows white in turn:
       Kafka -> HDFS -> K-Means -> Risk Tiers -> (repeat)
       Cycle = 8s, each step starts 2s after the previous one
       ================================================== */

    .architecture-card {
        background: linear-gradient(145deg, #0f141c, #090c12);
        border-radius: 18px;
        padding: 20px 14px;
        text-align: center;
        min-height: 108px;

        border: 1px solid #1f2937;
        border-top: 4px solid #3b82f6;

        box-shadow: 0 7px 22px rgba(0, 0, 0, 0.55);

        transition: transform 0.25s ease;
        animation: pipelineGlow 8s ease-in-out infinite;
    }

    .architecture-card.step-0 { animation-delay: 0s; }
    .architecture-card.step-1 { animation-delay: 2s; }
    .architecture-card.step-2 { animation-delay: 4s; }
    .architecture-card.step-3 { animation-delay: 6s; }

    .architecture-card:hover {
        transform: translateY(-6px);
    }

    @keyframes pipelineGlow {
        0% {
            box-shadow: 0 7px 22px rgba(0, 0, 0, 0.55);
            border-color: #1f2937;
            border-top-color: #3b82f6;
        }
        6%, 20% {
            box-shadow:
                0 0 0 1px rgba(255, 255, 255, 0.85),
                0 0 22px 4px rgba(255, 255, 255, 0.55),
                0 0 60px 14px rgba(255, 255, 255, 0.20);
            border-color: #ffffff;
            border-top-color: #ffffff;
        }
        30%, 100% {
            box-shadow: 0 7px 22px rgba(0, 0, 0, 0.55);
            border-color: #1f2937;
            border-top-color: #3b82f6;
        }
    }

    .architecture-icon {
        font-size: 27px;
        margin-bottom: 7px;
    }

    .architecture-title {
        font-size: 16px;
        font-weight: 750;
        color: #f8fafc;
    }

    .architecture-subtitle {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 4px;
    }

    .architecture-arrow {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 108px;
        font-size: 30px;
        font-weight: 800;
        color: #475569;
        animation: arrowFlow 8s ease-in-out infinite;
    }

    .architecture-arrow.arrow-0 { animation-delay: 1.4s; }
    .architecture-arrow.arrow-1 { animation-delay: 3.4s; }
    .architecture-arrow.arrow-2 { animation-delay: 5.4s; }

    @keyframes arrowFlow {
        0% {
            color: #475569;
            text-shadow: none;
            transform: translateX(0);
        }
        5%, 12% {
            color: #ffffff;
            text-shadow: 0 0 14px #ffffff, 0 0 30px rgba(255, 255, 255, 0.7);
            transform: translateX(6px);
        }
        20%, 100% {
            color: #475569;
            text-shadow: none;
            transform: translateX(0);
        }
    }

    /* ==================================================
       GENERAL SECTION HEADERS
       ================================================== */

    .section-header {
        font-size: 27px;
        font-weight: 800;
        color: #f8fafc;
        margin-top: 12px;
        margin-bottom: 6px;
    }

    .section-description {
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 20px;
    }

    /* ==================================================
       PORTFOLIO METRIC CARDS
       ================================================== */

    .metric-card {
        background: rgba(13, 17, 24, 0.92);
        border-radius: 17px;
        padding: 22px;
        min-height: 132px;
        border: 1px solid #1e293b;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }

    .metric-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 14px 30px rgba(59, 130, 246, 0.18);
    }

    .metric-label {
        font-size: 14px;
        font-weight: 650;
        color: #94a3b8;
        margin-bottom: 10px;
    }

    .metric-value {
        font-size: 32px;
        font-weight: 850;
        color: #f8fafc;
    }

    .metric-description {
        font-size: 12px;
        color: #64748b;
        margin-top: 6px;
    }

    /* ==================================================
       MODEL EVALUATION
       ================================================== */

    .evaluation-card {
        background: linear-gradient(145deg, #0f141c, #0a0e15);
        border-radius: 17px;
        padding: 22px;
        text-align: center;
        border: 1px solid #1e293b;
        border-top: 4px solid #6366f1;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
        min-height: 128px;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }

    .evaluation-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 15px 30px rgba(99, 102, 241, 0.22);
    }

    .evaluation-label {
        font-size: 13px;
        font-weight: 650;
        color: #818cf8;
    }

    .evaluation-value {
        font-size: 31px;
        font-weight: 850;
        color: #f8fafc;
        margin-top: 9px;
    }

    /* ==================================================
       RISK INSIGHT CARDS
       ================================================== */

    .insight-card {
        background: rgba(13, 17, 24, 0.94);
        border-radius: 17px;
        padding: 21px;
        min-height: 175px;
        border: 1px solid #1e293b;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }

    .insight-card:hover {
        transform: translateY(-7px);
        box-shadow: 0 16px 32px rgba(148, 163, 184, 0.14);
    }

    .insight-title {
        font-size: 18px;
        font-weight: 750;
        color: #f8fafc;
        margin-bottom: 12px;
    }

    .insight-number {
        font-size: 25px;
        font-weight: 850;
        color: #f8fafc;
        margin: 6px 0;
    }

    .insight-text {
        font-size: 14px;
        color: #94a3b8;
        line-height: 1.6;
    }

    /* ==================================================
       TABLE CONTAINERS
       ================================================== */

    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid #1e293b;
        box-shadow: 0 7px 22px rgba(0, 0, 0, 0.5);
        transition: box-shadow 0.25s ease;
    }

    div[data-testid="stDataFrame"]:hover {
        box-shadow: 0 12px 28px rgba(59, 130, 246, 0.15);
    }

    /* ==================================================
       SELECT BOX
       ================================================== */

    div[data-baseweb="select"] > div {
        border-radius: 12px;
        border: 1px solid #1e293b;
        background: #0f141c;
    }

    /* ==================================================
       HIGH RISK
       ================================================== */

    .high-risk-panel {
        background: linear-gradient(135deg, #1a0b0d, #220d10);
        border: 1px solid #7f1d1d;
        border-left: 6px solid #ef4444;
        border-radius: 16px;
        padding: 21px;
        transition: transform 0.25s ease;
        animation: riskGlow 3s ease-in-out infinite;
    }

    .high-risk-panel:hover {
        transform: translateY(-5px);
    }

    @keyframes riskGlow {
        0%, 100% {
            box-shadow: 0 7px 20px rgba(239, 68, 68, 0.10);
        }
        50% {
            box-shadow: 0 7px 30px rgba(239, 68, 68, 0.35);
        }
    }

    .high-risk-title {
        font-size: 20px;
        font-weight: 800;
        color: #fca5a5;
        margin-bottom: 8px;
    }

    .high-risk-text {
        color: #fecaca;
        font-size: 14px;
        line-height: 1.6;
    }

    /* ==================================================
       METHODOLOGY HORIZONTAL BARS
       ================================================== */

    .methodology-bar {
        display: flex;
        align-items: center;
        background: linear-gradient(90deg, #0f141c, #0b0f16);
        border-radius: 14px;
        border: 1px solid #1e293b;
        border-left: 6px solid #3b82f6;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 5px 16px rgba(0, 0, 0, 0.45);
        transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    }

    .methodology-bar:hover {
        transform: translateX(7px);
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.20);
        border-color: #3b82f6;
    }

    .methodology-icon {
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        border-radius: 11px;
        background: #172033;
        font-size: 20px;
        margin-right: 15px;
    }

    .methodology-content {
        flex: 1;
    }

    .methodology-step {
        font-size: 11px;
        font-weight: 750;
        letter-spacing: 1px;
        color: #60a5fa;
        margin-bottom: 2px;
    }

    .methodology-title {
        font-size: 15px;
        font-weight: 750;
        color: #f8fafc;
        margin-bottom: 3px;
    }

    .methodology-description {
        font-size: 13px;
        color: #94a3b8;
        line-height: 1.5;
    }

    /* ==================================================
       DIVIDERS
       ================================================== */

    hr {
        border: none;
        border-top: 1px solid rgba(148, 163, 184, 0.15);
        margin: 28px 0;
    }


    /* ==================================================
       FRONT PAGE
       ================================================== */

    .hero {
        text-align: center;
        padding: 64px 20px 28px 20px;
    }

    .hero-title {
        font-size: 60px;
        font-weight: 850;
        color: #f8fafc;
        letter-spacing: -2px;
        line-height: 1.1;
        margin-bottom: 14px;
    }

    .hero-sub {
        font-size: 16px;
        color: #94a3b8;
    }

    </style>
    """,
    unsafe_allow_html=True
)

if not flow_lines:
    st.markdown(
        "<style>.stApp::before { display: none !important; }</style>",
        unsafe_allow_html=True
    )

# --------------------------------------------------
# Interactive particle background (K-Means clusters)
# Four colour groups = four risk tiers. Particles orbit
# their cluster centre and move away from the mouse.
# --------------------------------------------------

PARTICLE_JS = """
<script>
(function () {
  const win = window.parent;
  const doc = win.document;
  const ENABLED = __ENABLED__;

  // Toggle off: remove the canvas and stop the loop
  if (!ENABLED) {
    const old = doc.getElementById('risk-bg');
    if (old) old.remove();
    if (win.__riskBgRaf) win.cancelAnimationFrame(win.__riskBgRaf);
    win.__riskBgRaf = null;
    return;
  }

  // Already running: do nothing
  if (doc.getElementById('risk-bg')) return;

  const host = doc.querySelector('.stApp') || doc.body;
  const c = doc.createElement('canvas');
  c.id = 'risk-bg';
  c.style.cssText =
    'position:fixed;top:0;left:0;width:100vw;height:100vh;' +
    'z-index:0;pointer-events:none;';
  host.prepend(c);
  const ctx = c.getContext('2d');

  const colors = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444']; // Very Low, Low, Moderate, High
  const anchors = [[0.12, 0.30], [0.38, 0.72], [0.64, 0.28], [0.88, 0.68]];
  let W = 0, H = 0, t = 0;
  const mouse = { x: -9999, y: -9999 };

  function resize() {
    W = c.width = win.innerWidth;
    H = c.height = win.innerHeight;
  }
  resize();
  win.addEventListener('resize', resize);
  win.addEventListener('mousemove', function (e) {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  const P = [];
  colors.forEach(function (col, k) {
    for (let i = 0; i < 40; i++) {
      P.push({
        k: k,
        col: col,
        a: Math.random() * Math.PI * 2,
        r: 30 + Math.random() * 110,
        s: (Math.random() * 0.004 + 0.0015) * (Math.random() < 0.5 ? 1 : -1),
        x: W * anchors[k][0],
        y: H * anchors[k][1],
        size: Math.random() * 2 + 1.5
      });
    }
  });

  function frame() {
    t += 0.004;
    ctx.clearRect(0, 0, W, H);

    P.forEach(function (p) {
      p.a += p.s;
      const cx = W * anchors[p.k][0] + Math.sin(t + p.k * 1.7) * 50;
      const cy = H * anchors[p.k][1] + Math.cos(t * 0.8 + p.k * 2.1) * 40;
      let tx = cx + Math.cos(p.a) * p.r;
      let ty = cy + Math.sin(p.a) * p.r;

      const dx = tx - mouse.x;
      const dy = ty - mouse.y;
      const d = Math.hypot(dx, dy);
      if (d < 130 && d > 0) {
        tx += (dx / d) * (130 - d) * 0.6;
        ty += (dy / d) * (130 - d) * 0.6;
      }

      p.x += (tx - p.x) * 0.08;
      p.y += (ty - p.y) * 0.08;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.shadowBlur = 10;
      ctx.shadowColor = p.col;
      ctx.fillStyle = p.col + 'dd';
      ctx.fill();
      ctx.shadowBlur = 0;
    });

    // faint links between nearby points of the same cluster
    for (let i = 0; i < P.length; i++) {
      for (let j = i + 1; j < P.length; j++) {
        if (P[i].k !== P[j].k) continue;
        const d = Math.hypot(P[i].x - P[j].x, P[i].y - P[j].y);
        if (d < 55) {
          ctx.strokeStyle = P[i].col + '55';
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(P[i].x, P[i].y);
          ctx.lineTo(P[j].x, P[j].y);
          ctx.stroke();
        }
      }
    }

    win.__riskBgRaf = win.requestAnimationFrame(frame);
  }
  frame();
})();
</script>
"""

components.html(
    PARTICLE_JS.replace("__ENABLED__", "true" if animated_bg else "false"),
    height=0
)

# --------------------------------------------------
# Front-page illustrations (generated SVG, no image files needed)
# --------------------------------------------------

C_BG = "#0b101a"
C_PANEL = "#0e1522"
C_LINE = "#1f2a3d"
C_TEXT = "#f8fafc"
C_MUTED = "#94a3b8"
C_DIM = "#64748b"
C_GREEN = "#22c55e"
C_BLUE = "#3b82f6"
C_AMBER = "#f59e0b"
C_RED = "#ef4444"
C_PURPLE = "#8b5cf6"
C_CYAN = "#38bdf8"
MONO = "Consolas, Menlo, 'Courier New', monospace"


def _svg(width, height, body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" '
        f'font-family="Segoe UI, Inter, Helvetica, Arial, sans-serif">'
        f'<defs>{defs}'
        f'<marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{C_DIM}"/></marker>'
        f'</defs>{body}</svg>'
    )


def _card(x, y, w, h, stroke=C_LINE, fill=C_PANEL, r=16, extra=""):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="1.5" {extra}/>'
    )


def _text(x, y, s, size=16, fill=C_TEXT, weight=400, anchor="start", mono=False, extra=""):
    family = f' font-family="{MONO}"' if mono else ""
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
        f'font-weight="{weight}" text-anchor="{anchor}"{family} {extra}>{s}</text>'
    )


def _pill(x, y, w, h, label, color, size=13):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{color}" fill-opacity="0.16" '
        f'stroke="{color}" stroke-opacity="0.7"/>'
        + _text(x + w / 2, y + h / 2 + size * 0.35, label, size, color, 700, "middle")
    )


def _header(title, sub):
    return _text(44, 72, title, 32, C_TEXT, 800) + _text(44, 104, sub, 17, C_MUTED)


def _dot_on(path, color=C_BLUE, dur="2.4s", begin="0s", r=4.5):
    return (
        f'<circle r="{r}" fill="{color}">'
        f'<animateMotion dur="{dur}" begin="{begin}" repeatCount="indefinite" path="{path}"/>'
        f'</circle>'
    )


# --------------------------------------------------
# Overview workflow illustration (wide)
# --------------------------------------------------

def svg_overview():
    W, H = 1000, 580
    b = []

    # title row
    for i, col in enumerate([C_GREEN, C_BLUE, C_AMBER, C_RED]):
        b.append(f'<circle cx="{46 + (i % 2) * 14}" cy="{34 + (i // 2) * 14}" r="5.5" fill="{col}"/>')
    b.append(_text(72, 46, "Credit Score Risk Segmentation", 22, C_TEXT, 800))
    b.append(
        f'<text x="960" y="46" font-size="15" font-weight="700" text-anchor="end">'
        f'<tspan fill="{C_CYAN}">Stream the data. </tspan>'
        f'<tspan fill="#c4b5fd">Group the applicants. </tspan>'
        f'<tspan fill="{C_GREEN}">Read the risk.</tspan></text>'
    )

    # panel A: applicant records
    b.append('<g class="node" data-node="records">')
    b.append(_card(40, 86, 230, 170))
    b.append(_text(58, 114, "Applicant Records", 15, C_TEXT, 700))
    b.append(_text(252, 114, "1,000", 13, C_DIM, 600, "end"))
    rows = [C_GREEN, C_RED, C_GREEN, C_GREEN]
    for i, col in enumerate(rows):
        y = 130 + i * 26
        b.append(f'<rect x="58" y="{y}" width="194" height="22" rx="6" fill="#131c2e"/>')
        b.append(f'<circle cx="72" cy="{y + 11}" r="5" fill="{col}"/>')
        b.append(f'<rect x="88" y="{y + 8}" width="{70 + (i * 17) % 40}" height="6" rx="3" fill="#2a3750"/>')
        b.append(f'<rect x="{200 - (i * 9) % 20}" y="{y + 8}" width="{40 + (i * 7) % 12}" height="6" rx="3" fill="#2a3750"/>')
    b.append(_text(58, 248, "20 attributes + outcome", 12, C_DIM))
    b.append('</g>')

    # panel B: kafka topic
    b.append('<g class="node" data-node="kafka">')
    b.append(_card(40, 296, 230, 128))
    b.append(_text(58, 324, "Kafka Topic", 15, C_TEXT, 700))
    b.append(_text(58, 346, "credit-applicants", 13, C_CYAN, 400, mono=True))
    for i in range(6):
        x = 58 + i * 33
        b.append(f'<rect x="{x}" y="362" width="26" height="22" rx="5" fill="{C_BLUE}" fill-opacity="{0.25 + i * 0.12}" stroke="{C_BLUE}" stroke-opacity="0.6"/>')
    b.append(_text(58, 412, "1 message per applicant", 12, C_DIM))
    b.append('</g>')

    # center: HDFS card + features card
    b.append('<g class="node" data-node="hdfs">')
    b.append(_card(310, 86, 190, 76, stroke="#1f3a5f"))
    b.append(_text(328, 114, "HDFS", 15, C_TEXT, 700))
    b.append(_text(328, 138, "/credit-risk/raw", 13, C_CYAN, 400, mono=True))
    b.append('</g>')
    b.append('<g class="node" data-node="features">')
    b.append(_card(520, 86, 190, 76, stroke="#3b2f63"))
    b.append(_text(538, 114, "Features", 15, C_TEXT, 700))
    b.append(_text(538, 138, "1,000 x 27 prepared", 13, "#c4b5fd", 400))
    b.append('</g>')

    # center: monitor window with clusters
    b.append('<g class="node" data-node="kmeans">')
    b.append(_card(310, 196, 400, 236, r=14, stroke="#2a3a5a", fill="#0a111d"))
    b.append(f'<path d="M310,232 H710" stroke="#1f2a3d" stroke-width="1.5"/>')
    for i, col in enumerate([C_RED, C_AMBER, C_GREEN]):
        b.append(f'<circle cx="{330 + i * 16}" cy="214" r="4.5" fill="{col}" fill-opacity="0.85"/>')
    b.append(_text(700, 219, "K-Means  K = 4", 13, C_MUTED, 600, "end"))

    rnd = random.Random(11)
    clusters = [
        (C_GREEN, 380, 290, 16),
        (C_BLUE, 470, 352, 18),
        (C_AMBER, 568, 290, 20),
        (C_RED, 650, 356, 24),
    ]
    for col, cx, cy, s in clusters:
        for _ in range(24):
            x = min(max(rnd.gauss(cx, s), 328), 692)
            y = min(max(rnd.gauss(cy, s * 0.8), 246), 398)
            b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="{col}" fill-opacity="0.9"/>')
        b.append(f'<circle cx="{cx}" cy="{cy}" r="9" fill="none" stroke="#ffffff" stroke-opacity="0.75" stroke-width="1.6"/>')
    b.append(_text(510, 420, "silhouette 0.1384", 12, C_DIM, 400, "middle"))
    b.append('</g>')

    # right: risk tiers
    b.append('<g class="node" data-node="tiers">')
    b.append(_card(750, 86, 210, 232))
    b.append(_text(768, 114, "Risk Tiers", 15, C_TEXT, 700))
    tiers = [
        ("Very Low", C_GREEN, "234"),
        ("Low", C_BLUE, "269"),
        ("Moderate", C_AMBER, "348"),
        ("High", C_RED, "149"),
    ]
    for i, (name, col, n) in enumerate(tiers):
        y = 134 + i * 44
        b.append(f'<rect x="768" y="{y}" width="174" height="36" rx="9" fill="{col}" fill-opacity="0.12" stroke="{col}" stroke-opacity="0.55"/>')
        b.append(f'<circle cx="786" cy="{y + 18}" r="6" fill="{col}"/>')
        b.append(_text(802, y + 23, name, 14, C_TEXT, 600))
        b.append(_text(932, y + 23, n, 14, col, 700, "end"))
    b.append('</g>')

    # right: saved card
    b.append('<g class="node" data-node="saved">')
    b.append(_card(750, 350, 210, 82, stroke="#14532d", fill="#0b1a14"))
    b.append(f'<circle cx="778" cy="382" r="12" fill="{C_GREEN}"/>')
    b.append(f'<path d="M772,382 l5,5 l9,-10" stroke="#06210f" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    b.append(_text(800, 380, "Segments saved", 14, C_TEXT, 700))
    b.append(_text(800, 398, "HDFS /processed", 12, "#86efac", 400, mono=True))
    b.append(_text(768, 420, "final_risk_segments.csv", 11, C_DIM, 400, mono=True))
    b.append('</g>')

    # connectors
    paths = [
        "M155,256 L155,296",
        "M270,360 C300,360 285,124 310,124",
        "M500,124 L520,124",
        "M615,162 C615,180 560,180 560,196",
        "M710,330 C730,330 730,200 750,200",
        "M710,380 C730,380 730,390 750,390",
    ]
    for p in paths:
        b.append(f'<path d="{p}" fill="none" stroke="{C_DIM}" stroke-width="1.6" stroke-dasharray="4 5" marker-end="url(#ar)"/>')
    dots = [
        (paths[0], C_BLUE, "1.2s", "0s"),
        (paths[1], C_CYAN, "2.2s", "0.3s"),
        (paths[2], C_CYAN, "0.9s", "0.8s"),
        (paths[3], "#c4b5fd", "1.4s", "1.2s"),
        (paths[4], C_AMBER, "2.0s", "1.6s"),
        (paths[5], C_GREEN, "1.6s", "2.0s"),
    ]
    for p, col, dur, begin in dots:
        b.append(_dot_on(p, col, dur, begin))

    # bottom numbered steps
    steps = [
        ("Ingest", "Publish applicants to Kafka", C_BLUE),
        ("Store", "Keep raw data in HDFS", C_PURPLE),
        ("Cluster", "K-Means on 27 features", C_AMBER),
        ("Label", "Name the four risk tiers", C_GREEN),
    ]
    for i, (t, d, col) in enumerate(steps):
        x = 60 + i * 232
        b.append(f'<g class="node step-node" data-node="{["kafka", "hdfs", "kmeans", "tiers"][i]}">')
        b.append(f'<rect x="{x - 6}" y="484" width="214" height="52" rx="10" fill="transparent"/>')
        b.append(f'<circle cx="{x + 14}" cy="506" r="14" fill="none" stroke="{col}" stroke-width="2"/>')
        b.append(_text(x + 14, 511, str(i + 1), 14, col, 800, "middle"))
        b.append(_text(x + 38, 502, t, 15, C_TEXT, 700))
        b.append(_text(x + 38, 522, d, 12, C_DIM))
        b.append('</g>')
        if i < 3:
            b.append(f'<path d="M{x + 200},506 H{x + 222}" stroke="{C_LINE}" stroke-width="2"/>')

    return _svg(W, H, "".join(b))


def _data_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")


STORY_STEPS = [
    (
        "Start with the applicant data",
        "1,000 applicants, 20 attributes, one known outcome.",
        "The project uses the German Credit Risk dataset from UCI. The original symbolic file is converted "
        "into a labelled CSV with 21 columns. Category codes such as A11 and A34 are kept as they are, and "
        "the Good / Bad outcome is stored for later but not used to form the groups.",
    ),
    (
        "Stream it through Kafka",
        "Every applicant becomes one message.",
        "Each row is converted to JSON, given an applicant_id, and published to the credit-applicants topic. "
        "A consumer then reads all 1,000 messages and saves them as a raw CSV checkpoint, so the batch can be "
        "checked before it is stored.",
    ),
    (
        "Store it on HDFS",
        "Raw and final data live in separate folders.",
        "The checkpoint file is uploaded to /credit-risk/raw in Hadoop HDFS. After clustering, the final "
        "segmented file is written to /credit-risk/processed, so both the original data and the result are kept.",
    ),
    (
        "Prepare the features",
        "Turn categories and amounts into comparable numbers.",
        "Selected categorical attributes are one-hot encoded and numerical attributes are standardized, so no "
        "single scale dominates the distance calculation. This gives 27 clustering features. The credit-risk "
        "outcome is left out and used only afterwards to interpret the clusters.",
    ),
    (
        "Group similar applicants",
        "K-Means is tried with four and five clusters.",
        "Each applicant is assigned to the nearest cluster centre. K=4 scores 0.1384 on the silhouette score "
        "against 0.1330 for K=5, so four clusters are selected.",
    ),
    (
        "Name each group as a risk tier",
        "Cluster numbers become Very Low to High Risk.",
        "Each cluster is profiled by credit amount, duration, installment rate and its observed bad-credit rate, "
        "then named Very Low, Low, Moderate or High Risk. The result is the dashboard you see next.",
    ),
]

# --------------------------------------------------
# Page navigation (front page <-> dashboard)
# --------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "front"


def go_to(page_name):
    st.session_state.page = page_name


# --------------------------------------------------
# Interactive workflow diagram
# Click a box in the diagram and its description appears on the left.
# Runs entirely in the browser (no Streamlit rerun), so it is instant.
# --------------------------------------------------

FLOW_NODE_STEPS = {
    "records": 0,
    "kafka": 1,
    "hdfs": 2,
    "features": 3,
    "kmeans": 4,
    "tiers": 5,
}

FLOW_PAGE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
  html, body {
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: "Source Sans Pro", "Segoe UI", Inter, Helvetica, Arial, sans-serif;
  }

  .flow-card {
    box-sizing: border-box;
    display: grid;
    grid-template-columns: minmax(0, 0.8fr) minmax(0, 2.2fr);
    gap: 36px;
    align-items: center;
    padding: 46px;
    border-radius: 34px;
    border: 1px solid #1b2742;
    background: linear-gradient(145deg, rgba(14, 20, 34, 0.97), rgba(8, 11, 19, 0.97));
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
  }

  .flow-label {
    font-family: Consolas, Menlo, monospace;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 3px;
    color: #6366f1;
    margin-bottom: 20px;
  }

  .flow-title {
    font-size: 46px;
    font-weight: 850;
    color: #f8fafc;
    letter-spacing: -1.4px;
    line-height: 1.08;
    margin-bottom: 18px;
  }

  .flow-title.small {
    font-size: 34px;
    letter-spacing: -1px;
  }

  .flow-lead {
    display: none;
    font-size: 18px;
    font-weight: 750;
    color: #e2e8f0;
    line-height: 1.4;
    margin-bottom: 12px;
  }

  .flow-text {
    font-size: 16px;
    color: #94a3b8;
    line-height: 1.7;
  }

  .flow-hint {
    margin-top: 22px;
    font-size: 14px;
    font-weight: 650;
    color: #f59e0b;
  }

  .flow-back {
    display: none;
    margin-top: 24px;
    padding: 9px 16px;
    border-radius: 10px;
    border: 1px solid #334155;
    background: #0f141c;
    color: #e2e8f0;
    font-size: 14px;
    font-weight: 650;
    cursor: pointer;
    font-family: inherit;
  }

  .flow-back:hover {
    border-color: #f59e0b;
    color: #fbbf24;
  }

  .flow-visual svg {
    width: 100%;
    height: auto;
    display: block;
  }

  /* clickable boxes */
  .node {
    cursor: pointer;
    transition: filter 0.2s ease;
    outline: none;
  }

  .node:hover {
    filter: brightness(1.3);
  }

  .node.active {
    filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
  }

  .node.active:not(.step-node) > rect:first-of-type {
    stroke: #ffffff;
    stroke-width: 2.5;
  }

  .step-node.active circle {
    fill: rgba(255, 255, 255, 0.18);
  }

  @media (max-width: 1000px) {
    .flow-card { grid-template-columns: 1fr; padding: 28px; }
    .flow-title { font-size: 34px; }
  }
</style>
</head>
<body>
  <div class="flow-card" id="card">
    <div class="flow-copy">
      <div class="flow-label" id="lab">DATA WORKFLOW</div>
      <div class="flow-title" id="ttl">From raw records to clear risk tiers.</div>
      <div class="flow-lead" id="led"></div>
      <div class="flow-text" id="txt"></div>
      <div class="flow-hint" id="hint">Click any box in the diagram to see what happens at that stage.</div>
      <button class="flow-back" id="back" type="button">&larr; Back to overview</button>
    </div>
    <div class="flow-visual">__SVG__</div>
  </div>

<script>
(function () {
  var DATA = __DATA__;
  var INTRO = {
    label: "DATA WORKFLOW",
    title: "From raw records to clear risk tiers.",
    lead: "",
    text: "Applicant data is streamed, stored, prepared and grouped. " +
          "Each stage feeds the next, ending in four risk tiers you can explore on the dashboard."
  };

  function el(id) { return document.getElementById(id); }
  var nodes = document.querySelectorAll('.node');
  var card = el('card');

  function fit() {
    try {
      var h = card.getBoundingClientRect().height + 24;
      window.frameElement.style.height = Math.ceil(h) + 'px';
    } catch (e) {}
  }

  function show(id) {
    var d = id ? DATA[id] : INTRO;
    el('lab').textContent = d.label;
    el('ttl').textContent = d.title;
    el('ttl').className = 'flow-title' + (id ? ' small' : '');
    el('led').textContent = d.lead;
    el('led').style.display = d.lead ? 'block' : 'none';
    el('txt').textContent = d.text;
    el('hint').style.display = id ? 'none' : 'block';
    el('back').style.display = id ? 'inline-block' : 'none';
    for (var i = 0; i < nodes.length; i++) {
      var active = id !== null && nodes[i].getAttribute('data-node') === id;
      if (active) { nodes[i].classList.add('active'); } else { nodes[i].classList.remove('active'); }
    }
    fit();
  }

  for (var i = 0; i < nodes.length; i++) {
    (function (n) {
      n.setAttribute('tabindex', '0');
      n.setAttribute('role', 'button');
      n.addEventListener('click', function () { show(n.getAttribute('data-node')); });
      n.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); show(n.getAttribute('data-node')); }
      });
    })(nodes[i]);
  }

  el('back').addEventListener('click', function () { show(null); });

  show(null);
  window.addEventListener('resize', fit);
  if (window.ResizeObserver) { new ResizeObserver(fit).observe(card); }
  setTimeout(fit, 80);
})();
</script>
</body>
</html>
"""


@st.cache_data
def build_flow_html():
    data = {}
    for key, i in FLOW_NODE_STEPS.items():
        title, lead, text = STORY_STEPS[i]
        data[key] = {"label": f"STEP {i + 1} OF 6", "title": title, "lead": lead, "text": text}

    data["saved"] = {
        "label": "OUTPUT",
        "title": "Segments saved",
        "lead": "The result is stored next to the raw data, in a separate folder.",
        "text": "After clustering, the final segmented file, final_risk_segments.csv, is written to "
                "/credit-risk/processed in HDFS, so both the original data and the result are kept.",
    }

    payload = json.dumps(data).replace("</", "<\\/")
    return FLOW_PAGE.replace("__SVG__", svg_overview()).replace("__DATA__", payload)


if st.session_state.page == "front":

    flow_html = build_flow_html()

    st.markdown(
        '<div class="hero">'
        '<div class="hero-title">📊 Credit Score Risk Segmentation</div>'
        '<div class="hero-sub">Segmenting loan applicants into four risk tiers using the German Credit Risk dataset</div>'
        '</div>',
        unsafe_allow_html=True
    )

    _, btn_col, _ = st.columns([1.2, 1, 1.2])
    with btn_col:
        st.button(
            "View Dashboard →",
            on_click=go_to,
            args=("dashboard",),
            use_container_width=True,
            type="primary",
            key="enter_top"
        )
    st.markdown("<div style='height:108px'></div>", unsafe_allow_html=True)
    components.html(flow_html, height=800)

    st.stop()

# --------------------------------------------------
# Load data
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    summary = pd.read_csv(SUMMARY_FILE)
    return df, summary


df, summary = load_data()

# --------------------------------------------------
# Title
# --------------------------------------------------

st.button("← Back", on_click=go_to, args=("front",), key="back_front")


st.markdown(
    '<div class="main-title">📊 Credit Score Risk Segmentation</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Applicant financial data is processed and segmented into four risk tiers using K-Means clustering.'
    '</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# Architecture Pipeline
# --------------------------------------------------

architecture = [
    ("📨", "Kafka", "Data Ingestion"),
    ("🗄️", "HDFS", "Data Storage"),
    ("🤖", "K-Means", "Clustering"),
    ("📊", "Risk Tiers", "Segmentation")
]

cols = st.columns([2, 0.35, 2, 0.35, 2, 0.35, 2])

for i, item in enumerate(architecture):

    icon, title, subtitle = item

    with cols[i * 2]:
        st.markdown(
            f"""
            <div class="architecture-card step-{i}">
                <div class="architecture-icon">{icon}</div>
                <div class="architecture-title">{title}</div>
                <div class="architecture-subtitle">{subtitle}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if i < 3:
        with cols[i * 2 + 1]:
            st.markdown(
                f'<div class="architecture-arrow arrow-{i}">→</div>',
                unsafe_allow_html=True
            )

st.divider()

# --------------------------------------------------
# Key metrics
# --------------------------------------------------

total_applicants = len(df)

high_risk = int(
    summary.loc[
        summary["risk_tier"] == "High Risk",
        "applicants"
    ].iloc[0]
)

moderate_risk = int(
    summary.loc[
        summary["risk_tier"] == "Moderate Risk",
        "applicants"
    ].iloc[0]
)

avg_credit = df["credit_amount"].mean()

high_risk_pct = high_risk / total_applicants * 100
moderate_risk_pct = moderate_risk / total_applicants * 100

st.markdown(
    '<div class="section-header">Portfolio Overview</div>',
    unsafe_allow_html=True
)

metric_cols = st.columns(4)

metrics = [
    ("👥", "Total Applicants", f"{total_applicants:,}", "100% of analyzed applicants"),
    ("🔴", "High Risk", f"{high_risk:,}", f"{high_risk_pct:.1f}% of applicants"),
    ("🟠", "Moderate Risk", f"{moderate_risk:,}", f"{moderate_risk_pct:.1f}% of applicants"),
    ("💳", "Average Credit Amount", f"{avg_credit:,.0f}", "Across all applicants")
]

for col, metric in zip(metric_cols, metrics):

    icon, label, value, description = metric

    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{icon} {label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-description">{description}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()

# --------------------------------------------------
# K-Means Model Evaluation
# --------------------------------------------------

st.markdown(
    '<div class="section-header">Model Evaluation</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'The number of clusters was evaluated using the Silhouette Score for K=4 and K=5.'
    '</div>',
    unsafe_allow_html=True
)

eval_cols = st.columns(3)

evaluation = [
    ("K = 4", "0.1384"),
    ("K = 5", "0.1330"),
    ("Selected K", "4")
]

for col, item in zip(eval_cols, evaluation):

    label, value = item

    with col:
        st.markdown(
            f"""
            <div class="evaluation-card">
                <div class="evaluation-label">{label}</div>
                <div class="evaluation-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

st.success(
    "K=4 was selected because it achieved the higher silhouette "
    "score (0.1384) compared with K=5 (0.1330)."
)

st.divider()

# --------------------------------------------------
# Risk-Tier Distribution
# --------------------------------------------------

st.markdown(
    '<div class="section-header">Risk-Tier Distribution</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Distribution of applicants across the four cluster-derived risk tiers.'
    '</div>',
    unsafe_allow_html=True
)

risk_order = [
    "Very Low Risk",
    "Low Risk",
    "Moderate Risk",
    "High Risk"
]

chart_data = (
    summary
    .set_index("risk_tier")
    .reindex(risk_order)
    .reset_index()
)

risk_colors = [
    "#22c55e",
    "#3b82f6",
    "#f59e0b",
    "#ef4444"
]

chart = (
    alt.Chart(chart_data)
    .mark_bar(
        cornerRadiusTopLeft=8,
        cornerRadiusTopRight=8
    )
    .encode(
        x=alt.X(
            "risk_tier:N",
            sort=risk_order,
            title="Risk Tier",
            axis=alt.Axis(labelAngle=0)
        ),
        y=alt.Y(
            "applicants:Q",
            title="Applicants",
            scale=alt.Scale(domain=[0, 400])
        ),
        color=alt.Color(
            "risk_tier:N",
            scale=alt.Scale(
                domain=risk_order,
                range=risk_colors
            ),
            legend=None
        ),
        tooltip=[
            alt.Tooltip("risk_tier:N", title="Risk Tier"),
            alt.Tooltip("applicants:Q", title="Applicants")
        ]
    )
    .properties(height=400)
    .configure(background="transparent")
    .configure_axis(
        labelColor="#cbd5e1",
        titleColor="#e2e8f0",
        gridColor="#1e293b",
        domainColor="#334155",
        tickColor="#334155"
    )
    .configure_view(strokeWidth=0)
)

st.altair_chart(chart, use_container_width=True, theme=None)

st.divider()

# --------------------------------------------------
# Risk Insights
# --------------------------------------------------

st.markdown(
    '<div class="section-header">Risk Insights</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Key observations from the cluster profiles and observed credit-risk outcomes.'
    '</div>',
    unsafe_allow_html=True
)

very_low = summary[summary["risk_tier"] == "Very Low Risk"].iloc[0]
low = summary[summary["risk_tier"] == "Low Risk"].iloc[0]
moderate = summary[summary["risk_tier"] == "Moderate Risk"].iloc[0]
high = summary[summary["risk_tier"] == "High Risk"].iloc[0]

insight_cols = st.columns(4)

insights = [
    ("🟢", "Very Low Risk", f"{int(very_low['applicants'])} applicants",
     f"Bad-credit rate: {very_low['bad_credit_pct']:.2f}%"),
    ("🔵", "Low Risk", f"{int(low['applicants'])} applicants",
     f"Bad-credit rate: {low['bad_credit_pct']:.2f}%"),
    ("🟠", "Moderate Risk", f"{int(moderate['applicants'])} applicants",
     f"Bad-credit rate: {moderate['bad_credit_pct']:.2f}%"),
    ("🔴", "High Risk", f"{int(high['applicants'])} applicants",
     f"Bad-credit rate: {high['bad_credit_pct']:.2f}%")
]

for col, insight in zip(insight_cols, insights):

    icon, title, number, text = insight

    with col:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">{icon} {title}</div>
                <div class="insight-number">{number}</div>
                <div class="insight-text">{text}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.divider()

# --------------------------------------------------
# Risk-Tier Profile
# --------------------------------------------------

st.markdown(
    '<div class="section-header">Risk-Tier Profile</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Comparison of applicant characteristics and observed credit-risk outcomes across risk tiers.'
    '</div>',
    unsafe_allow_html=True
)

display_columns = [
    "risk_tier",
    "applicants",
    "applicant_pct",
    "avg_credit_amount",
    "avg_duration_months",
    "avg_installment_rate",
    "good_credit_pct",
    "bad_credit_pct"
]

display_df = summary[display_columns].copy()

display_df.columns = [
    "Risk Tier",
    "Applicants",
    "Applicant %",
    "Avg Credit Amount",
    "Avg Duration (Months)",
    "Avg Installment Rate",
    "Good Credit %",
    "Bad Credit %"
]

numeric_columns = [
    "Applicant %",
    "Avg Credit Amount",
    "Avg Duration (Months)",
    "Avg Installment Rate",
    "Good Credit %",
    "Bad Credit %"
]

for column in numeric_columns:
    display_df[column] = display_df[column].round(2)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=220
)

st.divider()

# --------------------------------------------------
# Applicant Risk Explorer
# --------------------------------------------------

st.markdown(
    '<div class="section-header">Applicant Risk Explorer</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-description">'
    'Explore individual applicants and their assigned risk tiers.'
    '</div>',
    unsafe_allow_html=True
)

risk_options = [
    "All",
    "Very Low Risk",
    "Low Risk",
    "Moderate Risk",
    "High Risk"
]

selected_risk = st.selectbox(
    "Select Risk Tier",
    risk_options
)

if selected_risk == "All":
    filtered_df = df.copy()
else:
    filtered_df = df[df["risk_tier"] == selected_risk]

st.write(f"Showing **{len(filtered_df):,} applicants**")

table_columns = [
    "applicant_id",
    "credit_amount",
    "duration_months",
    "installment_rate",
    "age",
    "existing_credits",
    "credit_history",
    "checking_account",
    "savings_account",
    "credit_risk",
    "cluster",
    "risk_tier"
]

st.dataframe(
    filtered_df[table_columns],
    use_container_width=True,
    hide_index=True,
    height=430
)

st.divider()

# --------------------------------------------------
# High-Risk Segment Characteristics
# --------------------------------------------------

st.markdown(
    '<div class="section-header">High-Risk Segment Characteristics</div>',
    unsafe_allow_html=True
)

high_risk_profile = summary[summary["risk_tier"] == "High Risk"].iloc[0]

high_cols = st.columns(3)

high_metrics = [
    ("Average Credit Amount", f"{high_risk_profile['avg_credit_amount']:,.2f}"),
    ("Average Duration", f"{high_risk_profile['avg_duration_months']:.2f} months"),
    ("Bad Credit Rate", f"{high_risk_profile['bad_credit_pct']:.2f}%")
]

for col, metric in zip(high_cols, high_metrics):

    label, value = metric

    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="high-risk-panel">
        <div class="high-risk-title">
            🔴 High-Risk Segment
        </div>
        <div class="high-risk-text">
            The High Risk segment has the highest average credit amount,
            the longest average repayment duration, and the highest
            observed proportion of bad-credit outcomes among the four
            clusters.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.markdown(
    "<br><div style='text-align:center; color:#94a3b8; font-size:13px;'>"
    "Credit Score Risk Segmentation"
    "</div>",
    unsafe_allow_html=True
)