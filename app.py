import streamlit as st
import pandas as pd
import joblib
from datetime import date

st.set_page_config(
    page_title="Steam Game Type Classifier",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
/* Apple system fonts — no import needed */

:root {
  --cream:      #F5F5F7;
  --cream-2:    #E8E8ED;
  --cream-3:    #D2D2D7;
  --card:       #FFFFFF;
  --border:     rgba(0,0,0,0.08);
  --border-2:   rgba(0,0,0,0.12);
  --ink:        #1D1D1F;
  --ink-2:      #3A3A3C;
  --gray:       #6E6E73;
  --gray-2:     #86868B;
  --gray-3:     #AEAEB2;
  --gold:       #1D3A8A;
  --gold-lt:    #2563EB;
  --gold-pale:  rgba(37,99,235,0.08);
  --radius:     20px;
  --radius-sm:  12px;
  --shadow:     0 2px 8px rgba(0,0,0,0.05), 0 12px 40px rgba(0,0,0,0.07);
  --shadow-lg:  0 8px 24px rgba(0,0,0,0.09), 0 32px 80px rgba(0,0,0,0.11);
  --fd:         -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Helvetica, Arial, sans-serif;
  --fu:         -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
  --blue:       #2563EB;
  --blue-dk:    #1D4ED8;
  --blue-lt:    #3B82F6;
  --blue-pale:  rgba(37,99,235,0.08);
  --blue-ring:  rgba(37,99,235,0.18);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html { color-scheme: light !important; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background: var(--cream) !important;
  font-family: var(--fu) !important;
  -webkit-font-smoothing: antialiased;
  color: var(--ink) !important;
}

/* Hide all Streamlit chrome */
#MainMenu, footer, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stHeader"],
header[data-testid="stHeader"], .stApp > header {
  display: none !important; height: 0 !important;
  min-height: 0 !important; visibility: hidden !important;
}
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stAppViewContainer"] > .main {
  padding: 0 !important; margin-top: 0 !important;
  background: var(--cream) !important;
}
.main .block-container {
  padding: 0 !important; max-width: 100% !important;
  padding-top: 0 !important; margin-top: 0 !important;
}
.element-container, .stMarkdown { margin-bottom: 0 !important; }
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] { padding: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 16px !important; align-items: stretch !important; }

/* Force inputs light */
input, textarea, select,
input[type="text"], input[type="number"],
[data-baseweb="input"] input,
[data-baseweb="base-input"] input {
  background: var(--card) !important;
  background-color: var(--card) !important;
  color: var(--ink) !important;
  caret-color: var(--gold-lt) !important;
  -webkit-text-fill-color: var(--ink) !important;
}
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="input"] > div {
  background: var(--card) !important;
  background-color: var(--card) !important;
}
[data-baseweb="select"] > div,
[data-baseweb="select"] > div > div {
  background: var(--card) !important;
  background-color: var(--card) !important;
  color: var(--ink) !important;
}

/* Multiselect tags */
[data-baseweb="tag"] {
  background: var(--blue-pale) !important;
  border: 1px solid rgba(37,99,235,0.2) !important;
  color: var(--blue-dk) !important;
  font-family: var(--fu) !important;
  font-weight: 500 !important;
}
[data-baseweb="tag"] span { color: var(--blue-dk) !important; }

@keyframes fadeUp { from { opacity:0; transform:translateY(28px);} to { opacity:1; transform:translateY(0);} }
@keyframes cardFloat { 0% {transform:translateY(0) rotate(0.3deg);} 50% {transform:translateY(-14px) rotate(-0.4deg);} 100% {transform:translateY(0) rotate(0.3deg);} }
@keyframes shimmer { 0%{background-position:0% 50%;} 50%{background-position:100% 50%;} 100%{background-position:0% 50%;} }
@keyframes orbDrift { 0%{transform:translate(0,0) scale(1);} 100%{transform:translate(22px,16px) scale(1.07);} }
@keyframes pulseDot { 0%,100%{box-shadow:0 0 0 0 rgba(37,99,235,0.5);} 50%{box-shadow:0 0 0 6px rgba(37,99,235,0);} }
@keyframes barGrow { from { width:0% !important; } }
@keyframes resultReveal { from{opacity:0;transform:translateY(36px) scale(0.97);} to{opacity:1;transform:translateY(0) scale(1);} }
@keyframes tagIn { from{opacity:0;transform:translateX(-12px);} to{opacity:1;transform:translateX(0);} }
@keyframes stepIn { from{opacity:0;transform:translateX(-8px);} to{opacity:1;transform:translateX(0);} }

