
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
<style>
.pred {text-align:center;padding:5px 8px;border-radius:14px;font-weight:700;font-size:.78rem;margin-top:4px}
.pred.high{background:#ff4f65;color:white}.pred.mid{background:#ffbd38;color:#241900}.pred.low{background:#27d79a;color:#06291e}
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

def severity(v):
    return "Rendah" if v < .35 else "Sedang" if v < .65 else "Parah"

def detail(k, v, evidence_items):
    base = INDICATORS[k]["label"]
    if not evidence_items:
        return base + " Belum ada bukti kalimat yang cukup kuat."
    strongest = max(evidence_items, key=lambda x: x["weight"])
    if k == "Achievement Exposure":
        return f"Kalimat menunjukkan paparan terhadap pencapaian/keberhasilan pihak lain, terutama pada: “{strongest['text']}”"
    if k == "Future Uncertainty":
        return f"Kalimat memuat ketidakpastian atau kekhawatiran mengenai masa depan: “{strongest['text']}”"
    if k == "Negative Self-Evaluation":
        return f"Kalimat mengandung evaluasi atau keraguan terhadap kemampuan diri: “{strongest['text']}”"
    if k == "Perceived Lagging":
        return f"Kalimat menunjukkan kesan belum mencapai sesuatu atau merasa tertinggal: “{strongest['text']}”"
    return f"Kalimat menunjukkan perbandingan kondisi diri dengan orang lain: “{strongest['text']}”"

# ---------- Result ----------
if st.session_state.saed_result:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    a,b=st.columns([1,2])
    with a:
        fig=go.Figure(go.Pie(values=[overall,100-overall], hole=.76, textinfo="none",
                             marker=dict(colors=["#20cfff","#1a2a58"])))
        fig.update_layout(height=230, margin=dict(l=0,r=0,t=0,b=0), showlegend=False,
                          paper_bgcolor="rgba(0,0,0,0)",
                          annotations=[dict(text=f"<b>{overall}%</b><br>{level}",
                          x=.5,y=.5,font=dict(size=20,color="white"),showarrow=False)])
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
    with b:
        st.markdown("### 📊 Hasil Analisis")
        st.markdown(f"**Pola dominan:** <span class='badge'>{peak}</span>", unsafe_allow_html=True)
        st.write(f"Skor keseluruhan menunjukkan tingkat **{level.lower()}** berdasarkan gabungan lima indikator.")
        if links:
            for x in links:
                st.caption("• " + x)
        st.caption("Catatan: SAED adalah prototipe analisis bahasa, bukan alat diagnosis psikologis.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Chart ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📊 Ringkasan Indikator")
    st.caption("Semakin tinggi skor, semakin kuat indikasi polanya.")
    fig=go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=list(scores.values()),
        text=[f"{v:.2f}" for v in scores.values()],
        textposition="outside", marker_color=colors
    ))
    fig.update_yaxes(range=[0,1.15], dtick=.2)
    fig.update_layout(height=390, margin=dict(l=20,r=20,t=25,b=95),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_color="#dbe6ff", showlegend=False)
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    # Predicates under the chart, matching the reference style.
    pc = st.columns(5)
    for i, (k,v) in enumerate(scores.items()):
        sev = severity(v)
        with pc[i]:
            cls = "high" if sev=="Parah" else ("mid" if sev=="Sedang" else "low")
            st.markdown(f"<div class='pred {cls}'>{sev}</div>", unsafe_allow_html=True)
    st.markdown("### ☷ Detail Indikator")
    cols=st.columns(2)
    for i,(k,v) in enumerate(scores.items()):
        with cols[i%2]:
            sev=severity(v)
            icon = "🔴" if sev=="Parah" else ("🟠" if sev=="Sedang" else "🟢")
            st.markdown(
                f"""<div class="insight"><b>{icon} {k}</b>
                <span style="float:right"><b>{sev}</b> · {v:.2f}</span>
                <br><span class="small">{detail(k,v,evidence.get(k,[]))}</span></div>""",
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Sentence evidence ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🧠 Bukti Kalimat & Pola Paragraf")
    st.caption("Bagian ini menunjukkan kalimat yang membuat indikator aktif dan membantu menjelaskan mengapa skornya berbeda.")
    for k,v in scores.items():
        if evidence.get(k):
            sev=severity(v)
            st.markdown(f"**{k} — {sev} ({v:.2f})**")
            for item in evidence[k][:3]:
                matches=", ".join(item["matches"][:5])
                st.markdown(f"> **Kalimat {item['sentence']}:** {item['text']}")
                st.caption(f"Terpicu oleh: {matches}")
        else:
            st.caption(f"• {k}: belum ada bukti kalimat yang kuat.")
    if links:
        st.markdown("**Pola paragraf:**")
        for x in links:
            st.write("• " + x)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Deep analysis ----------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔍 Analisis Mendalam")
    top_two = sorted(scores.items(), key=lambda x:x[1], reverse=True)[:2]
    if top_two and top_two[0][1] > 0:
        st.markdown(f"<div class='insight'><b>🔵 Pola utama</b><br>{top_two[0][0]} menjadi indikator paling kuat dengan skor {top_two[0][1]:.2f}.</div>", unsafe_allow_html=True)
        if len(top_two) > 1 and top_two[1][1] >= .35:
            st.markdown(f"<div class='insight'><b>🟠 Pola pendamping</b><br>{top_two[1][0]} juga muncul dan dapat memperkuat konteks indikator utama.</div>", unsafe_allow_html=True)
    if any("tidak" in norm(x) or "belum" in norm(x) for x in sentences):
        st.markdown("<div class='insight'><b>🧩 Negasi</b><br>Teks mengandung kata negasi seperti “tidak” atau “belum”, sehingga konteks kalimat diperhitungkan agar tidak hanya menghitung kata kunci.</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Recommendations ----------
    def make_recommendations(scores, evidence, sentences):
        recs=[]
        joined=" ".join(sentences).lower()

        def add(x):
            if x not in recs: recs.append(x)

        active=sorted([(k,v) for k,v in scores.items() if v>=.35], key=lambda x:x[1], reverse=True)

        # Per-indicator recommendations, personalized by actual evidence.
        for k,v in active:
            e
