import re
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="SAED — Social Achievement Exposure Detector",
                   page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp { background: radial-gradient(circle at 80% 0%, #101d4d 0%, #050a1d 42%, #020513 100%); color:#eef3ff; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg,#07102d,#030817); border-right:1px solid #182957; }
.block-container { max-width: 1250px; padding-top: 1.4rem; }
.card { background: linear-gradient(145deg,rgba(17,29,66,.92),rgba(8,15,37,.94)); border:1px solid #203467; border-radius:20px; padding:22px; margin-bottom:16px; box-shadow:0 10px 35px rgba(0,0,0,.22); }
.hero { border-radius:20px; padding:18px 22px; background:linear-gradient(100deg,#101c46,#111a3d); border:1px solid #253b75; }
.badge { display:inline-block; padding:7px 14px; border-radius:18px; background:#123d78; color:#52cfff; font-weight:700; }
.small { color:#9ba9c9; font-size:.88rem; }
h1,h2,h3 { color:#f7f9ff !important; }
div[data-testid="stTextArea"] textarea { background:#0c1532 !important; color:#edf2ff !important; border:1px solid #2c4173 !important; border-radius:15px !important; }
.stButton > button { border-radius:12px; font-weight:700; min-height:46px; }
div[data-testid="stMetric"] { background:#0d1735; border:1px solid #213665; padding:12px; border-radius:14px; }
.insight { background:#0c1836; border:1px solid #223968; border-radius:15px; padding:14px 16px; margin:8px 0; }
.tip { background:linear-gradient(90deg,#073b3d,#123c3d); border:1px solid #087f79; border-radius:18px; padding:18px; }
</style>
""", unsafe_allow_html=True)

# ---------- Brain logo ----------
brain_svg = """<svg width="74" height="74" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#20d9ff"/><stop offset="1" stop-color="#693cff"/></linearGradient></defs>
<path d="M46 20c-12-10-27-1-25 12-12 4-12 22-2 27-4 13 9 24 20 17 4 12 18 11 21 2V22c-4-4-9-4-14-2z" fill="none" stroke="url(#g)" stroke-width="7" stroke-linecap="round"/>
<path d="M54 20c12-10 27-1 25 12 12 4 12 22 2 27 4 13-9 24-20 17-4 12-18 11-21 2V22c4-4 9-4 14-2z" fill="none" stroke="url(#g)" stroke-width="7" stroke-linecap="round"/>
<path d="M50 17v66M31 35c7 2 10 7 8 13M69 35c-7 2-10 7-8 13M31 57c6-1 10 2 10 8M69 57c-6-1-10 2-10 8" fill="none" stroke="#39cfff" stroke-width="4" stroke-linecap="round"/>
</svg>"""

with st.sidebar:
    st.markdown(brain_svg, unsafe_allow_html=True)
    st.markdown("## SAED")
    st.caption("Social Achievement Exposure Detector")
    st.markdown("---")
    st.markdown("### 🏠 Dashboard")
    st.markdown("📊 Analisis")
    st.markdown("🕘 Riwayat Analisis")
    st.markdown("💡 Rekomendasi")
    st.markdown("ℹ️ Tentang SAED")
    st.markdown("---")
    st.info("SAED adalah prototipe NLP untuk membaca pola bahasa terkait pencapaian sosial, perbandingan diri, kekhawatiran masa depan, dan evaluasi diri.")
    st.caption("© 2026 SAED • Prototype v1.0")

st.markdown(f"""
<div class="hero">
<div style="display:flex;align-items:center;gap:14px">{brain_svg}
<div><h1 style="margin:0">SAED</h1><div class="small">Social Achievement Exposure Detector</div></div>
<div style="margin-left:auto" class="badge">✦ Prototype NLP</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ---------- Input ----------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📝 Masukkan teks yang ingin dianalisis")
text = st.text_area("", placeholder="Tulis teks di sini... (misalnya keluhan, curhatan, atau opini)",
                    height=130, max_chars=1000, label_visibility="collapsed")
c1, c2 = st.columns([4,1])
analyze = c1.button("🔎  ANALISIS TEKS  ›", use_container_width=True, type="primary")
reset = c2.button("↻  Reset", use_container_width=True)
st.caption(f"{len(text)}/1000")
st.markdown('</div>', unsafe_allow_html=True)

if reset:
    st.rerun()

# ---------- NLP detector: contextual Indonesian pattern engine ----------
# ---------- Robust Indonesian pattern detector ----------
# Detector ini sengaja tidak bergantung pada satu kalimat/pola regex panjang.
# Ia memakai kombinasi kata kunci, frasa, hubungan "diri vs orang lain",
# konteks waktu, serta negasi sederhana.

SELF_WORDS = [
    "aku", "saya", "gue", "gua", "gw", "diriku", "diri saya", "hidup saya",
    "hidupku", "kemampuan saya", "kemampuan aku"
]
OTHER_WORDS = [
    "teman", "teman-teman", "mereka", "dia", "orang lain", "orang-orang",
    "rekan", "kenalan", "seumuran", "sebaya", "teman sebaya"
]
SUCCESS_WORDS = [
    "sukses", "berhasil", "prestasi", "pencapaian", "lulus", "diterima kerja",
    "dapat kerja", "dapat pekerjaan", "naik jabatan", "promosi", "gaji besar",
    "penghasilan", "menang", "juara", "wisuda", "menikah", "punya rumah",
    "punya mobil", "punya bisnis", "buka usaha", "karier bagus", "mapan",
    "mendapat pekerjaan", "mendapat kerja", "diterima kuliah", "masuk kampus"
]
EXPOSURE_WORDS = [
    "melihat", "lihat", "melihat postingan", "postingan", "posting",
    "instagram", "tiktok", "linkedin", "media sosial", "sosmed",
    "mendengar", "dengar", "mengetahui", "tahu", "melihat kabar",
    "melihat story", "story", "feed"
]
COMPARISON_WORDS = [
    "dibanding", "dibandingkan", "perbandingan", "bandingkan",
    "berbeda dengan", "tidak seperti", "seperti mereka", "kayak mereka",
    "seperti teman", "kayak teman", "lebih rendah", "lebih tinggi",
    "lebih sukses", "lebih maju", "lebih kaya", "lebih baik",
    "kalah", "selevel", "setara", "sama seperti", "sementara",
    "sedangkan", "kok mereka", "kenapa mereka", "kenapa aku",
    "kenapa saya", "kapan aku", "kapan saya"
]
LAG_WORDS = [
    "tertinggal", "ketinggalan", "terlambat", "belum mencapai",
    "belum punya", "belum berhasil", "belum dapat", "belum mendapatkan",
    "belum kerja", "belum bekerja", "belum lulus", "belum menikah",
    "belum mapan", "belum sukses", "jalan di tempat", "stuck",
    "tidak berkembang", "nggak berkembang", "gak berkembang",
    "teman sudah", "mereka sudah", "orang lain sudah"
]
FUTURE_WORDS = [
    "masa depan", "ke depan", "nanti", "besok", "tahun depan",
    "karier", "karir", "pekerjaan", "hidup saya ke depan", "hidupku ke depan",
    "akan", "rencana", "tujuan", "arah hidup"
]
UNCERTAINTY_WORDS = [
    "takut", "khawatir", "cemas", "bingung", "ragu", "tidak yakin",
    "nggak yakin", "gak yakin", "tidak tahu", "nggak tahu", "gak tahu",
    "belum tahu", "entah", "was-was", "kepikiran", "takut gagal",
    "takut tidak", "takut nggak", "takut gak"
]
NEGATIVE_SELF_WORDS = [
    "gagal", "bodoh", "payah", "buruk", "jelek", "tidak mampu",
    "nggak mampu", "gak mampu", "tidak cukup", "nggak cukup",
    "gak cukup", "tidak berguna", "nggak berguna", "gak berguna",
    "tidak layak", "nggak layak", "gak layak", "rendah diri",
    "tidak pintar", "nggak pintar", "gak pintar", "tidak bagus",
    "nggak bagus", "gak bagus", "mengecewakan", "tidak berharga",
    "nggak berharga", "gak berharga", "payah banget", "aku gagal",
    "saya gagal", "gue gagal", "aku bodoh", "saya bodoh", "aku payah",
    "saya payah"
]
NEGATION_WORDS = [
    "tidak", "tak", "bukan", "belum", "nggak", "gak", "ga", "gak pernah",
    "nggak pernah", "tidak pernah"
]
CONTRAST = re.compile(r"\b(tetapi|namun|sedangkan|sementara|walaupun|meskipun)\b")
CAUSAL = re.compile(r"\b(karena|sehingga|akibatnya|setelah|gara-gara|membuat|menyebabkan)\b")

INDICATORS = {
    "Achievement Exposure": {
        "label": "Paparan terhadap pencapaian pihak lain.",
        "primary": [OTHER_WORDS, SUCCESS_WORDS],
        "support": [EXPOSURE_WORDS]
    },
    "Social Comparison": {
        "label": "Perbandingan eksplisit atau implisit antara diri dan pihak lain.",
        "primary": [SELF_WORDS, OTHER_WORDS],
        "support": [COMPARISON_WORDS]
    },
    "Perceived Lagging": {
        "label": "Persepsi bahwa perkembangan diri tertinggal dari target atau kelompok pembanding.",
        "primary": [LAG_WORDS],
        "support": [SELF_WORDS, OTHER_WORDS, SUCCESS_WORDS]
    },
    "Future Uncertainty": {
        "label": "Ketidakpastian atau kekhawatiran yang diarahkan ke masa depan.",
        "primary": [UNCERTAINTY_WORDS],
        "support": [FUTURE_WORDS]
    },
    "Negative Self-Evaluation": {
        "label": "Evaluasi negatif yang diarahkan kepada diri sendiri.",
        "primary": [NEGATIVE_SELF_WORDS],
        "support": [SELF_WORDS]
    }
}

def _contains_phrase(text, phrase):
    # Phrase matching dengan batas kata agar "gagal" tidak match ke kata lain.
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text) is not None

def _token_positions(text, phrase):
    return [m.start() for m in re.finditer(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text)]

def _is_negated(text, pos, lookback=45):
    before = text[max(0, pos-lookback):pos]
    # Negasi sangat dekat dengan kata target -> abaikan sebagai bukti positif.
    return any(_contains_phrase(before, n) for n in NEGATION_WORDS)

def _hit_phrases(text, phrases, ignore_negation=False):
    hits = []
    for phrase in phrases:
        for pos in _token_positions(text, phrase):
            if ignore_negation or not _is_negated(text, pos):
                hits.append(phrase)
                break
    return hits

def _has_any(text, phrases):
    return any(_contains_phrase(text, p) for p in phrases)

def _distance_match(text, group_a, group_b, window=90):
    apos = []
    bpos = []
    for p in group_a:
        apos.extend(_token_positions(text, p))
    for p in group_b:
        bpos.extend(_token_positions(text, p))
    return any(abs(a-b) <= window for a in apos for b in bpos)

def _evidence_sentences(sentences, phrases, limit=3):
    found = []
    for i, sent in enumerate(sentences):
        if any(_contains_phrase(sent, p) for p in phrases):
            found.append((i+1, sent))
            if len(found) >= limit:
                break
    return found

def split_sentences(text):
    text = re.sub(r"\s+", " ", text.strip())
    # Teks pendek tanpa tanda baca tetap dianggap satu kalimat.
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+|[\n]+", text) if x.strip()]

def normalize(text):
    text = text.lower()
    text = text.replace("’", "'")
    text = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s.!?']", " ", text)
    text = text.replace("-", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def contextual_links(sentences):
    links = []
    for i in range(len(sentences) - 1):
        pair = sentences[i] + " " + sentences[i+1]
        if (
            _distance_match(pair, SELF_WORDS, OTHER_WORDS, 110)
            or CONTRAST.search(pair)
            or CAUSAL.search(pair)
        ):
            links.append((i+1, i+2, pair))
    return links

def score_indicator(name, sentences, links):
    joined = " ".join(sentences)
    if not joined:
        return 0.0, []

    evidence_phrases = []
    score = 0.0

    if name == "Achievement Exposure":
        other_success = _distance_match(joined, OTHER_WORDS, SUCCESS_WORDS, 120)
        exposure_other = _distance_match(joined, EXPOSURE_WORDS, OTHER_WORDS, 120)
        exposure_success = _distance_match(joined, EXPOSURE_WORDS, SUCCESS_WORDS, 150)

        if other_success:
            score += 0.50
            evidence_phrases += _hit_phrases(joined, OTHER_WORDS, ignore_negation=True)
            evidence_phrases += _hit_phrases(joined, SUCCESS_WORDS, ignore_negation=True)
        if exposure_other:
            score += 0.25
            evidence_phrases += _hit_phrases(joined, EXPOSURE_WORDS, ignore_negation=True)
        if exposure_success:
            score += 0.15
            evidence_phrases += _hit_phrases(joined, EXPOSURE_WORDS, ignore_negation=True)

    elif name == "Social Comparison":
        self_other = _distance_match(joined, SELF_WORDS, OTHER_WORDS, 120)
        comparison = _hit_phrases(joined, COMPARISON_WORDS)
        comparative = bool(re.search(r"\b(lebih|kurang|kalah|seperti|kayak|dibanding)\b", joined))
        contrast = bool(CONTRAST.search(joined))

        if self_other:
            score += 0.35
            evidence_phrases += _hit_phrases(joined, SELF_WORDS, ignore_negation=True)
            evidence_phrases += _hit_phrases(joined, OTHER_WORDS, ignore_negation=True)
        if comparison:
            score += min(0.45, 0.18 * len(comparison))
            evidence_phrases += comparison
        if comparative:
            score += 0.10
        if contrast and self_other:
            score += 0.08

    elif name == "Perceived Lagging":
        lag = _hit_phrases(joined, LAG_WORDS, ignore_negation=True)
        self_present = _has_any(joined, SELF_WORDS)
        others_success = _distance_match(joined, OTHER_WORDS, SUCCESS_WORDS, 120)
        self_not_yet = _distance_match(
            joined, SELF_WORDS,
            ["belum", "masih", "belum bisa", "belum punya", "belum dapat"],
            75
        )

        if lag:
            score += min(0.65, 0.32 * len(lag))
            evidence_phrases += lag
        if self_present and lag:
            score += 0.10
            evidence_phrases += _hit_phrases(joined, SELF_WORDS, ignore_negation=True)
        if others_success and self_not_yet:
            score += 0.25
            evidence_phrases += _hit_phrases(joined, OTHER_WORDS, ignore_negation=True)
            evidence_phrases += _hit_phrases(joined, SUCCESS_WORDS, ignore_negation=True)

    elif name == "Future Uncertainty":
        uncertainty = _hit_phrases(joined, UNCERTAINTY_WORDS)
        future = _hit_phrases(joined, FUTURE_WORDS, ignore_negation=True)
        question_future = bool(
            re.search(r"\b(kapan|bagaimana|gimana|entah)\b", joined)
        ) and bool(future)
        self_present = _has_any(joined, SELF_WORDS)

        if uncertainty:
            score += min(0.62, 0.28 * len(uncertainty))
            evidence_phrases += uncertainty
        if future:
            score += 0.22
            evidence_phrases += future
        if question_future:
            score += 0.10
        if self_present and uncertainty:
            score += 0.06
            evidence_phrases += _hit_phrases(joined, SELF_WORDS, ignore_negation=True)

    else:  # Negative Self-Evaluation
        negative = _hit_phrases(joined, NEGATIVE_SELF_WORDS)
        self_negative = _distance_match(joined, SELF_WORDS, NEGATIVE_SELF_WORDS, 85)

        if self_negative:
            score += 0.68
            evidence_phrases += _hit_phrases(joined, SELF_WORDS, ignore_negation=True)
            evidence_phrases += negative
        elif negative and _has_any(joined, SELF_WORDS):
            score += 0.50
            evidence_phrases += negative
        elif negative:
            score += 0.20
            evidence_phrases += negative

    evidence_phrases = list(dict.fromkeys(evidence_phrases))
    evidence = _evidence_sentences(sentences, evidence_phrases) if evidence_phrases else []

    if evidence and links:
        score += min(0.08, 0.03 * len(links))

    return round(min(score, 1.0), 2), evidence

def analyze_text(t):
    clean = normalize(t)
    sentences = split_sentences(clean)
    links = contextual_links(sentences)
    scores, evidence = {}, {}
    for name in INDICATORS:
        scores[name], evidence[name] = score_indicator(name, sentences, links)

    ranked = sorted(scores.values(), reverse=True)
    # Overall menekankan indikator terkuat agar satu pola yang jelas tidak
    # "tenggelam" karena indikator lain memang tidak relevan.
    if ranked and ranked[0] > 0:
        overall_score = ranked[0] * 0.70 + (ranked[1] if len(ranked) > 1 else 0) * 0.30
        overall = round(overall_score * 100)
    else:
        overall = 0
    total = sum(scores.values())
    peak = max(scores, key=scores.get) if total else "Belum terdeteksi"
    level = "Rendah" if overall < 35 else "Sedang" if overall < 65 else "Tinggi"
    return scores, evidence, overall, level, peak, sentences, links

if analyze and text.strip():
    scores, evidence, overall, level, peak, sentences, links = analyze_text(text)
else:
    scores = {k: 0.0 for k in INDICATORS}
    evidence = {k: [] for k in INDICATORS}
    overall, level, peak, sentences, links = 0, "Belum dianalisis", "Belum dianalisis", [], []

labels = list(scores.keys())
colors = ["#20a9ff","#ffae32","#22c4ca","#7446f5","#f23883"]

def severity(v):
    return "Rendah" if v < .35 else "Sedang" if v < .65 else "Tinggi"

def detail(k, v):
    return INDICATORS[k]["label"]

# ---------- Result ----------
st.markdown('<div class="card">', unsafe_allow_html=True)
a,b=st.columns([1,2])
with a:
    fig=go.Figure(go.Pie(values=[overall,100-overall], hole=.76, textinfo="none",
                         marker=dict(colors=["#20cfff","#1a2a58"])))
    fig.update_layout(height=230, margin=dict(l=0,r=0,t=0,b=0), showlegend=False,
                      paper_bgcolor="rgba(0,0,0,0)", annotations=[dict(text=f"<b>{overall}%</b><br>{level}",
                      x=.5,y=.5,font=dict(size=20,color="white"),showarrow=False)])
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
with b:
    st.markdown("### 📊 Hasil Analisis")
    detected_count = sum(1 for v in scores.values() if v >= 0.35)
    st.markdown(f"Pola yang terdeteksi: <span class='badge'>{peak}</span>",unsafe_allow_html=True)
    st.caption(f"{detected_count} dari {len(scores)} indikator melewati ambang deteksi 35%.")
    if peak=="Belum dianalisis":
        desc="Masukkan teks lalu tekan **ANALISIS TEKS**. Detector akan mencari kombinasi konteks, bukan hanya satu kata."
    elif peak=="Achievement Exposure":
        desc="Teks menyebut paparan terhadap pencapaian pihak lain. Ini berbeda dari Social Comparison: paparan saja belum berarti pengguna membandingkan dirinya dengan orang lain."
    else:
        desc=f"Teks paling kuat menunjukkan pola **{peak}** berdasarkan frasa yang terdeteksi. Indikasi harus dibaca bersama konteks kalimat, bukan dianggap sebagai diagnosis."
    st.write(desc)
    st.caption("Catatan: SAED adalah prototipe analisis bahasa, bukan alat diagnosis psikologis.")
st.markdown('</div>', unsafe_allow_html=True)

# ---------- Chart ----------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📊 Ringkasan Indikator")
st.caption("Semakin tinggi skor, semakin kuat indikasi pola pada teks.")
fig=go.Figure()
percent_values = [round(v * 100) for v in scores.values()]
fig.add_trace(go.Bar(x=labels,y=percent_values,text=[f"{v}%" for v in percent_values],
                     textposition="outside",marker_color=colors))
fig.update_yaxes(range=[0,105],dtick=20,ticksuffix="%")
fig.update_layout(height=370,margin=dict(l=20,r=20,t=30,b=90),paper_bgcolor="rgba(0,0,0,0)",
                  plot_bgcolor="rgba(0,0,0,0)",font_color="#dbe6ff",showlegend=False)
st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})


st.markdown("### 🎯 Persentase Indikator")
gcols = st.columns(len(scores))
for gcol, (glabel, gvalue) in zip(gcols, scores.items()):
    with gcol:
        gpct = int(round(gvalue * 100))
        gauge_fig = go.Figure(go.Pie(
            values=[gpct, 100-gpct],
            hole=0.78,
            textinfo="none",
            marker=dict(colors=["#20cfff", "#182a58"]),
            sort=False,
            direction="clockwise",
            rotation=270
        ))
        gauge_fig.update_layout(
            height=180,
            margin=dict(l=5,r=5,t=5,b=5),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(
                text=f"<b>{gpct}%</b><br><span style='font-size:10px'>{glabel}</span>",
                x=0.5, y=0.5, showarrow=False,
                font)]
