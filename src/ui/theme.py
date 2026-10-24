from __future__ import annotations

import streamlit as st


def inject_theme() -> None:
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    :root { --qp-bg:#0b0e13; --qp-surface:#131821; --qp-surface-2:#19202b; --qp-border:#2a3341; --qp-border-strong:#3b4658; --qp-violet:#a78bfa; --qp-violet-strong:#8b5cf6; --qp-cyan:#5eead4; --qp-amber:#fbbf24; --qp-danger:#fb7185; --qp-text:#f8fafc; --qp-muted:#a7b0bf; --qp-focus:#c4b5fd; }
    html, body, [class*="css"] { font-family:'DM Sans', sans-serif; }
    .stApp { background:radial-gradient(circle at 12% 0%, rgba(139,92,246,.13), transparent 34%), var(--qp-bg); color:var(--qp-text); }
    [data-testid="stAppViewContainer"] > .main { background:transparent; }
    [data-testid="stHeader"] { background:rgba(11,14,19,.78); }
    [data-testid="stSidebar"] { background:#10151d; border-right:1px solid var(--qp-border); }
    [data-testid="stSidebar"] .block-container { padding:1.6rem 1rem 2rem; }
    [data-testid="stSidebarNav"] { display:none; }
    .block-container { max-width:1440px; padding:2.3rem 3.25rem 4rem; }
    h1,h2,h3,h4 { font-family:'Space Grotesk', sans-serif; letter-spacing:-.035em; color:var(--qp-text); }
    h1 { font-size:clamp(2rem, 4vw, 3.35rem); line-height:1.05; margin-bottom:.55rem; }
    h2 { font-size:clamp(1.45rem, 2.2vw, 2.1rem); }
    h3 { font-size:1.28rem; }
    p, label, [data-testid="stCaptionContainer"] { color:var(--qp-muted); }
    [data-testid="stMarkdownContainer"] a { color:var(--qp-focus); }
    .qp-brand { display:flex; align-items:center; gap:.75rem; padding:.25rem .35rem 1.5rem; }
    .qp-brand-name { font-family:'Space Grotesk', sans-serif; font-size:1.15rem; font-weight:700; color:var(--qp-text); }
    .qp-brand-subtitle { color:var(--qp-muted); font-size:.75rem; margin-top:.1rem; }
    .qp-mark { width:34px; height:34px; border-radius:10px; background:linear-gradient(145deg, var(--qp-violet), var(--qp-violet-strong)); box-shadow:0 0 26px rgba(139,92,246,.34); position:relative; flex:0 0 auto; }
    .qp-mark:before { content:''; position:absolute; width:12px; height:12px; left:11px; top:7px; border:2px solid white; border-radius:50%; }
    .qp-mark:after { content:''; position:absolute; width:7px; height:2px; left:14px; top:23px; background:white; border-radius:2px; transform:rotate(-35deg); }
    .qp-card { background:linear-gradient(145deg, rgba(25,32,43,.92), rgba(19,24,33,.92)); border:1px solid var(--qp-border); border-radius:18px; padding:1.15rem 1.2rem; box-shadow:0 16px 42px rgba(0,0,0,.18); }
    .qp-card-compact { min-height:112px; }
    .qp-hero { background:linear-gradient(135deg, rgba(139,92,246,.19), rgba(19,24,33,.78) 58%); border:1px solid rgba(167,139,250,.35); border-radius:24px; padding:2rem 2.1rem; margin-bottom:1.4rem; }
    .qp-eyebrow { color:var(--qp-focus); text-transform:uppercase; letter-spacing:.13em; font-size:.72rem; font-weight:700; margin-bottom:.65rem; }
    .qp-muted { color:var(--qp-muted); font-size:.92rem; line-height:1.55; }
    .qp-kicker { color:var(--qp-muted); text-transform:uppercase; letter-spacing:.09em; font-size:.72rem; font-weight:700; }
    .qp-value { font-family:'Space Grotesk', sans-serif; font-size:1.8rem; font-weight:700; color:var(--qp-text); margin-top:.35rem; }
    .qp-pill { display:inline-flex; align-items:center; min-height:26px; padding:.22rem .62rem; margin:.14rem .22rem .14rem 0; border-radius:999px; border:1px solid var(--qp-border-strong); color:var(--qp-muted); font-size:.78rem; }
    .qp-status { display:inline-flex; align-items:center; gap:.42rem; min-height:28px; padding:.25rem .7rem; border-radius:999px; font-size:.78rem; font-weight:700; border:1px solid; }
    .qp-status:before { content:''; width:7px; height:7px; border-radius:50%; background:currentColor; }
    .qp-status--success { color:var(--qp-cyan); background:rgba(94,234,212,.08); border-color:rgba(94,234,212,.28); }
    .qp-status--warning { color:var(--qp-amber); background:rgba(251,191,36,.08); border-color:rgba(251,191,36,.28); }
    .qp-status--danger { color:var(--qp-danger); background:rgba(251,113,133,.08); border-color:rgba(251,113,133,.28); }
    .qp-status--neutral { color:var(--qp-muted); background:rgba(167,176,191,.08); border-color:var(--qp-border); }
    .qp-section-title { display:flex; align-items:end; justify-content:space-between; gap:1rem; margin:1.6rem 0 .75rem; }
    .qp-section-title h2, .qp-section-title h3 { margin:0; }
    .qp-callout { border:1px solid var(--qp-border); background:rgba(19,24,33,.72); border-radius:14px; padding:.95rem 1rem; }
    .qp-callout--success { border-color:rgba(94,234,212,.28); background:rgba(94,234,212,.06); }
    .qp-callout--warning { border-color:rgba(251,191,36,.28); background:rgba(251,191,36,.06); }
    .qp-callout--danger { border-color:rgba(251,113,133,.28); background:rgba(251,113,133,.06); }
    .qp-timeline { border-left:2px solid var(--qp-border-strong); margin:.2rem 0 .4rem .55rem; padding-left:1.15rem; }
    .qp-timeline div { position:relative; margin:.85rem 0; color:var(--qp-text); }
    .qp-dot { position:absolute; left:-1.5rem; top:.35rem; width:9px; height:9px; border-radius:50%; background:var(--qp-cyan); box-shadow:0 0 0 4px rgba(94,234,212,.1); }
    .qp-step-label { font-weight:600; }
    .qp-step-detail { color:var(--qp-muted); font-size:.85rem; margin-top:.15rem; }
    .qp-help { color:var(--qp-muted); font-size:.85rem; line-height:1.5; }
    .qp-empty { text-align:center; border:1px dashed var(--qp-border-strong); border-radius:18px; padding:2rem 1rem; color:var(--qp-muted); }
    .stButton button, .stDownloadButton button, .stFormSubmitButton button { min-height:2.7rem; border-radius:11px; border:1px solid var(--qp-border-strong); font-weight:600; transition:background .18s ease, border-color .18s ease, transform .18s ease; }
    .stButton button:hover, .stDownloadButton button:hover, .stFormSubmitButton button:hover { border-color:var(--qp-violet); transform:translateY(-1px); }
    .stButton button:focus-visible, .stDownloadButton button:focus-visible, .stFormSubmitButton button:focus-visible, input:focus-visible, textarea:focus-visible { outline:3px solid var(--qp-focus) !important; outline-offset:2px !important; }
    [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea { background:var(--qp-surface); color:var(--qp-text); border:1px solid var(--qp-border-strong); border-radius:12px; }
    [data-testid="stTextArea"] textarea { line-height:1.55; }
    [data-testid="stMetric"] { background:var(--qp-surface); border:1px solid var(--qp-border); border-radius:15px; padding:1rem; }
    [data-testid="stMetricLabel"] { color:var(--qp-muted); }
    [data-testid="stMetricValue"] { color:var(--qp-text); font-family:'Space Grotesk', sans-serif; }
    [data-testid="stExpander"] { border:1px solid var(--qp-border); border-radius:14px; background:rgba(19,24,33,.55); overflow:hidden; }
    [data-testid="stExpander"] summary { padding:.9rem 1rem; }
    [data-testid="stDataFrame"] { border:1px solid var(--qp-border); border-radius:14px; overflow:hidden; }
    [data-testid="stAlert"] { border-radius:13px; }
    [data-testid="stRadio"] label { color:var(--qp-muted); }
    [data-testid="stRadio"] label:hover { color:var(--qp-text); }
    hr { border-color:var(--qp-border); margin:1.5rem 0; }
    @media (max-width:900px) { .block-container { padding:1.5rem 1rem 3rem; } .qp-hero { padding:1.4rem; border-radius:18px; } }
    @media (prefers-reduced-motion:reduce) { *, *:before, *:after { animation-duration:.01ms !important; animation-iteration-count:1 !important; scroll-behavior:auto !important; transition-duration:.01ms !important; } }
    </style>""", unsafe_allow_html=True)
