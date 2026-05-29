"""
app.py — Tugas Besar Machine Learning
Prediksi Sentimen Review Game Steam
Jalankan:  streamlit run app.py
"""
import streamlit as st
import pandas as pd
import joblib
from datetime import date

# ============================================================
# KONFIG
# ============================================================
st.set_page_config(
    page_title="GameSentiment — Prediksi Sentimen Steam",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# LOAD MODEL (path: model/ )
# ============================================================
@st.cache_resource
def load_model():
    model = joblib.load("model/model_steam_sentiment.pkl")
    meta = joblib.load("model/model_meta.pkl")
    return model, meta

model, meta = load_model()
FEATURES = meta["feature_cols"]
LABELS = meta["label_names"]

# ============================================================
# CSS — tema modern, animasi, layout elegan
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root{
  --red:#C8102E; --red-dark:#8E0A1F; --red-light:#FBE3DE;
  --cream:#FAF4EC; --card:#FFFFFF;
  --ink:#1A1A1A; --muted:#6B6562; --line:#ECDFD3;
  --green:#2E9E5B; --amber:#E5A52B;
}
html, body, [class*="css"]{ font-family:'Inter',sans-serif !important; }
.stApp{ background:var(--cream); }
.block-container{ padding-top:3rem; padding-bottom:3rem; max-width:1200px; }
[data-testid="stHeader"]{ background:transparent !important; }
[data-testid="stToolbar"]{ right:1rem; }
#MainMenu, footer{ visibility:hidden; }

/* ---------- SIDEBAR ---------- */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,var(--red) 0%, var(--red-dark) 100%);
}
[data-testid="stSidebar"] *{ color:#fff !important; }
.sb-brand{ padding:6px 4px 24px; border-bottom:1px solid rgba(255,255,255,.15); margin-bottom:18px; }
.sb-brand .name{ font-weight:800; font-size:20px; letter-spacing:-.5px; }
.sb-brand .tag{ font-size:10px; opacity:.75; letter-spacing:2px; text-transform:uppercase; margin-top:2px; }
.sb-card{ background:rgba(255,255,255,.10); border-radius:12px; padding:14px 16px;
  margin-bottom:8px; transition:.25s; animation:fadeUp .5s ease both; }
.sb-card:hover{ background:rgba(255,255,255,.20); transform:translateX(3px); }
.sb-card .l{ font-size:9px; text-transform:uppercase; letter-spacing:1.5px; opacity:.75; margin-bottom:3px; }
.sb-card .v{ font-size:14px; font-weight:600; line-height:1.3; }
.sb-note{ border:1px dashed rgba(255,255,255,.35); border-radius:12px;
  padding:12px 14px; font-size:11px; line-height:1.5; margin-top:14px; opacity:.85; }

/* ---------- HERO ---------- */
.hero{ animation:fadeUp .6s ease both; }
.hero h1{ font-size:46px; font-weight:800; line-height:1.05; color:var(--ink);
  margin:0; letter-spacing:-1.5px; }
.hero h1 .accent{ color:var(--red); position:relative; }
.hero h1 .accent::after{ content:''; position:absolute; left:0; right:0; bottom:-4px;
  height:3px; background:var(--red); border-radius:2px;
  transform:scaleX(0); transform-origin:left;
  animation:underline .8s .4s cubic-bezier(.2,.8,.2,1) forwards; }
.hero .sub{ font-size:15px; color:var(--muted); margin-top:10px; letter-spacing:.2px; }
.hero hr{ border:none; border-top:1px solid var(--line); margin:26px 0; }
.hero .lead{ font-size:15px; color:#3a3534; max-width:780px; line-height:1.6; }
.hero .lead b{ color:var(--red); font-weight:600; }

/* ---------- FORM ---------- */
[data-testid="stForm"]{
  background:var(--card); border:1px solid var(--line); border-radius:24px;
  padding:34px 36px; box-shadow:0 24px 60px rgba(150,90,60,.08);
  animation:fadeUp .7s ease both;
}
label{ font-weight:500 !important; color:var(--ink) !important; font-size:13px !important; }
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input{
  background:#fff !important; color:var(--ink) !important;
  border:1.5px solid var(--line) !important; border-radius:10px !important;
  transition:border-color .2s, box-shadow .2s; }
[data-testid="stTextInput"] input:focus,[data-testid="stNumberInput"] input:focus{
  border-color:var(--red) !important; box-shadow:0 0 0 3px var(--red-light) !important; }
[data-testid="stNumberInput"] button{
  background:#fbf3ea !important; color:var(--red) !important; border:none !important; }
[data-baseweb="select"]>div{
  background:#fff !important; border:1.5px solid var(--line) !important; border-radius:10px !important; }
[data-baseweb="select"] *{ color:var(--ink) !important; }
[data-testid="stCheckbox"] *{ color:var(--ink) !important; }
[data-testid="stWidgetLabel"] p{ color:var(--ink) !important; }
.stSlider [data-baseweb="slider"] [role="slider"]{ background:var(--red) !important; }

[data-testid="stFormSubmitButton"] button{
  background:linear-gradient(135deg,var(--red),var(--red-dark));
  color:#fff !important; border:none; border-radius:12px;
  padding:14px 36px; font-weight:600; font-size:15px; letter-spacing:.3px;
  box-shadow:0 10px 26px rgba(200,16,46,.30); transition:.25s; }
[data-testid="stFormSubmitButton"] button:hover{
  transform:translateY(-2px); box-shadow:0 16px 34px rgba(200,16,46,.42); }
[data-testid="stFormSubmitButton"] button:active{ transform:translateY(0); }

/* ---------- HASIL ---------- */
.result{
  background:var(--card); border:1px solid var(--line); border-radius:24px;
  padding:34px 36px; margin-top:24px;
  box-shadow:0 24px 60px rgba(150,90,60,.10);
  animation:pop .55s cubic-bezier(.2,.9,.3,1.2) both;
}
.r-tag{ display:inline-block; font-size:10px; text-transform:uppercase; letter-spacing:2.5px;
  color:var(--muted); margin-bottom:10px; font-weight:600; }
.r-class{ font-size:48px; font-weight:800; line-height:1.05; letter-spacing:-1.5px; margin:2px 0 6px; }
.r-conf{ font-size:15px; color:var(--muted); }
.r-conf b{ color:var(--ink); font-weight:700; }

.section{ font-size:10px; text-transform:uppercase; letter-spacing:2.5px;
  color:var(--muted); margin:28px 0 14px; font-weight:600; }

/* Kartu metric (persentase 3 kelas) */
.mrow{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-top:20px; }
.metric{ background:#fdf8f2; border-radius:16px; padding:18px 20px;
  border:1px solid var(--line); transition:.3s;
  animation:fadeUp .6s ease both; position:relative; overflow:hidden; }
.metric::before{ content:''; position:absolute; left:0; top:0; bottom:0; width:4px; background:var(--c); }
.metric:hover{ transform:translateY(-4px); box-shadow:0 14px 30px rgba(0,0,0,.07); }
.metric .l{ font-size:10px; text-transform:uppercase; letter-spacing:1.5px; color:var(--muted); font-weight:600; }
.metric .v{ font-size:30px; font-weight:800; color:var(--c); margin-top:4px; letter-spacing:-1px;
  font-variant-numeric:tabular-nums; }
.metric.win{ background:linear-gradient(135deg,#fff,#fdf8f2); border:1.5px solid var(--c); }
.metric.win::after{ content:'TERPILIH'; position:absolute; top:10px; right:10px;
  font-size:8px; letter-spacing:1.5px; color:var(--c); font-weight:700;
  background:rgba(255,255,255,.6); padding:3px 7px; border-radius:6px; }

/* Bar grafik animasi */
.bar-row{ margin:16px 0; }
.bar-top{ display:flex; justify-content:space-between; font-size:13px;
  font-weight:600; color:var(--ink); margin-bottom:7px; }
.bar-top .pct{ font-variant-numeric:tabular-nums; color:var(--c); }
.bar-track{ height:12px; background:#f4ece2; border-radius:8px; overflow:hidden; }
.bar-fill{ height:100%; border-radius:8px; width:0; background:var(--c);
  animation:grow 1.2s cubic-bezier(.2,.8,.2,1) forwards; position:relative; }
.bar-fill::after{ content:''; position:absolute; inset:0;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.35),transparent);
  animation:shine 2.2s ease-in-out infinite; }

/* Analisis */
.analysis{ background:#fdf8f2; border-left:3px solid var(--red);
  border-radius:10px; padding:18px 22px; font-size:14px;
  line-height:1.75; color:#3a3534; animation:fadeUp .7s .2s ease both; }
.analysis b{ color:var(--ink); font-weight:600; }
.analysis .pill{ display:inline-block; padding:2px 10px; border-radius:20px;
  background:var(--red-light); color:var(--red); font-weight:600; font-size:12px;
  margin:0 2px; }

/* Ringkasan input */
.inputs{ display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; }
.chip{ background:#fbf3ea; border:1px solid var(--line); border-radius:20px;
  padding:6px 14px; font-size:12px; color:var(--ink); }
.chip b{ color:var(--red); font-weight:600; margin-left:4px; }

/* ---------- ANIMASI ---------- */
@keyframes fadeUp{ from{opacity:0;transform:translateY(20px);} to{opacity:1;transform:none;} }
@keyframes pop{ from{opacity:0;transform:scale(.95);} to{opacity:1;transform:scale(1);} }
@keyframes grow{ to{ width:var(--w); } }
@keyframes shine{ 0%{transform:translateX(-100%);} 60%,100%{transform:translateX(200%);} }
@keyframes underline{ to{ transform:scaleX(1); } }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <div class="name">GameSentiment</div>
        <div class="tag">ML Sentiment Analyzer</div>
    </div>
    <div class="sb-card"><div class="l">Algoritma</div><div class="v">Gradient Boosting</div></div>
    <div class="sb-card"><div class="l">Tuning</div><div class="v">GridSearchCV</div></div>
    <div class="sb-card"><div class="l">Akurasi Test</div><div class="v">66.3%</div></div>
    <div class="sb-card"><div class="l">F1 Macro</div><div class="v">0.57</div></div>
    <div class="sb-card"><div class="l">Imbalance Handler</div><div class="v">SMOTE Oversampling</div></div>
    <div class="sb-card"><div class="l">Fitur Terpenting</div><div class="v">Umur game & jumlah review</div></div>
    <div class="sb-note">Kolom "% positif" sengaja tidak dipakai sebagai fitur untuk mencegah <i>data leakage</i>.</div>
    """, unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero">
    <h1>Prediksi Sentimen<br>Review Game <span class="accent">Steam</span></h1>
    <div class="sub">Tugas Besar Machine Learning — Klasifikasi 3 tier sentimen review</div>
    <hr>
    <div class="lead">Masukkan karakteristik sebuah game, model akan memprediksi tingkat
    sentimen review-nya: <b>Mixed/Negatif</b>, <b>Positif</b>, atau <b>Sangat Positif</b>.</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# FORM
# ============================================================
with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        nama = st.text_input("Nama game", "Contoh Game")
        is_free = st.checkbox("Game gratis (Free)?", value=False)
        harga = st.number_input("Harga asli (Rp)", min_value=0, value=200000,
                                step=10000, disabled=is_free)
        diskon = st.slider("Besar diskon (%)", 0, 100, 0)
    with col2:
        reviews_count = st.number_input("Jumlah review", min_value=0, value=10000, step=1000)
        tahun = st.number_input("Tahun rilis", min_value=2006, max_value=2026, value=2022)
        kategori = st.selectbox("Kategori Steam",
                                ["topsellers", "mostplayed", "newreleases", "upcomingreleases"])
    submit = st.form_submit_button("Prediksi Sentimen")

# ============================================================
# PREDIKSI + OUTPUT KAYA (metric, grafik, analisis)
# ============================================================
if submit:
    orig = 0.0 if is_free else float(harga)
    disc = orig * (1 - diskon / 100.0)
    age_days = max((date(2026, 5, 28) - date(int(tahun), 1, 1)).days, 0)
    age_years = age_days // 365
    row = {
        "orig_price": orig, "disc_price": disc, "disc_pct": float(diskon),
        "Reviews Count": float(reviews_count), "game_age_days": float(age_days),
        "is_free": int(is_free), "has_discount": int(diskon > 0), "name_len": float(len(nama)),
        "filter_mostplayed": int(kategori == "mostplayed"),
        "filter_newreleases": int(kategori == "newreleases"),
        "filter_topsellers": int(kategori == "topsellers"),
        "filter_upcomingreleases": int(kategori == "upcomingreleases"),
    }
    X = pd.DataFrame([row])[FEATURES]
    pred = int(model.predict(X)[0])
    proba = model.predict_proba(X)[0]
    predicted = LABELS[pred]
    confidence = proba[pred] * 100

    color_map = {"Mixed/Negatif": "#C8102E", "Positif": "#E5A52B", "Sangat Positif": "#2E9E5B"}

    # =================== ANALISIS OTOMATIS ===================
    harga_str = "gratis" if is_free else f"Rp {orig:,.0f}".replace(",", ".")
    rev_pos_ratio = {0: "rendah", 1: "menengah", 2: "tinggi"}[
        0 if reviews_count < 5000 else (1 if reviews_count < 50000 else 2)
    ]
    umur_kat = {0: "baru", 1: "matang", 2: "klasik"}[
        0 if age_years < 2 else (1 if age_years < 8 else 2)
    ]

    if predicted == "Sangat Positif":
        analysis = (
            f"Model memprediksi game <b>{nama}</b> akan menerima review "
            f"<b style='color:#2E9E5B;'>Sangat Positif</b> dengan keyakinan <b>{confidence:.1f}%</b>. "
            f"<br><br><b>Faktor pendukung:</b> game ini tergolong <b>{umur_kat}</b> "
            f"(umur {age_years} tahun) dengan jumlah review <b>{rev_pos_ratio}</b> "
            f"({reviews_count:,} review). Karakteristik ini mirip dengan pola game-game terbaik "
            f"di Steam — game yang sudah lama beredar dan punya basis pemain besar cenderung "
            f"mengumpulkan sentimen yang kokoh karena komunitasnya matang dan banyak yang "
            f"merekomendasikan secara aktif. "
            f"<br><br><b>Konteks dataset:</b> kelas 'Sangat Positif' adalah kelas mayoritas (~65% data) "
            f"dengan rata-rata rating 88–96% positif. "
            f"<br><br><b>Catatan:</b> model hanya memakai metadata game (harga, umur, popularitas) — "
            f"kualitas konten dan genre tidak dianalisis, jadi hasil ini perlu divalidasi dengan "
            f"review sebenarnya."
        )
    elif predicted == "Positif":
        analysis = (
            f"Model memprediksi game <b>{nama}</b> akan diterima dengan sentimen "
            f"<b style='color:#E5A52B;'>Positif</b> dengan keyakinan <b>{confidence:.1f}%</b>. "
            f"<br><br><b>Faktor pendukung:</b> game ini berstatus <b>{umur_kat}</b> "
            f"(umur {age_years} tahun) dengan popularitas <b>{rev_pos_ratio}</b> "
            f"({reviews_count:,} review). Posisi ini ada di zona menengah — game diperkirakan "
            f"disukai pemain namun belum mencapai 'Sangat Positif'. Bisa karena belum cukup waktu "
            f"untuk membangun reputasi, atau punya beberapa kekurangan teknis yang membuat "
            f"sebagian pemain memberi review netral. "
            f"<br><br><b>Konteks dataset:</b> kelas 'Positif' adalah kelas minoritas (sekitar 21% data), "
            f"jadi prediksi ini relatif jarang. "
            f"<br><br><b>Catatan:</b> untuk naik ke 'Sangat Positif', biasanya butuh peningkatan "
            f"jumlah review aktif dan rekomendasi positif dari komunitas seiring waktu."
        )
    else:
        analysis = (
            f"Model memprediksi game <b>{nama}</b> akan menerima sentimen "
            f"<b style='color:#C8102E;'>Mixed atau Negatif</b> dengan keyakinan <b>{confidence:.1f}%</b>. "
            f"<br><br><b>Faktor pendukung:</b> kombinasi karakteristik game — usia <b>{umur_kat}</b> "
            f"({age_years} tahun), popularitas <b>{rev_pos_ratio}</b> ({reviews_count:,} review), "
            f"di kategori <b>{kategori}</b> — mirip dengan pola game ber-review campuran. Hal ini bisa "
            f"dipicu oleh game yang masih terlalu baru sehingga reputasinya belum terbangun, popularitas "
            f"yang masih rendah, atau pasar kategori tersebut yang relatif lebih kritis. "
            f"<br><br><b>Konteks dataset:</b> kelas 'Mixed/Negatif' mencakup ~14% data, dengan "
            f"rating positif rata-rata di bawah 60%. "
            f"<br><br><b>Catatan:</b> prediksi negatif tidak selalu berarti game-nya jelek — model "
            f"hanya membaca metadata, bukan kualitas gameplay atau cerita."
        )

    # =================== KARTU HASIL PREDIKSI ===================
    color = color_map[predicted]
    badge_html = (
        '<div style="background:#FFFFFF;border:1px solid #ECDFD3;border-radius:20px;'
        'padding:26px 30px;margin-top:18px;box-shadow:0 18px 44px rgba(150,90,60,.10);'
        'animation:pop .55s cubic-bezier(.2,.9,.3,1.2) both;">'
        '<div style="font-size:10px;text-transform:uppercase;letter-spacing:2.5px;'
        'color:#6B6562;font-weight:600;margin-bottom:6px;">Hasil Prediksi</div>'
        f'<div style="font-size:46px;font-weight:800;color:{color};letter-spacing:-1.5px;'
        f'line-height:1.1;">{predicted}</div>'
        f'<div style="font-size:15px;color:#6B6562;margin-top:8px;">Keyakinan model: '
        f'<b style="color:#1A1A1A;">{confidence:.1f}%</b></div>'
        '</div>'
    )
    st.markdown(badge_html, unsafe_allow_html=True)

    # =================== GRAFIK PROBABILITAS (NATIVE) ===================
    st.markdown("### Probabilitas tiap kelas")
    prob_df = pd.DataFrame({"Sentimen": LABELS, "Probabilitas": proba})
    st.bar_chart(prob_df.set_index("Sentimen"), height=340, color="#C8102E")

    # =================== TABEL PROBABILITAS ===================
    st.dataframe(
        prob_df.style.format({"Probabilitas": "{:.1%}"}),
        use_container_width=True,
        hide_index=True,
    )

    # =================== ANALISIS ===================
    st.markdown("### Analisis")
    analysis_html = (
        '<div style="background:#fdf8f2;border-left:4px solid #C8102E;border-radius:10px;'
        'padding:20px 24px;font-size:14px;line-height:1.75;color:#3a3534;'
        'animation:fadeUp .7s .2s ease both;">'
        f'{analysis}'
        '</div>'
    )
    st.markdown(analysis_html, unsafe_allow_html=True)