/* NAVIGATION */
.nav {
  position: fixed !important;
  top: 0 !important; left: 0 !important; right: 0 !important;
  width: 100% !important;
  z-index: 99999;
  height: 72px;
  background: rgba(245,245,247,0.88);
  backdrop-filter: saturate(200%) blur(28px);
  -webkit-backdrop-filter: saturate(200%) blur(28px);
  border-bottom: 1px solid rgba(0,0,0,0.09);
  box-shadow: 0 1px 12px rgba(0,0,0,0.06);
  display: flex; align-items: center; padding: 0 48px;
}
.nav-inner { max-width: 1200px; width: 100%; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; }
.nav-brand { display: flex; align-items: center; gap: 12px; text-decoration: none !important; border: none !important; outline: none !important; transition: opacity 0.15s; }
.nav-brand, .nav-brand:link, .nav-brand:visited, .nav-brand:hover, .nav-brand:active, .nav-brand:focus { text-decoration: none !important; border-bottom: none !important; box-shadow: none !important; color: inherit !important; -webkit-text-fill-color: inherit !important; }
.nav-brand:hover { opacity: 0.8; }
.nav-logo-box {
  width: 38px; height: 38px; border-radius: 10px;
  background: linear-gradient(135deg, var(--ink) 0%, #3B3B3B 100%);
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.22); flex-shrink: 0;
}
.sc-mono { font-family:-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif; font-size:17px; font-weight:800; font-style:normal; background:linear-gradient(135deg,#93C5FD 0%,#60A5FA 50%,#3B82F6 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; line-height:1; user-select:none; letter-spacing:-0.02em; }
.nav-brand-name { font-family: var(--fd); font-size: 17px; font-weight: 700; color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important; letter-spacing: -0.01em; text-decoration: none !important; }
.nav-links { display:flex; align-items:center; gap: 2px; }
.nav-links a { font-family: var(--fu); font-size: 14px; font-weight: 450; color: var(--gray); text-decoration: none; padding: 7px 15px; border-radius: 9px; transition: color 0.15s ease, background 0.15s ease; letter-spacing: -0.01em; }
.nav-links a:hover { color: var(--ink); background: var(--cream-2); }
.nav-btn {
  font-family: var(--fu) !important;
  background: linear-gradient(135deg, var(--blue) 0%, var(--blue-dk) 100%) !important;
  color: #fff !important; border-radius: 10px !important;
  padding: 10px 22px !important; font-size: 13.5px !important; font-weight: 600 !important;
  box-shadow: 0 2px 8px rgba(37,99,235,0.3), 0 0 0 1px rgba(37,99,235,0.15) !important;
  transition: transform 0.18s ease, box-shadow 0.18s ease !important;
  text-decoration: none !important; white-space: nowrap;
  letter-spacing: -0.01em !important;
}
.nav-btn:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(37,99,235,0.4), 0 0 0 1px rgba(37,99,235,0.2) !important;
  background: linear-gradient(135deg, var(--blue-lt) 0%, var(--blue) 100%) !important;
}

/* HERO */
.hero-section { position: relative; overflow: hidden; background: var(--cream); padding: 0 48px; margin-top: 72px; }
.hero-orb-a { position:absolute; border-radius:50%; pointer-events:none; filter:blur(110px); width:640px; height:640px; background:radial-gradient(circle, rgba(37,99,235,0.055) 0%, transparent 68%); top:-250px; right:-60px; animation: orbDrift 10s ease-in-out infinite alternate; }
.hero-orb-b { position:absolute; border-radius:50%; pointer-events:none; filter:blur(90px); width:440px; height:440px; background:radial-gradient(circle, rgba(174,174,178,0.1) 0%, transparent 68%); bottom:-120px; left:-60px; animation: orbDrift 13s ease-in-out infinite alternate-reverse; }
.hero-texture { position:absolute; inset:0; pointer-events:none; background-image: radial-gradient(var(--cream-3) 1px, transparent 1px); background-size: 30px 30px; opacity: 0.55; mask-image: linear-gradient(135deg, transparent 35%, rgba(0,0,0,0.45) 100%); -webkit-mask-image: linear-gradient(135deg, transparent 35%, rgba(0,0,0,0.45) 100%); }
.hero-inner { max-width: 1200px; margin: 0 auto; padding: 4px 0 56px; position:relative; z-index:1; display: grid; grid-template-columns: 1fr 320px; gap: 72px; align-items: center; }

.hero-tag {
  display:inline-flex; align-items:center; gap:8px;
  background: rgba(37,99,235,0.06);
  border:1px solid rgba(37,99,235,0.18);
  border-radius:980px; padding: 5px 15px 5px 9px;
  margin-bottom:28px; animation: tagIn 0.6s 0.1s both;
}
.hero-tag-dot { width:8px; height:8px; border-radius:50%; background:var(--blue); flex-shrink:0; animation: pulseDot 2s ease-in-out infinite; }
.hero-tag-txt { font-family:var(--fu); font-size:12px; font-weight:500; color:var(--blue-dk); letter-spacing:0.02em; }

.hero-h1 { font-family: var(--fd); font-size: clamp(44px,5.2vw,76px); font-weight:800; letter-spacing:-0.035em; line-height:1.07; color:var(--ink); margin-bottom:20px; animation: fadeUp 0.7s 0.2s both; }
.hero-h1 em { font-style:italic; background:linear-gradient(135deg, #0F2D6B 0%, #1D4ED8 50%, #2563EB 100%); background-size:200% 200%; -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; animation: shimmer 5s ease-in-out infinite; }
.hero-desc { font-family:var(--fu); font-size:17px; font-weight:350; line-height:1.7; color:var(--gray); max-width:460px; margin-bottom:38px; animation: fadeUp 0.7s 0.32s both; }
.hero-chips { display:flex; flex-wrap:wrap; gap:9px; margin-bottom:46px; animation: fadeUp 0.6s 0.44s both; }
.h-chip { display:flex; align-items:center; gap:7px; background:var(--card); border:1px solid var(--border-2); border-radius:980px; padding:5px 14px; font-family:var(--fu); font-size:12.5px; font-weight:450; color:var(--ink-2); box-shadow:0 1px 4px rgba(0,0,0,0.05); transition: transform 0.18s, box-shadow 0.18s; }
.h-chip:hover { transform:translateY(-1px); box-shadow:0 4px 12px rgba(0,0,0,0.09); }
.h-chip-dot { width:6px; height:6px; border-radius:50%; background:var(--gold-lt); }
.hero-stats { display:flex; border-top:1px solid var(--border); padding-top:30px; animation: fadeUp 0.6s 0.56s both; }
.h-stat { flex:1; padding:0 24px; border-right:1px solid var(--border); }
.h-stat:first-child { padding-left:0; }
.h-stat:last-child { border-right:none; }
.h-stat-val { font-family:var(--fd); font-size:32px; font-weight:800; letter-spacing:-0.03em; color:var(--ink); line-height:1; }
.h-stat-lbl { font-family:var(--fu); font-size:11.5px; font-weight:400; color:var(--gray-2); margin-top:4px; }

.hero-right { animation: fadeUp 0.8s 0.28s both; }
.mock-wrap { position:relative; width:300px; animation: cardFloat 5s ease-in-out infinite; }
.mock-shadow { position:absolute; bottom:-20px; left:50%; transform:translateX(-50%); width:200px; height:32px; background:rgba(0,0,0,0.13); border-radius:50%; filter:blur(18px); opacity:0.7; }
.mock-card { background:var(--ink); border-radius:22px; padding:28px 26px; box-shadow:0 20px 60px rgba(0,0,0,0.2), 0 4px 16px rgba(0,0,0,0.13); position:relative; overflow:hidden; }
.mock-glow { position:absolute; border-radius:50%; filter:blur(55px); pointer-events:none; width:200px; height:200px; background:rgba(37,99,235,0.22); top:-60px; right:-50px; }
.mock-ey { font-family:var(--fu); font-size:9px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:rgba(255,255,255,0.3); margin-bottom:11px; }
.mock-lbl { font-family:var(--fd); font-size:28px; font-weight:800; letter-spacing:-0.02em; line-height:1.1; background:linear-gradient(135deg,#93C5FD,#60A5FA,#3B82F6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:4px; }
.mock-conf { display:flex; align-items:baseline; gap:3px; margin-bottom:20px; }
.mock-conf-n { font-family:var(--fd); font-size:22px; font-weight:800; color:rgba(255,255,255,0.9); font-variant-numeric:tabular-nums; }
.mock-conf-u { font-family:var(--fu); font-size:11px; color:rgba(255,255,255,0.3); }
.mock-div { height:1px; background:rgba(255,255,255,0.1); margin-bottom:16px; }
.mock-b { margin-bottom:9px; }
.mock-b:last-of-type { margin-bottom:0; }
.mock-b-meta { display:flex; justify-content:space-between; font-family:var(--fu); font-size:10px; color:rgba(255,255,255,0.38); margin-bottom:4px; }
.mock-b-track { height:3px; background:rgba(255,255,255,0.08); border-radius:2px; overflow:hidden; }
.mock-b-fill { height:100%; border-radius:2px; }
.mock-bf-gold { background:linear-gradient(90deg,#1D4ED8,#3B82F6); }
.mock-bf-gray { background:rgba(255,255,255,0.18); }
.mock-chips-r { display:flex; gap:5px; flex-wrap:wrap; margin-top:16px; padding-top:14px; border-top:1px solid rgba(255,255,255,0.07); }
.mock-cp { background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1); border-radius:5px; padding:3px 8px; font-family:var(--fu); font-size:9.5px; font-weight:500; color:rgba(255,255,255,0.36); }

.mock-ring-1, .mock-ring-2 { position:absolute; border-radius:50%; pointer-events:none; border:1px solid var(--border); }
.mock-ring-1 { width:180px; height:180px; top:-50px; right:-90px; opacity:0.45; }
.mock-ring-2 { width:270px; height:270px; top:-80px; right:-130px; opacity:0.25; }

.hero-line { height:1px; background:linear-gradient(90deg,transparent,var(--border-2) 30%,var(--border-2) 70%,transparent); }

/* PAGE LAYOUT */
.pw { max-width:1200px; margin:0 auto; padding:0 44px; }
.gap { height:60px; } .gap-sm { height:28px; }

.eyebrow { font-family:var(--fu); font-size:10.5px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:var(--blue); margin-bottom:7px; display:inline-block; }
.sec-h2 { font-family:var(--fd); font-size:clamp(26px,2.8vw,40px); font-weight:800; letter-spacing:-0.03em; color:var(--ink); margin-bottom:7px; line-height:1.15; }
.sec-sub { font-family:var(--fu); font-size:14.5px; font-weight:400; color:var(--gray); line-height:1.65; margin-bottom:32px; }

/* FORM CARD */
.form-card { background: var(--card); border:1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; margin-bottom:20px; transition: box-shadow 0.28s ease; }
.form-card:hover { box-shadow: var(--shadow-lg); }
.form-accent-bar { height: 4px; background: linear-gradient(90deg, #0F2D6B 0%, var(--blue-dk) 35%, var(--blue) 70%, var(--blue-lt) 100%); }
.form-progress { display: flex; align-items: center; justify-content: center; gap: 0; padding: 26px 48px 4px; animation: fadeUp 0.5s 0.1s both; }
.fp-step { display: flex; align-items: center; gap: 9px; }
.fp-dot { width: 30px; height: 30px; border-radius: 50%; background: linear-gradient(135deg, var(--blue) 0%, var(--blue-dk) 100%); display: flex; align-items: center; justify-content: center; font-family: var(--fu); font-size: 11px; font-weight: 800; color: #fff; flex-shrink: 0; box-shadow: 0 2px 8px rgba(37,99,235,0.35); }
.fp-label { font-family: var(--fu); font-size: 12px; font-weight: 600; color: var(--ink-2); letter-spacing: 0.01em; }
.fp-line { width: 60px; height: 2px; background: var(--cream-3); margin: 0 8px; border-radius: 1px; }
.fp-line-done { background: linear-gradient(90deg, var(--blue), var(--blue-lt)); }

.form-body { padding: 32px 48px 44px; }
.step-section { animation: stepIn 0.5s both; }
.step-hdr { display:flex; align-items:flex-start; gap:14px; margin-bottom:24px; }
.step-n { width:38px; height:38px; border-radius:11px; flex-shrink:0; background:linear-gradient(135deg, var(--blue) 0%, var(--blue-dk) 100%); display:flex; align-items:center; justify-content:center; font-family:var(--fu); font-size:12px; font-weight:800; color:#fff; box-shadow:0 2px 10px rgba(37,99,235,0.35); margin-top:1px; }
.step-t { font-family:var(--fu); font-size:15.5px; font-weight:700; color:var(--ink); letter-spacing:-0.01em; margin-bottom:1px; }
.step-s { font-family:var(--fu); font-size:12.5px; color:var(--gray-2); }

.sep { height:1px; background:var(--cream-2); margin:28px 0; position:relative; }
.sep::after { content:''; position:absolute; top:0; left:0; width:80px; height:1px; background:linear-gradient(90deg, var(--gold-lt), transparent); }
.field-hint { font-family:var(--fu); font-size:11.5px; color:var(--gray-2); margin-top:5px; line-height:1.4; }

/* INPUT OVERRIDES */
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label {
  font-family: var(--fu) !important;
  font-size: 10.5px !important; font-weight: 700 !important;
  color: var(--gray) !important;
  letter-spacing: 0.07em !important; text-transform: uppercase !important;
  margin-bottom: 7px !important;
}

[data-testid="stTextInput"] > div > div,
[data-testid="stNumberInput"] > div > div {
  background: var(--card) !important;
  border: 1.5px solid var(--cream-3) !important;
  border-radius: var(--radius-sm) !important;
}
[data-testid="stTextInput"] > div > div:focus-within,
[data-testid="stNumberInput"] > div > div:focus-within {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3.5px var(--blue-ring) !important;
  background: #fff !important;
}
[data-testid="stTextInput"] > div > div > input,
[data-testid="stNumberInput"] > div > div > input {
  font-family: var(--fu) !important;
  background: transparent !important;
  color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important;
  font-size: 15px !important; font-weight: 400 !important;
  padding: 12px 14px !important; font-variant-numeric: tabular-nums !important;
  border: none !important; outline: none !important; box-shadow: none !important;
}
[data-testid="stTextInput"] > div > div > input::placeholder { color: var(--gray-3) !important; }

/* Number input +/- buttons */
[data-testid="stNumberInput"] button,
[data-testid="stNumberInput"] button[kind="secondary"],
[data-testid="stNumberInput"] > div > div > button {
  background: var(--cream-2) !important;
  background-color: var(--cream-2) !important;
  border: none !important;
  border-left: 1px solid var(--cream-3) !important;
  color: var(--ink) !important;
  -webkit-text-fill-color: var(--ink) !important;
  box-shadow: none !important;
  transition: background 0.15s ease !important;
}
[data-testid="stNumberInput"] button:hover,
[data-testid="stNumberInput"] > div > div > button:hover {
  background: var(--cream-3) !important;
  background-color: var(--cream-3) !important;
}
[data-testid="stNumberInput"] button svg,
[data-testid="stNumberInput"] > div > div > button svg {
  fill: var(--ink) !important;
  stroke: var(--ink) !important;
  color: var(--ink) !important;
}

[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
  font-family: var(--fu) !important;
  background: var(--card) !important;
  border: 1.5px solid var(--cream-3) !important;
  border-radius: var(--radius-sm) !important;
  min-height: 46px !important; color: var(--ink) !important;
  transition: border-color 0.18s, box-shadow 0.18s !important;
}
[data-testid="stSelectbox"] > div > div:focus-within,
[data-testid="stMultiSelect"] > div > div:focus-within {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3.5px var(--blue-ring) !important;
}
[data-testid="stSelectbox"] span, [data-testid="stMultiSelect"] span { color: var(--ink) !important; font-family: var(--fu) !important; font-size: 15px !important; }
[data-testid="stSelectbox"] svg, [data-testid="stMultiSelect"] svg { color: var(--gray-2) !important; }

[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] > label,
[data-testid="stCheckbox"] > label > div,
[data-testid="stCheckbox"] > label > span,
[data-testid="stCheckbox"] p,
[data-testid="stCheckbox"] span {
  font-family: var(--fu) !important;
  color: var(--ink) !important;
  -webkit-text-fill-color: var(--ink) !important;
}
[data-testid="stCheckbox"] label {
  font-size: 14px !important; font-weight: 500 !important;
  text-transform: none !important; letter-spacing: 0 !important;
}
[data-testid="stCheckbox"] > label {
  display: flex !important; align-items: center !important;
  gap: 12px !important; cursor: pointer !important;
  background: var(--card) !important;
  border: 1.5px solid var(--cream-3) !important;
  border-radius: var(--radius-sm) !important;
  padding: 12px 16px !important;
  transition: border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease !important;
  min-height: 48px !important;
}
[data-testid="stCheckbox"] > label:hover {
  border-color: var(--blue-lt) !important;
  background: var(--blue-pale) !important;
  box-shadow: 0 0 0 3px var(--blue-ring) !important;
}
[data-testid="stCheckbox"] input[type="checkbox"] {
  accent-color: var(--blue) !important;
  width: 17px !important; height: 17px !important;
  flex-shrink: 0 !important; cursor: pointer !important;
}

/* SUBMIT BUTTON */
[data-testid="stFormSubmitButton"] { display: flex !important; justify-content: flex-start !important; }
[data-testid="stFormSubmitButton"] > button,
button[kind="primaryFormSubmit"],
[data-testid="baseButton-primaryFormSubmit"] {
  font-family: var(--fu) !important;
  width: auto !important; min-width: 220px !important;
  background: linear-gradient(135deg, var(--blue) 0%, var(--blue-dk) 100%) !important;
  color: #fff !important;
  border: none !important; border-radius: 12px !important;
  padding: 14px 44px !important;
  font-size: 15px !important; font-weight: 700 !important;
  letter-spacing: -0.01em !important;
  box-shadow: 0 2px 8px rgba(37,99,235,0.35), 0 8px 28px rgba(37,99,235,0.25), 0 0 0 1px rgba(37,99,235,0.15) !important;
  transition: transform 0.22s cubic-bezier(0.22,1,0.36,1), box-shadow 0.22s ease !important;
  cursor: pointer !important; margin-top: 12px !important;
  display: inline-flex !important; align-items: center !important; gap: 10px !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
  background: linear-gradient(135deg, var(--blue-lt) 0%, var(--blue) 100%) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 18px rgba(37,99,235,0.45), 0 16px 48px rgba(37,99,235,0.3), 0 0 0 1px rgba(37,99,235,0.2) !important;
}
[data-testid="stFormSubmitButton"] > button:active { transform: translateY(0) !important; }

/* RESULT */
.result-reveal { animation: resultReveal 0.55s cubic-bezier(0.22,1,0.36,1) both; }
.res-card { background:var(--ink); border-radius:24px; padding:48px 52px; margin-bottom:20px; position:relative; overflow:hidden; box-shadow:0 8px 32px rgba(0,0,0,0.16), 0 24px 80px rgba(0,0,0,0.1); }
.res-glow { position:absolute; border-radius:50%; filter:blur(80px); pointer-events:none; }
.rg0 { width:420px; height:420px; background:rgba(34,211,238,0.14); top:-120px; right:-80px; }
.rg1 { width:380px; height:380px; background:rgba(244,63,94,0.16); top:-100px; right:-80px; }
.rg2 { width:460px; height:460px; background:rgba(37,99,235,0.18); top:-100px; right:-60px; }

.res-ey { font-family:var(--fu); font-size:10px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:rgba(255,255,255,0.28); margin-bottom:14px; }
.res-lbl { font-family:var(--fd); font-size:clamp(36px,5vw,62px); font-weight:900; letter-spacing:-0.04em; line-height:1.0; margin-bottom:12px; }
.rl0 { background:linear-gradient(135deg,#67E8F9,#22D3EE); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.rl1 { background:linear-gradient(135deg,#FDA4AF,#F43F5E); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.rl2 { background:linear-gradient(135deg,#93C5FD,#60A5FA,#3B82F6); background-size:200% 200%; -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; animation:shimmer 4s ease-in-out infinite; }
.res-conf { display:flex; align-items:baseline; gap:8px; margin-bottom:32px; }
.rc-n { font-family:var(--fd); font-size:42px; font-weight:900; letter-spacing:-0.04em; color:rgba(255,255,255,0.95); font-variant-numeric:tabular-nums; }
.rc-l { font-family:var(--fu); font-size:14px; color:rgba(255,255,255,0.3); }
.res-sep { height:1px; background:rgba(255,255,255,0.1); margin-bottom:22px; }
.res-chips { display:flex; flex-wrap:wrap; gap:8px; }
.res-chip { font-family:var(--fu); background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1); border-radius:8px; padding:5px 12px; font-size:12px; font-weight:500; color:rgba(255,255,255,0.45); white-space:nowrap; font-variant-numeric:tabular-nums; }
.res-chip b { color:rgba(255,255,255,0.82); font-weight:600; margin-left:4px; }

.prob-row { padding:12px 0; border-bottom:1px solid var(--cream-2); }
.prob-row:last-child { border-bottom:none; }
.prob-top { display:flex; justify-content:space-between; margin-bottom:8px; }
.prob-lbl { font-family:var(--fu); font-size:13.5px; font-weight:600; color:var(--ink); }
.prob-pct { font-family:var(--fu); font-size:13.5px; font-weight:700; color:var(--ink); font-variant-numeric:tabular-nums; }
.prob-track { height:5px; background:var(--cream-2); border-radius:3px; overflow:hidden; }
.prob-fill { height:100%; border-radius:3px; animation:barGrow 0.9s cubic-bezier(0.22,1,0.36,1) both; }
.pf-on { background:linear-gradient(90deg,var(--ink),var(--ink-2)); }
.pf-off { background:var(--cream-3); }

.ana-body { font-family:var(--fu); font-size:14.5px; font-weight:400; line-height:1.75; color:var(--gray); }
.ana-body p { margin-bottom:14px; }
.ana-body p:last-child { margin-bottom:0; }
.hl { font-weight:600; color:var(--ink); }
.caveat { font-family:var(--fu); font-size:12px; color:var(--gray-2); line-height:1.65; padding-top:15px; margin-top:18px; border-top:1px solid var(--cream-3); }

.sub-card { background:var(--card); border:1px solid var(--border); border-radius:var(--radius); padding:30px 34px; margin-bottom:20px; box-shadow:0 1px 4px rgba(0,0,0,0.04),0 4px 20px rgba(0,0,0,0.05); }
.sub-lbl { font-family:var(--fu); font-size:10px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:var(--gray-2); margin-bottom:16px; }

/* ABOUT */
.about-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-top:30px; }
.about-card { background:var(--card); border:1px solid var(--border); border-radius:18px; padding:26px 24px; box-shadow:0 1px 4px rgba(0,0,0,0.03); transition:box-shadow 0.22s, transform 0.22s, border-color 0.22s; }
.about-card:hover { box-shadow:var(--shadow); transform:translateY(-2px); border-color:var(--border-2); }
.abt-icon { width:44px; height:44px; border-radius:12px; margin-bottom:16px; display:flex; align-items:center; justify-content:center; font-size:18px; }
.abt-icon-blue { background:var(--blue-pale); border:1px solid rgba(37,99,235,0.2); }
.abt-icon-gold { background:var(--blue-pale); border:1px solid rgba(37,99,235,0.18); }
.abt-icon-gray { background:rgba(0,0,0,0.04); border:1px solid var(--border); }
.abt-t { font-family:var(--fu); font-size:14.5px; font-weight:700; color:var(--ink); margin-bottom:6px; letter-spacing:-0.01em; }
.abt-d { font-family:var(--fu); font-size:12.5px; color:var(--gray); line-height:1.6; }

/* FOOTER */
.site-footer { border-top:1px solid var(--border); padding:32px 44px; background:var(--cream); }
.ft-inner { max-width:1200px; margin:0 auto; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; }
.ft-left { display:flex; align-items:center; gap:9px; }
.ft-box { width:22px; height:22px; border-radius:6px; background:var(--ink); display:flex; align-items:center; justify-content:center; }
.ft-box svg { width:10px; height:10px; }
.ft-brand { font-family:var(--fd); font-size:13.5px; font-weight:700; color:var(--ink); }
.ft-note { font-family:var(--fu); font-size:12px; color:var(--gray-2); }

/* SPLASH SCREEN */
@keyframes splashLogoIn {
  from { opacity:0; transform:scale(0.78) translateY(20px); filter:blur(4px); }
  to   { opacity:1; transform:scale(1) translateY(0); filter:blur(0); }
}
@keyframes splashNameIn {
  from { opacity:0; transform:translateY(12px); letter-spacing:0.42em; }
  to   { opacity:0.55; transform:translateY(0); letter-spacing:0.24em; }
}
@keyframes splashFadeOut {
  from { opacity:1; }
  to   { opacity:0; }
}
@keyframes splashHide {
  to { visibility:hidden; pointer-events:none; }
}
@keyframes splashRingIn {
  0%   { transform:scale(0.5); opacity:0; }
  30%  { opacity:0.5; }
  100% { transform:scale(1); opacity:0; }
}
@keyframes splashGoldPulse {
  0%,100% { opacity:0.18; }
  50%     { opacity:0.32; }
}
#sc-splash {
  position:fixed; inset:0; z-index:99999999;
  background:#100F0E;
  display:flex; align-items:center; justify-content:center; flex-direction:column;
  gap:32px;
  animation: splashFadeOut 0.85s 2.6s cubic-bezier(0.4,0,0.2,1) forwards,
             splashHide 0s 3.5s forwards;
}
.sc-sp-wrap {
  position:relative; width:280px; height:280px;
  display:flex; align-items:center; justify-content:center;
}
.sc-sp-ring {
  position:absolute; border-radius:50%;
  border:1px solid rgba(37,99,235,0.25);
  animation:splashRingIn 2.2s ease-out infinite;
}
.sc-sp-ring-1 { width:168px; height:168px; animation-delay:0s; }
.sc-sp-ring-2 { width:224px; height:224px; animation-delay:0.55s; }
.sc-sp-ring-3 { width:280px; height:280px; animation-delay:1.1s; }
.sc-sp-box {
  width:132px; height:132px; border-radius:38px;
  background:linear-gradient(145deg,#1A1816 0%,#2A2724 50%,#1A1816 100%);
  box-shadow: 0 0 0 1px rgba(255,255,255,0.055),
              0 6px 24px rgba(0,0,0,0.55),
              0 32px 72px rgba(0,0,0,0.6),
              0 0 80px rgba(245,158,11,0.06);
  display:flex; align-items:center; justify-content:center;
  position:relative; overflow:hidden;
  opacity:0;
  animation:splashLogoIn 1.05s 0.1s cubic-bezier(0.22,1,0.36,1) forwards;
}
.sc-sp-glow {
  position:absolute; width:160px; height:160px; border-radius:50%;
  background:radial-gradient(circle, rgba(37,99,235,0.22) 0%, transparent 70%);
  top:-30px; right:-30px;
  animation:splashGoldPulse 2.5s ease-in-out infinite;
}
.sc-sp-shimmer {
  position:absolute; inset:0; border-radius:38px;
  background:linear-gradient(125deg, transparent 0%, rgba(147,197,253,0.08) 50%, transparent 100%);
  background-size:200% 200%;
  animation:shimmer 3.5s ease-in-out infinite;
}
.sc-sp-letters {
  font-family:-apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", sans-serif;
  font-size:60px; font-weight:800; font-style:normal;
  background:linear-gradient(135deg,#93C5FD 0%,#60A5FA 40%,#3B82F6 80%,#93C5FD 100%);
  background-size:200% 200%;
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  letter-spacing:-0.05em; line-height:1; position:relative; z-index:1;
  animation:shimmer 4s ease-in-out infinite;
}
.sc-sp-name-row {
  display:flex; align-items:center; gap:12px;
  font-family:-apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif;
  font-size:12px; font-weight:600; text-transform:uppercase;
  color:rgba(255,255,255,0.55); letter-spacing:0.24em;
  opacity:0;
  animation:splashNameIn 1s 0.55s cubic-bezier(0.22,1,0.36,1) forwards;
}
.sc-sp-dot {
  width:3px; height:3px; border-radius:50%;
  background:rgba(96,165,250,0.8); flex-shrink:0;
}

/* ===================== RESPONSIVE ===================== */

/* Tablet */
@media (max-width: 1024px) {
  .hero-inner { grid-template-columns: 1fr 260px; gap: 44px; padding: 20px 0 52px; }
  .about-grid { grid-template-columns: repeat(2, 1fr); }
  .pw { padding: 0 32px; }
  .hero-section { padding: 0 32px; }
  .nav { padding: 0 32px; }
}

/* Mobile */
@media (max-width: 768px) {
  /* === NAV === */
  .nav { padding: 0 18px; height: 58px; }
  .nav-links a:not(.nav-btn) { display: none !important; }
  .nav-btn { padding: 8px 15px !important; font-size: 12.5px !important; border-radius: 9px !important; }
  .nav-brand-name { font-size: 15px !important; }
  .nav-logo-box { width: 34px; height: 34px; }

  /* === HERO === */
  .hero-section { margin-top: 58px; padding: 0 18px; }
  .hero-inner {
    grid-template-columns: 1fr;
    gap: 0;
    padding: 16px 0 36px;
  }
  .hero-right { display: none !important; }
  .hero-h1 { font-size: clamp(34px, 8.5vw, 52px); margin-bottom: 14px; }
  .hero-desc { font-size: 15px; line-height: 1.65; margin-bottom: 24px; max-width: 100%; }
  .hero-chips { margin-bottom: 28px; gap: 7px; }
  .h-chip { font-size: 11.5px; padding: 4px 12px; }
  .hero-stats { padding-top: 22px; }
  .h-stat { padding: 0 14px; }
  .h-stat-val { font-size: 24px; }
  .h-stat-lbl { font-size: 10.5px; }
  .hero-tag { margin-bottom: 20px; }

  /* === PAGE LAYOUT === */
  .pw { padding: 0 18px; }
  .gap { height: 36px; }
  .gap-sm { height: 14px; }
  .sec-h2 { font-size: clamp(22px, 5.5vw, 32px); }
  .sec-sub { font-size: 13.5px; margin-bottom: 22px; }

  /* === FORM === */
  .form-progress { padding: 18px 18px 4px; }
  .fp-label { display: none !important; }
  .fp-line { width: 24px !important; margin: 0 4px !important; }
  .fp-dot { width: 26px !important; height: 26px !important; font-size: 10px !important; }
  .form-body { padding: 18px 18px 28px; }
  .step-t { font-size: 14px; }
  .step-s { font-size: 11.5px; }
  .sep { margin: 20px 0; }

  /* Fix spacing: hint text nabrak label berikutnya */
  .field-hint { margin-bottom: 14px !important; }
  .form-body .element-container,
  .form-body .stMarkdown { margin-bottom: 4px !important; }

  /* Streamlit columns → stack vertically */
  [data-testid="stHorizontalBlock"] {
    flex-direction: column !important;
    gap: 0 !important;
  }
  [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
    width: 100% !important;
    min-width: 0 !important;
    flex: 1 1 100% !important;
    margin-bottom: 10px !important;
  }
  [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"]:last-child {
    margin-bottom: 0 !important;
  }

  /* Fix multiselect tag terpotong */
  [data-testid="stMultiSelect"] [data-baseweb="tag"] {
    max-width: calc(100% - 32px);
    overflow: hidden;
  }
  [data-testid="stMultiSelect"] [data-baseweb="tag"] span {
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    max-width: 140px;
  }

  /* Submit button full width */
  [data-testid="stFormSubmitButton"] { justify-content: stretch !important; }
  [data-testid="stFormSubmitButton"] > button {
    width: 100% !important;
    min-width: 0 !important;
    justify-content: center !important;
    padding: 14px 24px !important;
  }

  /* === RESULT === */
  .res-card { padding: 28px 20px; border-radius: 18px; }
  .res-lbl { font-size: clamp(30px, 8vw, 48px); }
  .rc-n { font-size: 34px; }
  .res-conf { margin-bottom: 24px; }
  .sub-card { padding: 20px 18px; }
  .ana-body { font-size: 13.5px; }

  /* === ABOUT === */
  .about-grid { grid-template-columns: 1fr; gap: 10px; }

  /* === FOOTER === */
  .site-footer { padding: 22px 18px; }
  .ft-inner { flex-direction: column; align-items: flex-start; gap: 6px; }
}

/* Small phones */
@media (max-width: 430px) {
  .nav-brand-name { display: none !important; }
  .nav-logo-box { width: 32px; height: 32px; }
  .sc-mono { font-size: 15px; }

  .hero-h1 { font-size: clamp(30px, 8vw, 42px); letter-spacing: -0.025em; }
  .hero-desc { font-size: 14px; }
  .h-stat { padding: 0 10px; }
  .h-stat-val { font-size: 20px; }
  .h-stat-lbl { font-size: 9.5px; }

  .form-body { padding: 14px 14px 22px; }
  .form-progress { padding: 14px 14px 4px; }
  .fp-line { width: 18px !important; }

  /* Pastikan spacing hint tetap ada di HP kecil */
  .field-hint { margin-bottom: 16px !important; font-size: 11px !important; }
  [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
    margin-bottom: 8px !important;
  }

  .res-card { padding: 22px 16px; }
  .res-lbl { font-size: clamp(26px, 7.5vw, 38px); }
  .rc-n { font-size: 28px; }
  .res-chips { gap: 5px; }
  .res-chip { font-size: 11px; padding: 4px 9px; }

  .sub-card { padding: 18px 14px; }
  .sec-h2 { font-size: clamp(20px, 5.5vw, 28px); }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# MODEL LOADING
@st.cache_resource
def load_model():
    m    = joblib.load("model/model_game_type.pkl")
    meta = joblib.load("model/model_meta.pkl")
    return m, meta

model, meta = load_model()
FEATURES = meta["feature_cols"]
LABELS   = meta["label_names"]   # ['Singleplayer', 'Multiplayer', 'Hybrid']

KAT_OPTIONS = ["Top Sellers", "Most Played", "New Releases", "Upcoming Releases"]
KAT_MAP = {"Top Sellers":"topsellers", "Most Played":"mostplayed",
           "New Releases":"newreleases", "Upcoming Releases":"upcoming"}

OS_OPTIONS = ["Windows", "macOS", "Linux / SteamOS"]
CTRL_OPTIONS = ["Full Controller Support", "Xbox Controller", "PlayStation Controller"]

# HELPERS
def analysis_text(pred, proba, nama, orig, diskon, reviews, tahun, is_free, kats, oses, ctrls):
    lbl  = LABELS[pred]
    conf = proba[pred] * 100
    age_d = max((date.today() - date(int(tahun), 1, 1)).days, 0)
    age_y = age_d / 365.25
    cw = ("sangat tinggi" if conf>=80 else "cukup tinggi" if conf>=60 else "moderat" if conf>=45 else "rendah")

    # Indikator umum
    free_str = "Game gratis" if is_free else f"Berbayar (${orig:.2f})" if False else f"Berbayar (Rp {orig:,.0f})"
    multi_os = len(oses) >= 2
    has_full_ctrl = any('Full' in o for o in ctrls)
    review_tier = ("rendah" if reviews<5000 else "menengah" if reviews<50000 else "tinggi")

    # Faktor pendukung — beda per kelas
    if pred == 0:  # Singleplayer
        factor = (f"Karakteristik input — {'gratis' if is_free else f'berbayar Rp {orig:,.0f}'}, "
                  f"{review_tier} review ({int(reviews):,}), "
                  f"{'full controller support' if has_full_ctrl else 'controller terbatas'}, "
                  f"{'multi-platform' if multi_os else 'platform terbatas'} — "
                  f"mirip pola game singleplayer di dataset.")
        ctx = ("Game Singleplayer adalah kelas kedua terbesar (~41% data). "
               "Karakter umumnya: berbayar (97% tidak gratis), full controller support tinggi (63%), "
               "% review positif paling tinggi (86.6%) — komunitasnya paling puas.")
    elif pred == 1:  # Multiplayer
        factor = (f"Karakteristik input — {'gratis' if is_free else f'berbayar Rp {orig:,.0f}'}, "
                  f"{review_tier} review ({int(reviews):,}), "
                  f"{'multi-platform' if multi_os else 'Windows-only'} — "
                  f"mirip pola game multiplayer di dataset.")
        ctx = ("Game Multiplayer adalah kelas minoritas (~11% data). "
               "Karakter umumnya: hampir setengah gratis/F2P (49%), Windows-only (82%), "
               "jumlah review tertinggi (rata-rata 86k) — paling rame, paling kritis komunitas.")
    else:  # Hybrid
        factor = (f"Karakteristik input — {'gratis' if is_free else f'berbayar Rp {orig:,.0f}'}, "
                  f"{review_tier} review ({int(reviews):,}), umur {age_y:.1f} tahun — "
                  f"mirip pola game Hybrid di dataset.")
        ctx = ("Game Hybrid (single + multi) adalah kelas mayoritas (~49% data). "
               "Karakter di tengah-tengah: mostly berbayar (91% tidak gratis), "
               "campuran controller support, mengakomodasi pemain solo & sosial.")

    intro = (f"<p>Model mengklasifikasikan <span class='hl'>{nama}</span> sebagai "
             f"<span class='hl'>{lbl}</span> dengan keyakinan <span class='hl'>{conf:.1f}%</span> ({cw}).</p>")
    para1 = f"<p><span class='hl'>Faktor pendukung:</span> {factor}</p>"
    para2 = f"<p><span class='hl'>Konteks dataset:</span> {ctx}</p>"
    para3 = (f"<p><span class='hl'>Umur game:</span> {age_d} hari ({age_y:.1f} tahun). "
             f"Umur tidak terlalu mendiskriminasi jenis game, tapi game lama cenderung punya lebih banyak review terkumpul.</p>")
    caveat = ("<p class='caveat'>Catatan: Model hanya membaca metadata publik (harga, OS, controller, review count). "
              "Genre, gameplay, story, dan elemen sosial tidak dianalisis. "
              "Hasil ini referensi analitik, bukan keputusan final.</p>")
    return intro + para1 + para2 + para3 + caveat

def prob_html(proba, pred):
    out = ""
    for i, (lbl, p) in enumerate(zip(LABELS, proba)):
        pct = p * 100
        cls = "pf-on" if i == pred else "pf-off"
        d = f"animation-delay:{i*0.14:.2f}s;"
        out += (f"<div class='prob-row'><div class='prob-top'><span class='prob-lbl'>{lbl}</span>"
                f"<span class='prob-pct'>{pct:.1f}%</span></div>"
                f"<div class='prob-track'><div class='prob-fill {cls}' style='width:{pct:.2f}%;{d}'></div></div></div>")
    return out

def chip_html(orig, diskon, reviews, tahun, is_free, kats, oses, ctrls):
    age_d = max((date.today() - date(int(tahun), 1, 1)).days, 0)
    age_y = age_d / 365.25
    harga_str = "Gratis" if is_free else f"Rp {orig:,.0f}"
    kat_str = ", ".join(kats) if kats else "—"
    os_str = ", ".join(oses) if oses else "—"
    ctrl_str = ", ".join([c.split()[0] for c in ctrls]) if ctrls else "—"
    data = [("Harga", harga_str),
            ("Diskon", f"{diskon:.0f}%" if diskon > 0 else "—"),
            ("Review", f"{int(reviews):,}"),
            ("Umur", f"{age_y:.1f} thn"),
            ("Kategori", kat_str),
            ("OS", os_str),
            ("Controller", ctrl_str)]
    return "".join(f"<div class='res-chip'>{k}<b>{v}</b></div>" for k, v in data)

# SPLASH SCREEN (shown only once per session)
_SPLASH_HTML = (
    "<div id='sc-splash'>"
    "<div class='sc-sp-wrap'>"
    "<div class='sc-sp-ring sc-sp-ring-3'></div>"
    "<div class='sc-sp-ring sc-sp-ring-2'></div>"
    "<div class='sc-sp-ring sc-sp-ring-1'></div>"
    "<div class='sc-sp-box'>"
    "<div class='sc-sp-glow'></div>"
    "<div class='sc-sp-shimmer'></div>"
    "<span class='sc-sp-letters'>SC</span>"
    "</div></div>"
    "<div class='sc-sp-name-row'>"
    "Steam<div class='sc-sp-dot'></div>Classifier"
    "</div></div>"
)
if '_splash_shown' not in st.session_state:
    st.session_state['_splash_shown'] = True
    st.markdown(_SPLASH_HTML, unsafe_allow_html=True)

# NAVIGATION
_SC_LOGO = "<span class='sc-mono'>SC</span>"

st.markdown(
    f"<div class='nav'><div class='nav-inner'>"
    f"<a class='nav-brand' href='#'>"
    f"<div class='nav-logo-box'>{_SC_LOGO}</div>"
    f"<span class='nav-brand-name'>Steam Classifier</span>"
    f"</a>"
    f"<div class='nav-links'>"
    f"<a href='#'>Beranda</a>"
    f"<a href='#prediksi'>Prediksi</a>"
    f"<a href='#tentang'>Tentang</a>"
    f"<a class='nav-btn' href='#prediksi'>Mulai Klasifikasi</a>"
    f"</div></div></div>",
    unsafe_allow_html=True,
)

# HERO
st.markdown(
    "<div class='hero-section'>"
    "<div class='hero-orb-a'></div><div class='hero-orb-b'></div><div class='hero-texture'></div>"
    "<div class='hero-inner'>"
    "<div class='hero-left'>"
    "<div class='hero-tag'><div class='hero-tag-dot'></div><span class='hero-tag-txt'>Machine Learning &middot; Steam Analytics</span></div>"
    "<h1 class='hero-h1'>Klasifikasi Jenis<br><em>Game Steam</em></h1>"
    "<p class='hero-desc'>Masukkan metadata game untuk mengklasifikasikan jenisnya berdasarkan mode pemain — Singleplayer, Multiplayer, atau Hybrid — dari pola ribuan judul di platform Steam.</p>"
    "<div class='hero-chips'>"
    "<div class='h-chip'><div class='h-chip-dot'></div>Random Forest Model</div>"
    "<div class='h-chip'><div class='h-chip-dot'></div>19 Fitur Metadata</div>"
    "<div class='h-chip'><div class='h-chip-dot'></div>3 Kelas Output</div>"
    "</div>"
    "<div class='hero-stats'>"
    "<div class='h-stat'><div class='h-stat-val'>3</div><div class='h-stat-lbl'>Kelas Jenis Game</div></div>"
    "<div class='h-stat'><div class='h-stat-val'>19</div><div class='h-stat-lbl'>Fitur Input</div></div>"
    "<div class='h-stat'><div class='h-stat-val'>1.1K</div><div class='h-stat-lbl'>Game Terlatih</div></div>"
    "</div></div>"
    "<div class='hero-right'>"
    "<div class='mock-ring-1'></div><div class='mock-ring-2'></div>"
    "<div class='mock-wrap'>"
    "<div class='mock-shadow'></div>"
    "<div class='mock-card'><div class='mock-glow'></div>"
    "<div class='mock-ey'>Contoh Hasil Klasifikasi</div>"
    "<div class='mock-lbl'>Hybrid</div>"
    "<div class='mock-conf'><span class='mock-conf-n'>72.4</span><span class='mock-conf-u'>% keyakinan</span></div>"
    "<div class='mock-div'></div>"
    "<div class='mock-b'><div class='mock-b-meta'><span>Singleplayer</span><span>18%</span></div><div class='mock-b-track'><div class='mock-b-fill mock-bf-gray' style='width:18%'></div></div></div>"
    "<div class='mock-b'><div class='mock-b-meta'><span>Multiplayer</span><span>10%</span></div><div class='mock-b-track'><div class='mock-b-fill mock-bf-gray' style='width:10%'></div></div></div>"
    "<div class='mock-b'><div class='mock-b-meta'><span>Hybrid</span><span>72%</span></div><div class='mock-b-track'><div class='mock-b-fill mock-bf-gold' style='width:72%'></div></div></div>"
    "<div class='mock-chips-r'><div class='mock-cp'>Top Sellers</div><div class='mock-cp'>Rp 299k</div><div class='mock-cp'>Full Controller</div></div>"
    "</div></div></div>"
    "</div></div>"
    "<div class='hero-line'></div>",
    unsafe_allow_html=True,
)

# FORM SECTION
st.markdown("<div class='pw' id='prediksi'><div class='gap'></div>", unsafe_allow_html=True)
st.markdown(
    "<div class='eyebrow'>Klasifikasi</div>"
    "<div class='sec-h2'>Detail Game</div>"
    "<div class='sec-sub'>Lengkapi tiga bagian di bawah untuk menghasilkan klasifikasi jenis game berbasis ML.</div>",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='form-card'>"
    "<div class='form-accent-bar'></div>"
    "<div class='form-progress'>"
    "<div class='fp-step'><div class='fp-dot'>1</div><span class='fp-label'>Identitas</span></div>"
    "<div class='fp-line fp-line-done'></div>"
    "<div class='fp-step'><div class='fp-dot'>2</div><span class='fp-label'>Harga &amp; Review</span></div>"
    "<div class='fp-line fp-line-done'></div>"
    "<div class='fp-step'><div class='fp-dot'>3</div><span class='fp-label'>Platform</span></div>"
    "</div>"
    "<div class='form-body'>",
    unsafe_allow_html=True,
)

with st.form("pred_form", clear_on_submit=False):
    # Step 1: Identitas
    st.markdown(
        "<div class='step-section'>"
        "<div class='step-hdr'><div class='step-n'>01</div>"
        "<div><div class='step-t'>Identitas Game</div><div class='step-s'>Nama, tahun rilis, dan kategori Steam</div></div>"
        "</div></div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([3, 2], gap="large")
    with c1:
        nama = st.text_input("Nama Game", placeholder="Contoh: Elden Ring")
        st.markdown("<div class='field-hint'>Nama lengkap game seperti tertera di halaman Steam.</div>", unsafe_allow_html=True)
    with c2:
        tahun = st.number_input("Tahun Rilis", min_value=2000, max_value=date.today().year + 1, value=2022, step=1)
        st.markdown("<div class='field-hint'>Tahun rilis game di Steam.</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    kats = st.multiselect("Kategori Steam (boleh pilih lebih dari 1)", options=KAT_OPTIONS, default=["Top Sellers"])
    st.markdown("<div class='field-hint'>1 game bisa muncul di beberapa kategori (mis. Top Sellers + Most Played).</div>", unsafe_allow_html=True)

    st.markdown("<div class='sep'></div>", unsafe_allow_html=True)

    # Step 2: Harga & Review
    st.markdown(
        "<div class='step-section'>"
        "<div class='step-hdr'><div class='step-n'>02</div>"
        "<div><div class='step-t'>Harga, Diskon &amp; Komunitas</div><div class='step-s'>Struktur harga dan ulasan di Steam</div></div>"
        "</div></div>",
        unsafe_allow_html=True,
    )
    c3, c4, c5 = st.columns(3, gap="large")
    with c3:
        is_free = st.checkbox("Free-to-Play", value=False)
        st.markdown("<div class='field-hint'>Aktifkan jika game gratis.</div>", unsafe_allow_html=True)
    with c4:
        harga = st.number_input("Harga Asli (Rp)", min_value=0, max_value=2_000_000, value=200000, step=10000)
        st.markdown("<div class='field-hint'>Harga sebelum diskon.</div>", unsafe_allow_html=True)
    with c5:
        diskon = st.number_input("Diskon (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0, format="%.1f")
        st.markdown("<div class='field-hint'>0 jika tidak ada diskon.</div>", unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    reviews = st.number_input("Jumlah Ulasan Steam", min_value=0, max_value=10_000_000, value=10000, step=1000)
    st.markdown("<div class='field-hint'>Total ulasan pengguna yang diterima game.</div>", unsafe_allow_html=True)

    st.markdown("<div class='sep'></div>", unsafe_allow_html=True)

    # Step 3: Platform
    st.markdown(
        "<div class='step-section'>"
        "<div class='step-hdr'><div class='step-n'>03</div>"
        "<div><div class='step-t'>Platform &amp; Controller</div><div class='step-s'>Sistem operasi & dukungan controller</div></div>"
        "</div></div>",
        unsafe_allow_html=True,
    )
    c6, c7 = st.columns(2, gap="large")
    with c6:
        oses = st.multiselect("Sistem Operasi", options=OS_OPTIONS, default=["Windows"])
        st.markdown("<div class='field-hint'>OS yang didukung game (boleh lebih dari 1).</div>", unsafe_allow_html=True)
    with c7:
        ctrls = st.multiselect("Dukungan Controller", options=CTRL_OPTIONS, default=[])
        st.markdown("<div class='field-hint'>Kosongkan jika tidak ada info controller.</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Jalankan Klasifikasi  →")

st.markdown("</div></div>", unsafe_allow_html=True)

# RESULT
if submitted:
    if not nama.strip():
        st.warning("Masukkan nama game terlebih dahulu.")
    elif not oses:
        st.warning("Pilih minimal 1 sistem operasi.")
    elif not kats:
        st.warning("Pilih minimal 1 kategori Steam.")
    else:
        orig = 0.0 if is_free else float(harga)
        disc = orig * (1.0 - diskon / 100.0)
        age_d = max((date.today() - date(int(tahun), 1, 1)).days, 0)

        # OS one-hot
        os_win = int("Windows" in oses)
        os_mac_v = int("macOS" in oses)
        os_linux_v = int("Linux / SteamOS" in oses)
        os_count_v = os_win + os_mac_v + os_linux_v

        # Controller one-hot
        ctrl_full = int(any('Full' in c for c in ctrls))
        ctrl_xbox = int(any('Xbox' in c for c in ctrls))
        ctrl_ps = int(any('PlayStation' in c for c in ctrls))

        # Search filter one-hot
        kat_vals = [KAT_MAP[k] for k in kats]
        f_top = int("topsellers" in kat_vals)
        f_most = int("mostplayed" in kat_vals)
        f_new = int("newreleases" in kat_vals)
        f_up = int("upcoming" in kat_vals)
        filter_count = f_top + f_most + f_new + f_up

        row = {
            "orig_price": orig, "disc_price": disc, "disc_pct": float(diskon),
            "game_age_days": float(age_d), "name_len": float(len(nama)),
            "is_free": int(is_free), "has_discount": int(diskon > 0),
            "os_windows": os_win, "os_mac": os_mac_v, "os_linux": os_linux_v, "os_count": os_count_v,
            "ctrl_full": ctrl_full, "ctrl_xbox": ctrl_xbox, "ctrl_playstation": ctrl_ps,
            "filter_topsellers": f_top, "filter_mostplayed": f_most,
            "filter_newreleases": f_new, "filter_upcoming": f_up,
            "filter_count": filter_count,
        }
        X = pd.DataFrame([row])[FEATURES]
        pred = int(model.predict(X)[0])
        proba = model.predict_proba(X)[0]
        lbl = LABELS[pred]
        conf = proba[pred] * 100

        st.markdown("<div class='result-reveal'><div class='gap-sm'></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='res-card'>"
            f"<div class='res-glow rg{pred}'></div>"
            f"<div class='res-ey'>Hasil Klasifikasi &mdash; {nama}</div>"
            f"<div class='res-lbl rl{pred}'>{lbl}</div>"
            f"<div class='res-conf'><span class='rc-n'>{conf:.1f}%</span><span class='rc-l'>keyakinan model</span></div>"
            f"<div class='res-sep'></div>"
            f"<div class='res-chips'>{chip_html(orig, diskon, reviews, tahun, is_free, kats, oses, ctrls)}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        ca, cb = st.columns([5, 7], gap="large")
        with ca:
            st.markdown(
                f"<div class='sub-card'><div class='sub-lbl'>Distribusi Probabilitas</div>"
                f"{prob_html(proba, pred)}</div>",
                unsafe_allow_html=True,
            )
        with cb:
            st.markdown(
                f"<div class='sub-card'><div class='sub-lbl'>Analisis Kontekstual</div>"
                f"<div class='ana-body'>{analysis_text(pred, proba, nama, orig, diskon, reviews, tahun, is_free, kats, oses, ctrls)}</div></div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='gap'></div></div>", unsafe_allow_html=True)

# ABOUT
st.markdown(
    "<div style='border-top:1px solid var(--border)'></div>"
    "<div class='pw' id='tentang'><div class='gap'></div>"
    "<div class='eyebrow'>Tentang</div>"
    "<div class='sec-h2'>Cara Kerja Model</div>"
    "<div class='sec-sub'>Random Forest dilatih pada metadata 1.116 game Steam untuk mengklasifikasikan jenis game ke tiga kategori berdasarkan mode pemain.</div>"
    "<div class='about-grid'>"
    "<div class='about-card'><div class='abt-icon abt-icon-blue'>&#9679;</div><div class='abt-t'>Fitur Metadata</div><div class='abt-d'>19 fitur: harga, diskon, umur game, OS support, controller support, dan kategori Steam multi-label.</div></div>"
    "<div class='about-card'><div class='abt-icon abt-icon-gold'>&#9650;</div><div class='abt-t'>Tiga Kelas Output</div><div class='abt-d'>Singleplayer, Multiplayer, dan Hybrid — masing-masing dengan skor probabilitas. SMOTE diterapkan untuk balancing.</div></div>"
    "<div class='about-card'><div class='abt-icon abt-icon-gray'>&#9670;</div><div class='abt-t'>Keterbatasan</div><div class='abt-d'>Genre, gameplay, dan elemen story tidak terukur. Hasil ini referensi analitik, bukan keputusan final.</div></div>"
    "</div><div class='gap'></div></div>",
    unsafe_allow_html=True,
)

# FOOTER
FOOT_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="#F7F4EF" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
st.markdown(
    f"<div class='site-footer'><div class='ft-inner'>"
    f"<div class='ft-left'><div class='ft-box'>{FOOT_SVG}</div><span class='ft-brand'>Steam Classifier</span></div>"
    f"<span class='ft-note'>scikit-learn &middot; Streamlit &middot; Data publik Steam</span>"
    f"</div></div>",
    unsafe_allow_html=True,
)