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
.tip { background:linear-gradient(135deg,#073b3d,#123c3d 55%,#173b65); border:1px solid #0aa69b; border-radius:18px; padding:18px; box-shadow:0 10px 30px rgba(0,0,0,.18); }
.suggestion { border-radius:14px; padding:12px 14px; margin:8px 0; border:1px solid rgba(255,255,255,.10); background:linear-gradient(90deg,rgba(15,34,70,.95),rgba(13,24,52,.95)); }
.suggestion .tag { display:inline-block; border-radius:12px; padding:3px 8px; font-size:.72rem; font-weight:800; margin-right:7px; }
.tag-blue{background:#214bd6;color:#dce6ff}.tag-orange{background:#a95d10;color:#fff0cf}.tag-pink{background:#a92870;color:#ffe4f3}.tag-purple{background:#5c38a8;color:#efe5ff}.tag-cyan{background:#087f93;color:#d9fbff}.tag-green{background:#087b63;color:#d8fff2}
.detail-card{border-radius:17px;padding:15px 16px;margin:8px 0;background:linear-gradient(145deg,#101f49,#0b1531);border:1px solid #263d73;box-shadow:0 8px 24px rgba(0,0,0,.15)}
.evidence-chip{display:inline-block;margin:4px 4px 0 0;padding:4px 8px;border-radius:10px;background:#182d5e;color:#b9d5ff;font-size:.76rem}
.score-pill{float:right;padding:4px 9px;border-radius:12px;font-size:.75rem;font-weight:800}
.ind-icon{display:inline-flex;align-items:center;justify-content:center;width:42px;height:42px;border-radius:13px;margin-right:7px;vertical-align:middle;background:linear-gradient(145deg,rgba(255,255,255,.10),rgba(255,255,255,.03));border:1px solid rgba(255,255,255,.14);box-shadow:inset 0 0 18px rgba(255,255,255,.04),0 5px 18px rgba(0,0,0,.20);position:relative;overflow:hidden}
.ind-icon:before{content:"";position:absolute;inset:1px;border-radius:12px;background:radial-gradient(circle at 30% 20%,rgba(255,255,255,.18),transparent 48%);pointer-events:none}
.ind-icon svg{width:27px;height:27px;filter:drop-shadow(0 0 5px currentColor);position:relative;z-index:1}
.icon-blue{color:#35c9ff;border-color:#247dff66;background:linear-gradient(145deg,#153a86,#091d49)}
.icon-orange{color:#ffc04d;border-color:#ffad3266;background:linear-gradient(145deg,#714016,#281b10)}
.icon-pink{color:#ff62b0;border-color:#f2388366;background:linear-gradient(145deg,#711b58,#28132d)}
.icon-purple{color:#9a74ff;border-color:#7446f566;background:linear-gradient(145deg,#432a8e,#1b1642)}
.icon-cyan{color:#36e1df;border-color:#22c4ca66;background:linear-gradient(145deg,#125d70,#10263e)}
.detail-card .ind-icon{width:36px;height:36px;border-radius:11px}
.detail-card .ind-icon svg{width:23px;height:23px}
@media(max-width:700px){.ind-icon{width:38px;height:38px;border-radius:12px}.ind-icon svg{width:24px;height:24px}}


</style>
<style>
.pred {text-align:center;padding:5px 8px;border-radius:14px;font-weight:700;font-size:.78rem;margin-top:4px}
.pred.high{background:linear-gradient(135deg,#ff416c,#ff6b35);color:white;box-shadow:0 4px 14px rgba(255,65,108,.28)}.pred.mid{background:linear-gradient(135deg,#ffc107,#ff8f00);color:#241900;box-shadow:0 4px 14px rgba(255,170,0,.24)}.pred.low{background:linear-gradient(135deg,#18d89f,#18b7d8);color:#04251e;box-shadow:0 4px 14px rgba(24,216,159,.22)}
@media(max-width:700px){
 .block-container{padding-left:.7rem!important;padding-right:.7rem!important;padding-top:.8rem!important}
 .card{padding:15px!important;border-radius:16px!important}
 .insight{padding:12px!important}
}
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
    st.caption("© 2026 SAED • Prototype v2.2 • Futuristic Icons")

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
                    height=130, max_chars=1000, label_visibility="collapsed", key="saed_text")
c1, c2 = st.columns([4,1])
analyze = c1.button("🔎  ANALISIS TEKS  ›", use_container_width=True, type="primary", key="saed_analyze")
reset = c2.button("↻  Reset", use_container_width=True, key="saed_reset")
st.caption(f"{len(text)}/1000")
st.markdown('</div>', unsafe_allow_html=True)

if reset:
    st.rerun()


# ---------- NLP sentence + paragraph engine ----------
INDICATORS = {
    "Achievement Exposure": {
        "label": "Paparan terhadap pencapaian orang lain.",
        "keywords": ["sukses", "berhasil", "prestasi", "gaji", "jabatan", "lulus", "menang",
                     "pencapaian", "karier", "pekerjaan bagus", "teman", "orang lain",
                     "linkedin", "instagram", "media sosial"],
        "phrases": [
            (["teman", "sukses"], .35), (["orang lain", "berhasil"], .35),
            (["melihat", "pencapaian"], .30), (["melihat", "sukses"], .30),
            (["media sosial", "sukses"], .35), (["instagram", "sukses"], .35)
        ]
    },
    "Future Uncertainty": {
        "label": "Kekhawatiran atau ketidakpastian mengenai masa depan.",
        "keywords": ["takut", "khawatir", "cemas", "masa depan", "besok", "nanti",
                     "gagal", "tidak yakin", "bingung", "waswas", "gelisah",
                     "tidak tahu", "belum tahu", "karier ke depan"],
        "phrases": [
            (["takut", "masa depan"], .45), (["khawatir", "masa depan"], .45),
            (["cemas", "gagal"], .40), (["tidak yakin", "masa depan"], .45),
            (["bingung", "karier"], .40), (["tidak tahu", "masa depan"], .40)
        ]
    },
    "Negative Self-Evaluation": {
        "label": "Penilaian negatif atau keraguan terhadap diri sendiri.",
        "keywords": ["tidak mampu", "tidak cukup", "kurang", "jelek", "bodoh",
                     "gagal", "rendah diri", "tidak pintar", "tidak berbakat",
                     "tidak berguna", "lemah", "buruk", "saya gagal", "aku gagal"],
        "phrases": [
            (["saya", "gagal"], .40), (["aku", "gagal"], .40),
            (["tidak", "mampu"], .40), (["tidak", "cukup"], .35),
            (["merasa", "tidak mampu"], .45), (["merasa", "kurang"], .35)
        ]
    },
    "Perceived Lagging": {
        "label": "Perasaan tertinggal dari target atau ritme orang lain.",
        "keywords": ["tertinggal", "ketinggalan", "belum punya", "belum berhasil",
                     "telat", "terlambat", "lambat", "belum mencapai", "belum dapat",
                     "belum sukses", "masih di sini", "seharusnya sudah"],
        "phrases": [
            (["merasa", "tertinggal"], .50), (["belum", "sukses"], .40),
            (["seharusnya", "sudah"], .45), (["teman", "sedangkan", "saya"], .50),
            (["mereka", "sudah", "saya", "belum"], .55)
        ]
    },
    "Social Comparison": {
        "label": "Kecenderungan membandingkan kondisi diri dengan orang lain.",
        "keywords": ["dibanding", "bandingkan", "mereka lebih", "dia lebih",
                     "lebih sukses", "lebih maju", "seumuran", "teman sebaya",
                     "sementara mereka", "sedangkan mereka", "orang lain"],
        "phrases": [
            (["dibanding", "saya"], .40), (["mereka", "lebih"], .40),
            (["teman", "lebih"], .40), (["seumuran", "sudah"], .45),
            (["sementara", "mereka"], .45), (["sedangkan", "mereka"], .45)
        ]
    }
}

NEGATIONS = {"tidak", "bukan", "belum", "jangan", "tanpa", "bukanlah"}
INTENSIFIERS = {"sangat": .14, "terlalu": .14, "selalu": .12, "sering": .10,
                "benar-benar": .12, "begitu": .08, "banget": .10, "terus": .08}
EMOTION_WORDS = {"takut", "khawatir", "cemas", "gelisah", "waswas", "tertekan", "sedih", "malu"}

def split_sentences(text):
    # Keep Indonesian punctuation and avoid requiring external NLP packages.
    chunks = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
    return [re.sub(r'\s+', ' ', x).strip() for x in chunks if x.strip()]

def norm(x):
    return re.sub(r'[^a-z0-9\s]', ' ', x.lower())

def token_set(x):
    return set(norm(x).split())

def phrase_present(sentence, phrase_words):
    low = norm(sentence)
    # For multi-word expressions, use phrase text when possible.
    phrase = " ".join(phrase_words)
    if phrase in low:
        return True
    toks = token_set(sentence)
    return all(w in toks for w in phrase_words)

def analyze_text(text):
    sentences = split_sentences(text)
    if not sentences:
        return ({k: 0.0 for k in INDICATORS}, {k: [] for k in INDICATORS},
                0, "Rendah", "Belum dianalisis", [], [])

    evidence = {k: [] for k in INDICATORS}
    raw_scores = {k: 0.0 for k in INDICATORS}

    for idx, sentence in enumerate(sentences, 1):
        low = norm(sentence)
        toks = token_set(sentence)
        for ind, spec in INDICATORS.items():
            matched = []
            weight = 0.0

            # Exact keywords / phrases.
            for kw in spec["keywords"]:
                if kw in low:
                    matched.append(kw)
                    weight += .14 if " " in kw else .11

            for words, bonus in spec["phrases"]:
                if phrase_present(sentence, words):
                    weight += bonus
                    matched.append(" ".join(words))

            # Contextual intensifiers increase strength, but only if an indicator signal exists.
            if matched:
                for word, bonus in INTENSIFIERS.items():
                    if word in toks:
                        weight += bonus

            # Negation is contextual: "tidak merasa tertinggal" should not be treated
            # like a direct "merasa tertinggal".
            if matched and "tidak" in toks:
                # Reduce only when the indicator phrase is negated in the same sentence.
                negated_targets = ["tertinggal", "khawatir", "cemas", "takut", "gagal",
                                   "kurang", "tidak mampu", "tidak cukup"]
                if any(t in low for t in negated_targets):
                    weight *= .55

            if matched:
                unique = list(dict.fromkeys(matched))
                evidence[ind].append({
                    "sentence": idx,
                    "text": sentence,
                    "matches": unique,
                    "weight": min(weight, .95)
                })
                raw_scores[ind] += min(weight, .95)

    # Paragraph-level reinforcement: repeated evidence across multiple sentences.
    for ind in INDICATORS:
        count = len(evidence[ind])
        if count >= 2:
            raw_scores[ind] += .12
        if count >= 3:
            raw_scores[ind] += .10

    # Cross-indicator contextual patterns.
    joined = " ".join(sentences).lower()
    if any(evidence["Achievement Exposure"]) and any(evidence["Social Comparison"]):
        raw_scores["Social Comparison"] += .12
    if any(evidence["Social Comparison"]) and any(evidence["Perceived Lagging"]):
        raw_scores["Perceived Lagging"] += .12
    if any(evidence["Future Uncertainty"]) and any(evidence["Negative Self-Evaluation"]):
        raw_scores["Future Uncertainty"] += .08
        raw_scores["Negative Self-Evaluation"] += .08

    scores = {k: round(min(1.0, v), 2) for k, v in raw_scores.items()}

    # If text has no indicator evidence, return genuinely low scores instead of inventing a high baseline.
    if not any(evidence.values()):
        scores = {k: 0.0 for k in INDICATORS}

    overall = round(sum(scores.values()) / len(scores) * 100)
    peak = max(scores, key=scores.get) if any(scores.values()) else "Belum dianalisis"
    level = "Rendah" if overall < 35 else "Sedang" if overall < 65 else "Parah"

    # Paragraph/context links for the UI.
    links = []
    active = [k for k,v in scores.items() if v >= .35]
    if len(active) >= 2:
        links.append("Beberapa indikator muncul bersamaan sehingga konteks antar-kalimat ikut diperhitungkan.")
    if len(sentences) >= 3:
        links.append(f"Teks terdiri dari {len(sentences)} kalimat; pola yang berulang diberi bobot tambahan.")
    if any(len(evidence[k]) >= 2 for k in evidence):
        links.append("Ada indikator yang muncul di lebih dari satu kalimat.")

    return scores, evidence, overall, level, peak, sentences, links

# ---------- Session state ----------
if "saed_result" not in st.session_state:
    st.session_state.saed_result = None

if reset:
    st.session_state.saed_result = None
    st.session_state.saed_text = ""
    st.rerun()

if analyze:
    current = st.session_state.get("saed_text", text).strip()
    if not current:
        st.warning("⚠️ Masukkan teks terlebih dahulu.")
        st.session_state.saed_result = None
    else:
        st.session_state.saed_result = analyze_text(current)
        st.success("✅ Teks berhasil dianalisis. Indikator, bukti kalimat, dan saran diperbarui.")

if st.session_state.saed_result:
    scores, evidence, overall, level, peak, sentences, links = st.session_state.saed_result
else:
    scores = {k: 0.0 for k in INDICATORS}
    evidence = {k: [] for k in INDICATORS}
    overall, level, peak, sentences, links = 0, "Rendah", "Belum dianalisis", [], []

labels=list(scores.keys())
colors=["#20a9ff","#ffae32","#22c4ca","#7446f5","#f23883"]
IND_ICON = {
    "Achievement Exposure": """<span class='ind-icon icon-blue'><svg viewBox='0 0 48 48' aria-hidden='true'><path d='M15 9h18v6h5v3c0 6-4 10-10 11-1 4-4 6-7 7-3-1-6-3-7-7-6-1-10-5-10-11v-3h5z' fill='none' stroke='currentColor' stroke-width='2.6'/><path d='M19 39h10M24 36v-7M12 15H7v2c0 4 3 7 8 8M36 15h5v2c0 4-3 7-8 8' fill='none' stroke='currentColor' stroke-width='2.6' stroke-linecap='round'/><path d='M20 19l4-2 4 2-4 2z' fill='currentColor'/><circle cx='24' cy='14' r='2' fill='none' stroke='currentColor' stroke-width='1.8'/></svg></span>""",
    "Future Uncertainty": """<span class='ind-icon icon-orange'><svg viewBox='0 0 48 48' aria-hidden='true'><circle cx='24' cy='24' r='15' fill='none' stroke='currentColor' stroke-width='2.6'/><path d='M24 9v-4M39 24h4M24 39v4M9 24H5' stroke='currentColor' stroke-width='2.2' stroke-linecap='round'/><path d='M24 16v8l6 4' fill='none' stroke='currentColor' stroke-width='2.6' stroke-linecap='round'/><path d='M17 18l3-3M31 18l3-3' stroke='currentColor' stroke-width='2' stroke-linecap='round'/><circle cx='24' cy='24' r='2.4' fill='currentColor'/></svg></span>""",
    "Negative Self-Evaluation": """<span class='ind-icon icon-pink'><svg viewBox='0 0 48 48' aria-hidden='true'><rect x='9' y='7' width='30' height='34' rx='8' fill='none' stroke='currentColor' stroke-width='2.6'/><circle cx='24' cy='20' r='6' fill='none' stroke='currentColor' stroke-width='2.2'/><path d='M15 35c2-6 16-6 18 0M19 19h1M28 19h1M20 23c2 2 6 2 8 0' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round'/><path d='M13 11l-3-3M35 11l3-3' stroke='currentColor' stroke-width='2' stroke-linecap='round'/></svg></span>""",
    "Perceived Lagging": """<span class='ind-icon icon-purple'><svg viewBox='0 0 48 48' aria-hidden='true'><circle cx='24' cy='24' r='16' fill='none' stroke='currentColor' stroke-width='2.6'/><path d='M24 14v11l7 4' fill='none' stroke='currentColor' stroke-width='2.8' stroke-linecap='round'/><path d='M10 38l-4 4M38 38l4 4M7 24H3M45 24h-4' stroke='currentColor' stroke-width='2.2' stroke-linecap='round'/><path d='M18 8l-2-4M30 8l2-4' stroke='currentColor' stroke-width='2' stroke-linecap='round'/></svg></span>""",
    "Social Comparison": """<span class='ind-icon icon-cyan'><svg viewBox='0 0 48 48' aria-hidden='true'><circle cx='17' cy='17' r='5' fill='none' stroke='currentColor' stroke-width='2.5'/><circle cx='31' cy='17' r='5' fill='none' stroke='currentColor' stroke-width='2.5'/><path d='M8 35c1-7 5-11 9-11s8 4 9 11M22 35c1-7 5-11 9-11s8 4 9 11' fill='none' stroke='currentColor' stroke-width='2.5' stroke-linecap='round'/><path d='M21 17h6M20 14l-3 3 3 3M28 14l3 3-3 3' fill='none' stroke='currentColor' stroke-width='2.1' stroke-linecap='round' stroke-linejoin='round'/><circle cx='24' cy='9' r='2' fill='currentColor'/></svg></span>"""
}
IND_TAG={"Achievement Exposure":"blue","Future Uncertainty":"orange","Negative Self-Evaluation":"pink","Perceived Lagging":"purple","Social Comparison":"cyan"}
IND_SHORT={"Achievement Exposure":"Paparan pencapaian orang lain","Future Uncertainty":"Ketidakpastian masa depan","Negative Self-Evaluation":"Penilaian terhadap diri","Perceived Lagging":"Rasa tertinggal","Social Comparison":"Perbandingan sosial"}

def severity(v):
    return "Rendah" if v < .35 else "Sedang" if v < .65 else "Parah"

def detail(k, v, evidence_items):
    base = INDICATORS[k]["label"]
    if not evidence_items:
        return base + " Belum ada bukti kalimat yang cukup kuat."
    strongest = max(evidence_items, key=lambda x: x["weight"])
    if k == "Achievement Exposure":
        return f"Kalimat menunjukkan paparan"
