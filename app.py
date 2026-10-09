"""
AI Career Guide Agent — Main Streamlit App
Supports SDG 8: Decent Work and Economic Growth

Run with:
    python -m streamlit run app.py
"""
import json
import os
import sys
import time
import csv
from datetime import datetime
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from utils.translations import t
from utils.matcher import match_jobs
from utils.resume_generator import generate_resume_pdf, REPORTLAB_AVAILABLE

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Career Guide",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main {
    background: #0f172a !important;
    font-family: 'Inter', -apple-system, "Segoe UI", sans-serif;
    color: #f1f5f9;
}

[data-testid="stAppViewContainer"] > .main > .block-container {
    max-width: 720px !important;
    padding: 0 1rem 4rem 1rem !important;
}

/* hide streamlit chrome */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ── Top Nav Bar ── */
.topbar {
    background: linear-gradient(135deg, #1e3a5f 0%, #1a1a3e 100%);
    border-radius: 0 0 20px 20px;
    padding: 1rem 1.4rem 1.2rem;
    margin: 0 -1rem 1.8rem -1rem;
    border-bottom: 2px solid #3b82f6;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
}
.topbar-title { font-size: 1.3rem; font-weight: 800; color: #fff; }
.topbar-sub   { font-size: 0.78rem; color: #93c5fd; margin-top: 2px; }
.sdg-tag {
    background: rgba(134,239,172,0.15);
    border: 1px solid #4ade80;
    color: #4ade80;
    border-radius: 999px;
    padding: 0.22rem 0.85rem;
    font-size: 0.72rem;
    font-weight: 600;
    white-space: nowrap;
}

/* ── Step progress strip ── */
.steps-strip {
    display: flex;
    gap: 0.3rem;
    margin-bottom: 1.4rem;
    align-items: center;
}
.step-dot {
    flex: 1;
    height: 6px;
    background: #1e293b;
    border-radius: 999px;
}
.step-dot.done  { background: #3b82f6; }
.step-dot.active{ background: #818cf8; }
.steps-label {
    font-size: 0.75rem;
    color: #64748b;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

/* ── Generic card ── */
.card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1.1rem;
}
.card-blue {
    background: linear-gradient(135deg, #1e3a5f 0%, #1e2d4f 100%);
    border: 1px solid #3b82f6;
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    margin-bottom: 1.1rem;
}
.card-green {
    background: #052e16;
    border: 1px solid #16a34a;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
    color: #bbf7d0;
}
.card-amber {
    background: #1c1400;
    border: 1px solid #d97706;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
    color: #fde68a;
}
.card-purple {
    background: #1a0533;
    border: 1px solid #7c3aed;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
}

/* ── Hero section ── */
.hero-icon { font-size: 3.2rem; text-align: center; margin-bottom: 0.6rem; }
.hero-title {
    font-size: 2rem;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 0.5rem;
}
.hero-sub {
    text-align: center;
    color: #94a3b8;
    font-size: 0.95rem;
    line-height: 1.6;
    margin-bottom: 1.5rem;
}

/* ── Feature list items ── */
.feat-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.75rem 0;
    border-bottom: 1px solid #1e293b;
}
.feat-item:last-child { border-bottom: none; }
.feat-icon {
    background: #1e3a5f;
    border-radius: 10px;
    width: 40px;
    height: 40px;
    min-width: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.15rem;
}
.feat-text-title { font-size: 0.92rem; font-weight: 600; color: #f1f5f9; }
.feat-text-sub   { font-size: 0.8rem; color: #64748b; margin-top: 1px; }

/* ── Language buttons ── */
.lang-row { display: flex; gap: 0.8rem; margin: 1rem 0; }

/* ── Streamlit button overrides ── */
div[data-testid="stButton"] > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1.2rem !important;
    transition: all 0.15s !important;
    width: 100% !important;
    border: none !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%) !important;
    color: white !important;
    font-size: 1.05rem !important;
    padding: 0.8rem 1.5rem !important;
}
div[data-testid="stButton"] > button[kind="secondary"],
div[data-testid="stButton"] > button[kind="tertiary"],
div[data-testid="stButton"] > button:not([kind]) {
    background: #1e293b !important;
    color: #cbd5e1 !important;
    border: 1px solid #334155 !important;
}
div[data-testid="stButton"] > button:hover { opacity: 0.88 !important; }

/* ── Form inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: #1e293b !important;
    border: 1.5px solid #334155 !important;
    border-radius: 12px !important;
    color: #f1f5f9 !important;
    font-size: 1rem !important;
    padding: 0.7rem 1rem !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.2) !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* ── Streamlit expander ── */
div[data-testid="stExpander"] {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 14px !important;
    margin-bottom: 0.8rem !important;
    overflow: hidden !important;
}
div[data-testid="stExpander"] summary {
    color: #f1f5f9 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 1rem 1.2rem !important;
}
div[data-testid="stExpander"] summary:hover { background: #263348 !important; }
div[data-testid="stExpander"] > div { padding: 0.5rem 1.2rem 1.2rem !important; }

/* ── Progress bar ── */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg,#3b82f6,#818cf8) !important;
    border-radius: 999px !important;
}
div[data-testid="stProgress"] > div {
    background: #1e293b !important;
    border-radius: 999px !important;
    height: 10px !important;
}

/* ── Select slider ── */
div[data-testid="stSlider"] label { color: #94a3b8 !important; }

/* ── Chat bubbles ── */
.bubble-agent {
    background: #1e3a5f;
    border: 1px solid #2563eb;
    border-radius: 18px 18px 18px 4px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.9rem;
    font-size: 1rem;
    line-height: 1.65;
    color: #e2e8f0;
}
.bubble-user {
    background: #1a1a3e;
    border: 1px solid #4338ca;
    border-radius: 18px 18px 4px 18px;
    padding: 0.8rem 1.1rem;
    margin-bottom: 0.7rem;
    margin-left: 2.5rem;
    font-size: 0.95rem;
    color: #c7d2fe;
}
.bot-label {
    font-size: 0.72rem;
    color: #60a5fa;
    font-weight: 600;
    margin-bottom: 0.3rem;
    letter-spacing: 0.5px;
}
.user-label {
    font-size: 0.72rem;
    color: #818cf8;
    font-weight: 600;
    margin-bottom: 0.3rem;
    text-align: right;
    letter-spacing: 0.5px;
}

/* ── Skill pills ── */
.pill-have {
    display: inline-block;
    background: #052e16;
    border: 1px solid #16a34a;
    color: #4ade80;
    border-radius: 999px;
    padding: 0.25rem 0.85rem;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 0.2rem 0.15rem;
}
.pill-need {
    display: inline-block;
    background: #1c0a00;
    border: 1px solid #d97706;
    color: #fbbf24;
    border-radius: 999px;
    padding: 0.25rem 0.85rem;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 0.2rem 0.15rem;
}

/* ── Match percentage ring ── */
.match-ring {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(59,130,246,0.12);
    border: 1.5px solid #3b82f6;
    border-radius: 999px;
    padding: 0.3rem 1rem 0.3rem 0.5rem;
    font-size: 1rem;
    font-weight: 700;
    color: #60a5fa;
    margin-bottom: 0.8rem;
}
.match-ring .ring-dot {
    width: 10px; height: 10px;
    background: #3b82f6;
    border-radius: 50%;
}

/* ── Resource links ── */
.res-link {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    margin-bottom: 0.5rem;
    text-decoration: none;
    color: #93c5fd;
    font-size: 0.88rem;
    font-weight: 500;
    transition: border-color 0.15s;
}
.res-link:hover { border-color: #3b82f6; color: #60a5fa; }
.res-icon { font-size: 1rem; }

/* ── Section label ── */
.sec-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #475569;
    margin: 1.2rem 0 0.5rem 0;
}

/* ── Big stat ── */
.stat-box {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 0.9rem;
    text-align: center;
}
.stat-box .stat-val { font-size: 1.5rem; font-weight: 800; color: #60a5fa; }
.stat-box .stat-lbl { font-size: 0.75rem; color: #64748b; margin-top: 2px; }

/* ── Footer ── */
.footer-bar {
    text-align: center;
    font-size: 0.75rem;
    color: #475569;
    padding: 1.5rem 0 0.5rem;
    border-top: 1px solid #1e293b;
    margin-top: 2rem;
}

/* ── Divider ── */
.divider { height: 1px; background: #1e293b; margin: 1rem 0; }

/* ── Alert / info boxes ── */
div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
    font-size: 0.9rem !important;
}

/* ── Download button ── */
div[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #059669 0%, #0d9488 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    padding: 0.85rem !important;
    width: 100% !important;
}

/* ── Feedback stars ── */
div[data-testid="stSlider"] {
    padding: 0.5rem 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
DEFAULTS = {
    "screen":        "welcome",
    "lang":          "en",
    "chat_step":     0,
    "profile":       {},
    "results":       [],
    "chat_history":  [],
    "resume_pdf":    None,
    "feedback_done": False,
    "metrics":       {},
    "compare_done":  False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

QUESTIONS = [
    ("education",  "q_education"),
    ("skills",     "q_skills"),
    ("interests",  "q_interests"),
    ("city",       "q_city"),
    ("experience", "q_experience"),
    ("work_type",  "q_work_type"),
]

def lang(): return st.session_state["lang"]
def tr(key, **kw): return t(key, lang(), **kw)
def go_to(s):
    st.session_state["screen"] = s
    st.rerun()
def save_metric(k, v=1):
    st.session_state["metrics"][k] = st.session_state["metrics"].get(k, 0) + v

def topbar(subtitle=""):
    st.markdown(f"""
    <div class="topbar">
      <div>
        <div class="topbar-title">🎯 AI Career Guide</div>
        <div class="topbar-sub">{subtitle if subtitle else ("आपका AI करियर सलाहकार" if lang()=="hi" else "Your AI Career Advisor — Free · Fast · Local")}</div>
      </div>
    </div>""", unsafe_allow_html=True)

def save_feedback(rating, comment):
    log_path = ROOT / "data" / "feedback_log.csv"
    is_new = not log_path.exists()
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(["timestamp","rating","comment","city","education","top_role"])
        p = st.session_state.get("profile", {})
        top = (st.session_state.get("results") or [{}])[0].get("title","")
        w.writerow([datetime.now().isoformat(), rating, comment,
                    p.get("city",""), p.get("education",""), top])


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 1 — WELCOME
# ══════════════════════════════════════════════════════════════════════════════
def screen_welcome():
    topbar()

    # Hero
    st.markdown("""
    <div style='text-align:center; padding: 0.5rem 0 1rem'>
      <div style='font-size:3.5rem; margin-bottom:0.4rem'>🎯</div>
      <div class='hero-title'>AI Career Guide</div>
      <div class='hero-sub'>
        Free career advice for students &amp; job seekers<br>
        in Tier-2 &amp; Tier-3 cities of India
      </div>
    </div>""", unsafe_allow_html=True)

    # What you get
    st.markdown("<div class='sec-label'>What you'll get in 2 minutes</div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card'>
      <div class='feat-item'>
        <div class='feat-icon'>🗺️</div>
        <div><div class='feat-text-title'>Top 3 Career Paths</div>
             <div class='feat-text-sub'>Matched to YOUR skills and interests</div></div>
      </div>
      <div class='feat-item'>
        <div class='feat-icon'>📌</div>
        <div><div class='feat-text-title'>Skill Gap Analysis</div>
             <div class='feat-text-sub'>Exactly what you need to learn next</div></div>
      </div>
      <div class='feat-item'>
        <div class='feat-icon'>📚</div>
        <div><div class='feat-text-title'>Free Learning Resources</div>
             <div class='feat-text-sub'>IBM SkillsBuild, NPTEL, YouTube &amp; more</div></div>
      </div>
      <div class='feat-item'>
        <div class='feat-icon'>📄</div>
        <div><div class='feat-text-title'>Downloadable Resume (PDF)</div>
             <div class='feat-text-sub'>ATS-friendly resume generated for you</div></div>
      </div>
      <div class='feat-item'>
        <div class='feat-icon'>📍</div>
        <div><div class='feat-text-title'>Local City Jobs</div>
             <div class='feat-text-sub'>Roles available near your city right now</div></div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Language
    st.markdown("<div class='sec-label'>Choose your language / अपनी भाषा चुनें</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        active_en = "✅ " if lang()=="en" else ""
        if st.button(f"{active_en}🇬🇧  English", use_container_width=True):
            st.session_state["lang"] = "en"
            st.rerun()
    with c2:
        active_hi = "✅ " if lang()=="hi" else ""
        if st.button(f"{active_hi}🇮🇳  हिंदी", use_container_width=True):
            st.session_state["lang"] = "hi"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    btn_label = "🚀  Start — Find My Career Path  →" if lang()=="en" else "🚀  शुरू करें — मेरा करियर खोजें  →"
    if st.button(btn_label, type="primary", use_container_width=True):
        greeting = (
            "नमस्ते! 🙏 मैं आपका AI कैरियर गाइड हूं।\nमैं आपसे 6 छोटे सवाल पूछूंगा और आपके लिए सबसे अच्छे करियर विकल्प खोजूंगा।\n\n"
            if lang()=="hi" else
            "Hello! 🙏 I'm your AI Career Guide.\nI'll ask you 6 quick questions and find the best career paths for you.\n\n"
        )
        first_q = tr(QUESTIONS[0][1])
        st.session_state["chat_history"] = [{"role":"agent","text": greeting + first_q}]
        st.session_state["chat_step"] = 0
        st.session_state["profile"] = {}
        save_metric("sessions_started")
        go_to("chat")

    st.markdown("""
    <div class='footer-bar'>
      🔒 No login &nbsp;•&nbsp; 100% Free &nbsp;•&nbsp; No data stored online<br>
      Made for India's Tier-2/3 youth
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 2 — CHAT
# ══════════════════════════════════════════════════════════════════════════════
def screen_chat():
    step     = st.session_state["chat_step"]
    history  = st.session_state["chat_history"]
    topbar("Chat with your AI Career Guide" if lang()=="en" else "AI कैरियर गाइड से चैट करें")

    # ── Step indicators ────────────────────────────────────────────────────
    dots_html = ""
    for i in range(len(QUESTIONS)):
        cls = "done" if i < step else ("active" if i == step else "")
        dots_html += f"<div class='step-dot {cls}'></div>"

    q_label = (f"Question {step+1} of {len(QUESTIONS)}" if lang()=="en"
               else f"प्रश्न {step+1} / {len(QUESTIONS)}")
    st.markdown(f"<div class='steps-label'>{q_label}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='steps-strip'>{dots_html}</div>", unsafe_allow_html=True)

    # ── Chat history ───────────────────────────────────────────────────────
    for msg in history:
        if msg["role"] == "agent":
            bot_lbl  = "🤖 AI Career Guide" if lang()=="en" else "🤖 AI कैरियर गाइड"
            st.markdown(
                f"<div class='bot-label'>{bot_lbl}</div>"
                f"<div class='bubble-agent'>{msg['text'].replace(chr(10),'<br>')}</div>",
                unsafe_allow_html=True,
            )
        else:
            you_lbl = "👤 You" if lang()=="en" else "👤 आप"
            st.markdown(
                f"<div class='user-label'>{you_lbl}</div>"
                f"<div class='bubble-user'>{msg['text']}</div>",
                unsafe_allow_html=True,
            )

    # ── Input form ─────────────────────────────────────────────────────────
    if step < len(QUESTIONS):
        profile_key = QUESTIONS[step][0]
        hint_map_en = {
            "education":  "e.g.  B.Tech / BCA / 12th Pass / ITI / BA",
            "skills":     "e.g.  Python, Excel, Canva, Tally, Welding",
            "interests":  "e.g.  computers, teaching, design, sales",
            "city":       "e.g.  Indore / Jaipur / Nagpur / Patna",
            "experience": "e.g.  Fresher / 0-1 year / 1-3 years",
            "work_type":  "e.g.  Office / Remote / Freelance",
        }
        hint_map_hi = {
            "education":  "जैसे: B.Tech / BCA / 12वीं / ITI / BA",
            "skills":     "जैसे: Python, Excel, Canva, Tally",
            "interests":  "जैसे: कंप्यूटर, पढ़ाना, डिज़ाइन, सेल्स",
            "city":       "जैसे: इंदौर / जयपुर / नागपुर / पटना",
            "experience": "जैसे: Fresher / 0-1 साल / 1-3 साल",
            "work_type":  "जैसे: ऑफिस / रिमोट / फ्रीलांस",
        }
        ph = hint_map_hi.get(profile_key,"") if lang()=="hi" else hint_map_en.get(profile_key,"")

        send_lbl = "Send  ➤" if lang()=="en" else "भेजें  ➤"
        with st.form(key=f"cf_{step}", clear_on_submit=True):
            ans = st.text_input(
                "Your answer:" if lang()=="en" else "आपका जवाब:",
                placeholder=ph,
            )
            sent = st.form_submit_button(send_lbl, type="primary", use_container_width=True)

        if sent and ans.strip():
            st.session_state["profile"][profile_key] = ans.strip()
            history.append({"role":"user","text": ans.strip()})
            nxt = step + 1
            st.session_state["chat_step"] = nxt
            if nxt < len(QUESTIONS):
                history.append({"role":"agent","text": tr(QUESTIONS[nxt][1])})
                st.rerun()
            else:
                done = ("शानदार! 🎉 आपने सभी जानकारी दे दी।\nअब मैं आपके लिए करियर विकल्प खोजता हूं..."
                        if lang()=="hi" else
                        "Excellent! 🎉 All done!\nFinding the best career paths for you now...")
                history.append({"role":"agent","text": done})
                go_to("analysing")

    # ── Back button ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back" if lang()=="en" else "← वापस", use_container_width=True):
        if step > 0:
            st.session_state["chat_history"] = history[:-2]
            st.session_state["chat_step"] = step - 1
            st.rerun()
        else:
            go_to("welcome")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 3 — ANALYSING
# ══════════════════════════════════════════════════════════════════════════════
def screen_analysing():
    topbar()
    st.markdown("<br><br>", unsafe_allow_html=True)
    heading_text = "Analysing your profile..." if lang()=="en" else "प्रोफाइल का विश्लेषण हो रहा है..."
    sub_text     = "Matching your skills across 20 career paths" if lang()=="en" else "20 करियर पाथ से आपकी स्किल्स मैच हो रही हैं"
    st.markdown(
        f"<div style='text-align:center'>"
        f"<div style='font-size:3.5rem;margin-bottom:1rem'>🔍</div>"
        f"<div style='font-size:1.5rem;font-weight:800;color:#60a5fa;margin-bottom:0.5rem'>{heading_text}</div>"
        f"<div style='color:#64748b;font-size:0.95rem'>{sub_text}</div>"
        f"</div><br>",
        unsafe_allow_html=True,
    )

    bar = st.progress(0)
    steps_en = ["📖 Reading your profile…","🎯 Scoring 20 career paths…",
                "📊 Calculating skill gaps…","🗺️ Building your roadmap…"]
    steps_hi = ["📖 प्रोफाइल पढ़ रहे हैं…","🎯 20 करियर पाथ स्कोर हो रहे हैं…",
                "📊 स्किल गैप देख रहे हैं…","🗺️ रोडमैप बना रहे हैं…"]
    steps = steps_hi if lang()=="hi" else steps_en
    for i, s in enumerate(steps):
        time.sleep(0.55)
        bar.progress((i+1)*25, text=s)

    results = match_jobs(st.session_state["profile"])
    st.session_state["results"] = results
    save_metric("analyses_completed")
    go_to("results")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 4 — RESULTS
# ══════════════════════════════════════════════════════════════════════════════
def screen_results():
    results = st.session_state.get("results", [])
    if not results:
        go_to("welcome"); return

    topbar("Your Career Recommendations" if lang()=="en" else "आपकी करियर सिफारिशें")

    heading = "🌟 Your Top Career Matches" if lang()=="en" else "🌟 आपके लिए सर्वश्रेष्ठ करियर"
    st.markdown(f"<div style='font-size:1.4rem;font-weight:800;color:#f1f5f9;margin-bottom:0.3rem'>{heading}</div>",
                unsafe_allow_html=True)
    st.markdown(f"<div style='color:#64748b;font-size:0.85rem;margin-bottom:1.2rem'>"
                f"{'Based on your skills, education, and city' if lang()=='en' else 'आपकी स्किल्स, शिक्षा और शहर के आधार पर'}"
                f"</div>", unsafe_allow_html=True)

    medal = ["🥇","🥈","🥉"]
    rank_label = ["Top Match ⭐","2nd Match","3rd Match"] if lang()=="en" else ["सर्वश्रेष्ठ ⭐","दूसरा","तीसरा"]

    for idx, role in enumerate(results):
        title = role.get("title_hi", role["title"]) if lang()=="hi" else role["title"]
        desc  = role.get("description_hi", role["description"]) if lang()=="hi" else role["description"]
        local = role.get("local_note_hi", role["local_note"]) if lang()=="hi" else role["local_note"]
        pct   = role["match_pct"]

        # colour the bar: green ≥70, blue ≥50, amber <50
        bar_color = "#22c55e" if pct >= 70 else ("#3b82f6" if pct >= 50 else "#f59e0b")

        exp_label = f"{medal[idx]}  {title}  —  {pct}% Match"
        with st.expander(exp_label, expanded=(idx == 0)):

            # ── Match % visual bar ────────────────────────────────────────
            st.markdown(
                f"<div style='margin-bottom:0.9rem'>"
                f"<div style='display:flex;justify-content:space-between;margin-bottom:0.3rem'>"
                f"<span style='font-size:0.82rem;font-weight:600;color:#94a3b8'>"
                f"{'Match Score' if lang()=='en' else 'मैच स्कोर'}</span>"
                f"<span style='font-size:0.95rem;font-weight:800;color:{bar_color}'>{pct}%</span>"
                f"</div>"
                f"<div style='background:#1e293b;border-radius:999px;height:10px;width:100%'>"
                f"<div style='background:{bar_color};border-radius:999px;height:10px;"
                f"width:{pct}%;transition:width 0.6s ease'></div>"
                f"</div></div>",
                unsafe_allow_html=True,
            )

            # Top row
            c1, c2 = st.columns([2,1])
            with c1:
                st.markdown(f"<div style='color:#94a3b8;font-size:0.88rem;margin-bottom:0.5rem'>{desc}</div>",
                            unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class='stat-box'>
                  <div class='stat-val'>{role['avg_salary']}</div>
                  <div class='stat-lbl'>{'Expected Salary' if lang()=='en' else 'अपेक्षित वेतन'}</div>
                </div>""", unsafe_allow_html=True)

            # Work types
            wt_icons = {"remote":"🏠","office":"🏢","freelance":"💼",
                        "on-site":"🔧","any":"🌐"}
            wt_html = " ".join(
                f"<span style='background:#1e3a5f;border:1px solid #3b82f6;color:#93c5fd;"
                f"border-radius:999px;padding:0.2rem 0.7rem;font-size:0.78rem;margin:0.1rem'>"
                f"{wt_icons.get(w,'📌')} {w.title()}</span>"
                for w in role["work_types"]
            )
            st.markdown(f"<div style='margin-bottom:1rem'>{wt_html}</div>", unsafe_allow_html=True)

            # ── Skill Gap ──────────────────────────────────────────────────
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            have_lbl = "✅ Skills you HAVE" if lang()=="en" else "✅ आपके पास हैं"
            need_lbl = "📌 Skills to LEARN" if lang()=="en" else "📌 ये सीखनी होंगी"

            ga, gb = st.columns(2)
            with ga:
                st.markdown(f"<div style='font-size:0.82rem;font-weight:700;color:#4ade80;margin-bottom:0.4rem'>{have_lbl}</div>",
                            unsafe_allow_html=True)
                if role["skills_have"]:
                    st.markdown(" ".join(f"<span class='pill-have'>{s}</span>" for s in role["skills_have"]),
                                unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color:#475569;font-size:0.82rem'>None yet — start learning!</span>",
                                unsafe_allow_html=True)
            with gb:
                st.markdown(f"<div style='font-size:0.82rem;font-weight:700;color:#fbbf24;margin-bottom:0.4rem'>{need_lbl}</div>",
                            unsafe_allow_html=True)
                if role["skills_need"]:
                    st.markdown(" ".join(f"<span class='pill-need'>{s}</span>" for s in role["skills_need"]),
                                unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color:#4ade80;font-size:0.88rem'>🎉 You have ALL required skills!</span>",
                                unsafe_allow_html=True)

            # ── Local note ────────────────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            city_lbl = "📍 In Your City" if lang()=="en" else "📍 आपके शहर में"
            st.markdown(
                f"<div class='card-green'><b style='font-size:0.82rem;letter-spacing:0.5px'>{city_lbl}</b>"
                f"<div style='margin-top:0.35rem;font-size:0.9rem'>{local}</div></div>",
                unsafe_allow_html=True)

            # ── Next Action ───────────────────────────────────────────────
            na_lbl = "⚡ Your Next Action" if lang()=="en" else "⚡ आपका अगला कदम"
            st.markdown(
                f"<div class='card-amber'><b style='font-size:0.82rem'>{na_lbl}</b>"
                f"<div style='margin-top:0.35rem;font-size:0.92rem'>{role['next_action']}</div></div>",
                unsafe_allow_html=True)

            # ── Free Resources ────────────────────────────────────────────
            res_lbl = "📚 Free Resources to Get Started" if lang()=="en" else "📚 मुफ्त संसाधन"
            st.markdown(f"<div class='sec-label'>{res_lbl}</div>", unsafe_allow_html=True)
            for res in role["resources"]:
                st.markdown(
                    f"<a href='{res['url']}' target='_blank' class='res-link'>"
                    f"<span class='res-icon'>🔗</span>{res['name']}</a>",
                    unsafe_allow_html=True)

            st.markdown(
                f"<div style='color:#334155;font-size:0.75rem;margin-top:0.5rem'>"
                f"{'* Salary is indicative for India. Actual may vary.' if lang()=='en' else '* वेतन भारत के लिए सांकेतिक है।'}</div>",
                unsafe_allow_html=True)

    # ── Compare button ────────────────────────────────────────────────────
    if len(results) >= 2:
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        cmp_lbl = "⚖️  Compare Top 2 Roles Side-by-Side" if lang()=="en" else "⚖️  टॉप 2 रोल की तुलना करें"
        if st.button(cmp_lbl, use_container_width=True):
            go_to("compare")

    # ── Action buttons ────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        lbl = "📄  Build My Resume  →" if lang()=="en" else "📄  रिज्यूमे बनाएं  →"
        if st.button(lbl, type="primary", use_container_width=True):
            go_to("resume")
    with b2:
        lbl2 = "🔄  Start Over" if lang()=="en" else "🔄  फिर से शुरू करें"
        if st.button(lbl2, use_container_width=True):
            for k, v in DEFAULTS.items(): st.session_state[k] = v
            go_to("welcome")

    st.markdown("""<div class='footer-bar'>AI Career Guide &nbsp;•&nbsp; Free Forever</div>""",
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 5 — RESUME BUILDER
# ══════════════════════════════════════════════════════════════════════════════
def screen_resume():
    profile = st.session_state.get("profile", {})
    results = st.session_state.get("results", [])
    topbar("Resume Builder" if lang()=="en" else "रिज्यूमे बनाएं")

    h = "📄 Build Your Resume" if lang()=="en" else "📄 अपना रिज्यूमे बनाएं"
    sub = "Fill in your details below. We'll create a clean PDF resume for you." if lang()=="en" \
          else "नीचे अपनी जानकारी भरें। हम आपके लिए PDF रिज्यूमे बनाएंगे।"
    st.markdown(f"<div style='font-size:1.4rem;font-weight:800;color:#f1f5f9;margin-bottom:0.25rem'>{h}</div>",
                unsafe_allow_html=True)
    st.markdown(f"<div style='color:#64748b;font-size:0.88rem;margin-bottom:1.3rem'>{sub}</div>",
                unsafe_allow_html=True)

    # ── Profile summary card ───────────────────────────────────────────────
    if profile:
        p_lbl = "Your Profile Summary" if lang()=="en" else "आपकी प्रोफाइल"
        st.markdown(f"<div class='sec-label'>{p_lbl}</div>", unsafe_allow_html=True)
        items = [
            ("🎓", "Education" if lang()=="en" else "शिक्षा",       profile.get("education","")),
            ("🛠️","Skills" if lang()=="en" else "स्किल्स",           profile.get("skills","")),
            ("📍","City" if lang()=="en" else "शहर",                 profile.get("city","")),
            ("💼","Experience" if lang()=="en" else "अनुभव",         profile.get("experience","")),
            ("🏢","Work Type" if lang()=="en" else "काम का तरीका",   profile.get("work_type","")),
            ("🎯","Best Role" if lang()=="en" else "सर्वश्रेष्ठ रोल", results[0]["title"] if results else ""),
        ]
        rows = ""
        for icon, lbl, val in items:
            if val:
                rows += (f"<div style='display:flex;gap:0.6rem;padding:0.5rem 0;"
                         f"border-bottom:1px solid #1e293b'>"
                         f"<span style='font-size:1rem'>{icon}</span>"
                         f"<span style='color:#64748b;font-size:0.85rem;width:90px;flex-shrink:0'>{lbl}</span>"
                         f"<span style='color:#e2e8f0;font-size:0.88rem;font-weight:500'>{val}</span>"
                         f"</div>")
        st.markdown(f"<div class='card'>{rows}</div>", unsafe_allow_html=True)

    # ── Form ──────────────────────────────────────────────────────────────
    f_lbl = "Personal Details" if lang()=="en" else "व्यक्तिगत जानकारी"
    st.markdown(f"<div class='sec-label'>{f_lbl}</div>", unsafe_allow_html=True)

    with st.form("resume_form"):
        name  = st.text_input(
            "Full Name  *" if lang()=="en" else "पूरा नाम  *",
            placeholder="Rahul Kumar" if lang()=="en" else "राहुल कुमार")
        c1, c2 = st.columns(2)
        with c1:
            phone = st.text_input(
                "Phone  *" if lang()=="en" else "फोन  *",
                placeholder="9876543210")
        with c2:
            email = st.text_input(
                "Email  *" if lang()=="en" else "ईमेल  *",
                placeholder="rahul@gmail.com")
        obj = st.text_area(
            ("Professional Objective (optional — auto-generated if blank)"
             if lang()=="en" else
             "प्रोफेशनल उद्देश्य (वैकल्पिक — खाली छोड़ें तो हम बनाएंगे)"),
            height=90,
            placeholder=("Motivated graduate seeking a career in technology..."
                         if lang()=="en" else
                         "एक प्रेरित स्नातक जो टेक्नोलॉजी में करियर की तलाश में है..."))
        gen_lbl = "⬇️  Generate & Download PDF Resume" if lang()=="en" else "⬇️  PDF रिज्यूमे बनाएं और डाउनलोड करें"
        submitted = st.form_submit_button(gen_lbl, type="primary", use_container_width=True)

    if submitted:
        # ── Validation ────────────────────────────────────────────────────
        import re
        errors = []
        name_clean  = name.strip()
        email_clean = email.strip()
        phone_clean = re.sub(r'\s+', '', phone.strip())  # strip spaces

        if not name_clean:
            errors.append("Please enter your full name." if lang()=="en"
                          else "कृपया अपना पूरा नाम दर्ज करें।")

        # Phone: optional but if entered must be 10-digit Indian mobile
        # Allow optional +91 or 0 prefix
        if phone_clean:
            phone_digits = re.sub(r'^(\+91|91|0)', '', phone_clean)
            if not re.fullmatch(r'[6-9]\d{9}', phone_digits):
                errors.append(
                    "Enter a valid 10-digit Indian mobile number (e.g. 9876543210)"
                    if lang()=="en" else
                    "सही 10-अंकों का मोबाइल नंबर दर्ज करें (जैसे: 9876543210)"
                )

        # Email: required, proper format
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$')
        if not email_clean:
            errors.append("Please enter your email address." if lang()=="en"
                          else "कृपया अपना ईमेल पता दर्ज करें।")
        elif not email_pattern.match(email_clean):
            errors.append(
                "Invalid email format. Use format: name@example.com"
                if lang()=="en" else
                "ईमेल गलत है। सही फॉर्मेट: name@example.com"
            )

        if errors:
            for err in errors:
                st.error(err)
        else:
            skills_raw  = profile.get("skills","")
            skills_list = [s.strip() for s in skills_raw.replace(","," ").split() if s.strip()]
            resume_data = {
                "name": name_clean, "phone": phone_clean, "email": email_clean,
                "city": profile.get("city",""), "education": profile.get("education",""),
                "skills": skills_list, "experience_level": profile.get("experience","Fresher"),
                "work_type": profile.get("work_type",""), "interests": profile.get("interests",""),
                "top_role": results[0] if results else {}, "objective": obj.strip(),
            }
            if REPORTLAB_AVAILABLE:
                with st.spinner("Generating PDF…" if lang()=="en" else "PDF बन रहा है…"):
                    pdf_bytes = generate_resume_pdf(resume_data)
                st.success("✅ Resume ready! Click below to download." if lang()=="en"
                           else "✅ रिज्यूमे तैयार है! नीचे से डाउनलोड करें।")
                st.download_button(
                    label="📥  Download PDF Resume" if lang()=="en" else "📥  PDF रिज्यूमे डाउनलोड करें",
                    data=pdf_bytes,
                    file_name=f"resume_{name.replace(' ','_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
                save_metric("resumes_generated")
            else:
                st.error("Run:  pip install reportlab")

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("← Back to Results" if lang()=="en" else "← परिणामों पर वापस", use_container_width=True):
            go_to("results")
    with b2:
        lbl = "💬  Leave Feedback" if lang()=="en" else "💬  फीडबैक दें"
        if st.button(lbl, use_container_width=True):
            go_to("feedback")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 6 — FEEDBACK
# ══════════════════════════════════════════════════════════════════════════════
def screen_feedback():
    topbar("Feedback" if lang()=="en" else "फीडबैक")

    if st.session_state.get("feedback_done"):
        st.markdown("""
        <div style='text-align:center;padding:2.5rem 1rem'>
          <div style='font-size:3rem;margin-bottom:0.7rem'>🙏</div>
          <div style='font-size:1.3rem;font-weight:700;color:#4ade80;margin-bottom:0.5rem'>
            Thank you for your feedback!</div>
          <div style='color:#64748b;font-size:0.9rem'>
            It helps us improve for other students in Tier-2/3 cities.</div>
        </div>""" if lang()=="en" else """
        <div style='text-align:center;padding:2.5rem 1rem'>
          <div style='font-size:3rem;margin-bottom:0.7rem'>🙏</div>
          <div style='font-size:1.3rem;font-weight:700;color:#4ade80;margin-bottom:0.5rem'>
            आपके फीडबैक के लिए धन्यवाद!</div>
          <div style='color:#64748b;font-size:0.9rem'>
            यह हमें टियर-2/3 शहरों के छात्रों के लिए बेहतर बनाने में मदद करता है।</div>
        </div>""", unsafe_allow_html=True)

        lbl = "🔄  Start Over — Try Again" if lang()=="en" else "🔄  फिर से शुरू करें"
        if st.button(lbl, type="primary", use_container_width=True):
            for k, v in DEFAULTS.items(): st.session_state[k] = v
            go_to("welcome")
        return

    h = "💬 How helpful was this?" if lang()=="en" else "💬 यह कितना उपयोगी था?"
    sub = ("Rate your experience from 1 (not helpful) to 5 (extremely helpful)"
           if lang()=="en" else
           "1 (बिल्कुल नहीं) से 5 (बहुत उपयोगी) तक रेट करें")
    st.markdown(f"<div style='font-size:1.4rem;font-weight:800;color:#f1f5f9;margin-bottom:0.3rem'>{h}</div>",
                unsafe_allow_html=True)
    st.markdown(f"<div style='color:#64748b;font-size:0.88rem;margin-bottom:1.3rem'>{sub}</div>",
                unsafe_allow_html=True)

    # Star display
    star_labels = {1:"😞 Not helpful",2:"😐 A little helpful",3:"🙂 Okay",
                   4:"😊 Helpful!",5:"🤩 Very helpful!"}
    star_labels_hi = {1:"😞 बिल्कुल नहीं",2:"😐 थोड़ा",3:"🙂 ठीक है",
                      4:"😊 उपयोगी!",5:"🤩 बहुत उपयोगी!"}

    sl = star_labels_hi if lang()=="hi" else star_labels
    rating = st.select_slider(
        "Rating" if lang()=="en" else "रेटिंग",
        options=[1,2,3,4,5],
        value=4,
        format_func=lambda x: sl[x],
    )

    # Visual stars
    stars_html = "".join(
        f"<span style='font-size:2rem;color:{'#fbbf24' if i<=rating else '#1e293b'}'>"
        f"{'★' if i<=rating else '☆'}</span>" for i in range(1,6)
    )
    st.markdown(f"<div style='text-align:center;margin:0.3rem 0 1rem'>{stars_html}</div>",
                unsafe_allow_html=True)

    comment_lbl = "Any suggestions? (optional)" if lang()=="en" else "कोई सुझाव? (वैकल्पिक)"
    comment = st.text_area(
        comment_lbl,
        placeholder=("What worked well? What can be improved?"
                     if lang()=="en" else
                     "क्या अच्छा लगा? क्या बेहतर हो सकता है?"),
        height=100,
    )

    sub_lbl = "✅  Submit Feedback" if lang()=="en" else "✅  फीडबैक जमा करें"
    if st.button(sub_lbl, type="primary", use_container_width=True):
        save_feedback(rating, comment)
        save_metric("feedbacks_submitted")
        st.session_state["feedback_done"] = True
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Resume" if lang()=="en" else "← रिज्यूमे पर वापस", use_container_width=True):
        go_to("resume")


# ══════════════════════════════════════════════════════════════════════════════
# SCREEN 7 — COMPARE (Top 2 roles side by side)
# ══════════════════════════════════════════════════════════════════════════════
def screen_compare():
    results = st.session_state.get("results", [])
    if len(results) < 2:
        go_to("results"); return

    topbar("Role Comparison" if lang()=="en" else "रोल तुलना")

    h = "⚖️ Side-by-Side Comparison" if lang()=="en" else "⚖️ दोनों रोल की तुलना"
    st.markdown(f"<div style='font-size:1.4rem;font-weight:800;color:#f1f5f9;margin-bottom:1.2rem'>{h}</div>",
                unsafe_allow_html=True)

    r1, r2 = results[0], results[1]
    t1 = r1.get("title_hi", r1["title"]) if lang()=="hi" else r1["title"]
    t2 = r2.get("title_hi", r2["title"]) if lang()=="hi" else r2["title"]

    # ── colour bars ───────────────────────────────────────────────────────
    def bar_col(p): return "#22c55e" if p >= 70 else ("#3b82f6" if p >= 50 else "#f59e0b")

    def cmp_bar(pct):
        c = bar_col(pct)
        return (f"<div style='background:#0f172a;border-radius:999px;height:8px;margin-top:4px'>"
                f"<div style='background:{c};border-radius:999px;height:8px;width:{pct}%'></div></div>")

    # ── Column headers ────────────────────────────────────────────────────
    hc1, hc2 = st.columns(2)
    with hc1:
        st.markdown(
            f"<div style='background:#1e3a5f;border:1px solid #3b82f6;border-radius:12px;"
            f"padding:1rem;text-align:center'>"
            f"<div style='font-size:1.5rem'>🥇</div>"
            f"<div style='font-weight:800;font-size:1rem;color:#f1f5f9;margin:0.3rem 0'>{t1}</div>"
            f"<div style='font-size:1.4rem;font-weight:800;color:{bar_col(r1['match_pct'])}'>{r1['match_pct']}%</div>"
            f"{cmp_bar(r1['match_pct'])}</div>",
            unsafe_allow_html=True)
    with hc2:
        st.markdown(
            f"<div style='background:#1a1a3e;border:1px solid #6366f1;border-radius:12px;"
            f"padding:1rem;text-align:center'>"
            f"<div style='font-size:1.5rem'>🥈</div>"
            f"<div style='font-weight:800;font-size:1rem;color:#f1f5f9;margin:0.3rem 0'>{t2}</div>"
            f"<div style='font-size:1.4rem;font-weight:800;color:{bar_col(r2['match_pct'])}'>{r2['match_pct']}%</div>"
            f"{cmp_bar(r2['match_pct'])}</div>",
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Comparison rows ───────────────────────────────────────────────────
    def row(label, val1, val2, highlight=False):
        bg = "background:#1e293b;" if highlight else "background:#0f172a;"
        return (
            f"<div style='{bg}border-radius:10px;padding:0.7rem 0.9rem;"
            f"margin-bottom:0.4rem;display:grid;grid-template-columns:1fr 1fr;gap:0.5rem'>"
            f"<div><div style='font-size:0.7rem;color:#475569;font-weight:600;letter-spacing:0.5px;margin-bottom:0.2rem'>{label} (🥇)</div>"
            f"<div style='color:#e2e8f0;font-size:0.88rem;font-weight:500'>{val1}</div></div>"
            f"<div><div style='font-size:0.7rem;color:#475569;font-weight:600;letter-spacing:0.5px;margin-bottom:0.2rem'>{label} (🥈)</div>"
            f"<div style='color:#e2e8f0;font-size:0.88rem;font-weight:500'>{val2}</div></div>"
            f"</div>"
        )

    salary_lbl  = "💰 Salary"      if lang()=="en" else "💰 वेतन"
    work_lbl    = "🏢 Work Mode"   if lang()=="en" else "🏢 काम का तरीका"
    edu_lbl     = "🎓 Education"   if lang()=="en" else "🎓 शिक्षा"
    have_lbl    = "✅ Skills You Have" if lang()=="en" else "✅ आपके पास हैं"
    need_lbl    = "📌 Skills to Learn" if lang()=="en" else "📌 सीखनी होंगी"
    action_lbl  = "⚡ Next Action" if lang()=="en" else "⚡ अगला कदम"

    table_html = (
        row(salary_lbl,  r1["avg_salary"], r2["avg_salary"], highlight=True) +
        row(work_lbl,    ", ".join(r1["work_types"]).title(), ", ".join(r2["work_types"]).title()) +
        row(edu_lbl,     ", ".join(r1["education"][:3]),      ", ".join(r2["education"][:3]),     highlight=True) +
        row(have_lbl,
            (", ".join(r1["skills_have"]) or "—"),
            (", ".join(r2["skills_have"]) or "—")) +
        row(need_lbl,
            (", ".join(r1["skills_need"]) or "✅ None"),
            (", ".join(r2["skills_need"]) or "✅ None"),   highlight=True) +
        row(action_lbl,  r1["next_action"][:80]+"…",          r2["next_action"][:80]+"…")
    )
    st.markdown(table_html, unsafe_allow_html=True)

    # ── Verdict ───────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if r1["match_pct"] > r2["match_pct"]:
        winner, winner_pct = t1, r1["match_pct"]
    else:
        winner, winner_pct = t2, r2["match_pct"]

    verdict_txt = (f"Based on your profile, <b>{winner}</b> is the stronger fit ({winner_pct}% match)."
                   if lang()=="en" else
                   f"आपकी प्रोफाइल के अनुसार, <b>{winner}</b> बेहतर विकल्प है ({winner_pct}% मैच)।")
    st.markdown(
        f"<div class='card-green' style='text-align:center;font-size:0.95rem'>"
        f"🏆 {verdict_txt}</div>",
        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    b1, b2 = st.columns(2)
    with b1:
        if st.button("← Back to Results" if lang()=="en" else "← परिणामों पर वापस",
                     use_container_width=True):
            go_to("results")
    with b2:
        lbl = "📄  Build Resume  →" if lang()=="en" else "📄  रिज्यूमे बनाएं  →"
        if st.button(lbl, type="primary", use_container_width=True):
            go_to("resume")


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD (Sidebar)
# ══════════════════════════════════════════════════════════════════════════════
def sidebar_dashboard():
    import csv as _csv
    log_path = ROOT / "data" / "feedback_log.csv"

    with st.sidebar:
        st.markdown("## 📊 Admin Dashboard")
        st.markdown("---")

        # Session metrics
        m = st.session_state.get("metrics", {})
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Sessions", m.get("sessions_started", 0))
            st.metric("Analyses", m.get("analyses_completed", 0))
        with col_b:
            st.metric("Resumes", m.get("resumes_generated", 0))
            st.metric("Feedbacks", m.get("feedbacks_submitted", 0))

        # Feedback log stats
        if log_path.exists():
            st.markdown("---")
            st.markdown("**📝 All-time Feedback**")
            rows = []
            with open(log_path, "r", encoding="utf-8") as f:
                reader = _csv.DictReader(f)
                for r in reader:
                    rows.append(r)

            if rows:
                ratings = [int(r["rating"]) for r in rows if r.get("rating","").isdigit()]
                avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0
                st.metric("Total Responses", len(rows))
                st.metric("Avg Rating", f"{avg_rating} / 5 ⭐")

                # Top cities
                cities = [r["city"] for r in rows if r.get("city")]
                if cities:
                    from collections import Counter
                    top_cities = Counter(cities).most_common(3)
                    st.markdown("**📍 Top Cities**")
                    for city, cnt in top_cities:
                        st.markdown(f"- {city}: {cnt} users")

                # Top roles recommended
                roles_rec = [r["top_role"] for r in rows if r.get("top_role")]
                if roles_rec:
                    top_roles = Counter(roles_rec).most_common(3)
                    st.markdown("**🎯 Top Recommended Roles**")
                    for role, cnt in top_roles:
                        st.markdown(f"- {role}: {cnt}×")
            else:
                st.caption("No feedback yet.")
        else:
            st.caption("No feedback data yet. Complete the flow to generate data.")

        st.markdown("---")
        st.caption("Data is session-only. Feedback persists in feedback_log.csv")


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
SCREENS = {
    "welcome":   screen_welcome,
    "chat":      screen_chat,
    "analysing": screen_analysing,
    "results":   screen_results,
    "compare":   screen_compare,
    "resume":    screen_resume,
    "feedback":  screen_feedback,
}

# Add "compare" to DEFAULTS so session state is always valid
if "screen" not in st.session_state:
    st.session_state["screen"] = "welcome"

sidebar_dashboard()
SCREENS.get(st.session_state["screen"], screen_welcome)()
