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
    st.caption("© 2026 SAED • Prototype v1.5")

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
text = st.text_area(
    "",
    placeholder="Tulis teks di sini... (misalnya: Teman-teman saya sudah banyak yang sukses. Saya merasa tertinggal dan khawatir tidak akan bisa menyusul mereka.)",
    height=150,
    max_chars=1000,
    label_visibility="collapsed",
    key="saed_text"
)
c1, c2 = st.columns([4,1])
analyze = c1.button(
    "🔎  ANALISIS TEKS  ›",
    use_container_width=True,
    type="primary",
    key="saed_analyze_button"
)
reset = c2.button("↻  Reset", use_container_width=True, key="saed_reset_button")
st.caption(f"{len(text)}/1000")
st.markdown('</div>', unsafe_allow_html=True)

# ---------- NLP engine v14: multi-signal sentence + paragraph analysis ----------
# Rule-based prototype: membaca hubungan kata, kalimat, negasi, kontras,
# sebab-akibat, intensifier, dan pola antar-kalimat. Bukan diagnosis psikologis.

INDICATORS = {
    "Achievement Exposure": {
        "label": "Paparan terhadap pencapaian, keberhasilan, status, atau keunggulan pihak lain.",
        "patterns": [
            r"\b(teman|orang lain|mereka|dia|lawan|rekan|kenalan)\b.{0,140}\b(sudah|telah|punya|memiliki|mendapat|berhasil|sukses|menang|lulus|diterima|naik jabatan|berpengalaman|lebih maju|lebih hebat|lebih unggul)\b",
            r"\b(saya|aku)\b.{0,120}\b(melihat|lihat|menonton|mendengar|mengetahui|tahu|menyadari|melihat postingan|melihat pencapaian)\b.{0,140}\b(teman|orang lain|mereka|dia)\b",
            r"\b(postingan|unggahan|story|status|linkedin|instagram|media sosial)\b.{0,120}\b(sukses|lulus|wisuda|kerja|jabatan|prestasi|menang|penghasilan|pencapaian)\b"
        ],
        "phrases": [
            "teman saya sudah","orang lain sudah","teman saya berhasil","teman saya punya",
            "orang lain berhasil","melihat pencapaian orang lain","melihat postingan teman"
        ]
    },
    "Social Comparison": {
        "label": "Perbandingan eksplisit atau implisit antara diri dengan pihak lain.",
        "patterns": [
            r"\b(dibanding|dibandingkan|di banding|berbeda dengan|kalah dari|lebih rendah dari|tidak sebaik|tidak seperti|daripada)\b.{0,120}\b(saya|aku|diriku|diri saya|teman|mereka|dia|orang lain|lawan)\b",
            r"\b(saya|aku)\b.{0,100}\b(dibanding|dibandingkan|di banding|berbeda dengan|kalah dari|daripada)\b",
            r"\b(teman|mereka|dia|orang lain|lawan)\b.{0,100}\b(lebih berpengalaman|lebih sukses|lebih maju|lebih baik|lebih mampu|lebih hebat|lebih cepat|lebih pintar|lebih kaya)\b.{0,100}\b(saya|aku)\b",
            r"\b(saya|aku)\b.{0,100}\b(seperti|kayak|sama seperti|selevel dengan|setara dengan)\b.{0,100}\b(teman|mereka|dia|orang lain)\b",
            r"\b(kenapa|mengapa)\b.{0,120}\b(mereka|dia|teman|orang lain)\b.{0,100}\b(sudah|bisa|mampu|berhasil)\b.{0,100}\b(saya|aku)\b"
        ],
        "phrases": [
            "dibanding saya","dibandingkan dengan saya","lebih berpengalaman dari saya",
            "lebih sukses dari saya","lebih maju dari saya","seperti teman saya","kalah dari mereka"
        ]
    },
    "Perceived Lagging": {
        "label": "Perasaan tertinggal, terlambat, belum mencapai tahap tertentu, atau berada di belakang timeline orang lain.",
        "patterns": [
            r"\b(saya|aku)\b.{0,100}\b(tertinggal|ketinggalan|terlambat|belum sampai|belum mencapai|belum punya|belum bisa|masih belum|masih tertinggal|telat)\b",
            r"\b(teman|mereka|dia|orang lain)\b.{0,120}\b(sudah|telah|lebih dulu|lebih cepat)\b.{0,120}\b(saya|aku)\b",
            r"\b(umur|usia)\b.{0,100}\b(sudah|telah|seharusnya)\b.{0,120}\b(saya|aku|teman|mereka)\b",
            r"\b(umur|usia)\b.{0,80}\b(25|26|27|28|29|30|31|32|33|34|35)\b.{0,120}\b(belum|masih)\b.{0,120}\b(kerja|lulus|menikah|punya|mencapai|sukses|mapan)\b",
            r"\b(kapan|kapan ya)\b.{0,100}\b(bisa|mampu|punya|memiliki|mencapai)\b.{0,100}\b(seperti|kayak|selevel)\b.{0,100}\b(teman|mereka|dia|orang lain)\b"
        ],
        "phrases": [
            "tertinggal","ketinggalan","masih tertinggal","belum bisa","masih belum",
            "belum mencapai","belum punya","kapan ya bisa seperti"
        ]
    },
    "Future Uncertainty": {
        "label": "Kekhawatiran, keraguan, pertanyaan kemungkinan, atau ketidakpastian mengenai masa depan/hasil.",
        "patterns": [
            r"\b(saya|aku)\b.{0,120}\b(khawatir|cemas|takut|ragu|bingung|waswas|gelisah)\b.{0,180}\b(akan|bisa|mampu|nanti|ke depan|masa depan|suatu hari|berhasil|menang|gagal|mencapai|mendapat|punya|memiliki)\b",
            r"\b(khawatir|cemas|takut|waswas|ragu)\b.{0,120}\b(tidak|nggak|gak|belum|mungkin tidak)\b.{0,120}\b(bisa|mampu|berhasil|menang|mencapai|mendapat|punya|memiliki|sempat)\b",
            r"\b(kapan|kapan ya|kapan kira.?kira|entah kapan)\b.{0,160}\b(bisa|mampu|akan|mendapat|mencapai|punya|memiliki|berhasil|terjadi|tercapai)\b",
            r"\b(belum tahu|tidak tahu|nggak tahu|gak tahu|entah|tidak yakin|nggak yakin|gak yakin|belum yakin|masih ragu)\b.{0,180}\b(akan|bisa|mampu|nanti|ke depan|masa depan|berhasil|menang|gagal|mencapai|mendapat|punya|memiliki|terjadi)\b",
            r"\b(apakah|akankah|bisakah|mungkinkah)\b.{0,180}\b(saya|aku|kita)\b.{0,120}\b(bisa|mampu|berhasil|menang|mencapai|mendapat|punya|memiliki)\b",
            r"\b(saya|aku)\b.{0,120}\b(mungkin|kemungkinan|takutnya|jangan.?jangan)\b.{0,160}\b(gagal|kalah|tidak bisa|tidak mampu|tidak berhasil|tidak tercapai|tidak mendapat)\b"
        ],
        "phrases": [
            "saya khawatir","aku khawatir","saya takut","aku takut","saya cemas","aku cemas",
            "saya ragu","aku ragu","kapan ya bisa","belum tahu","tidak yakin","belum yakin",
            "masih ragu","apakah saya bisa","bisakah saya","mungkinkah saya","takutnya saya","jangan-jangan saya"
        ]
    },
    "Negative Self-Evaluation": {
        "label": "Penilaian negatif yang diarahkan langsung kepada nilai, kemampuan, atau kelayakan diri.",
        "patterns": [
            r"\b(saya|aku|diriku|diri saya)\b.{0,100}\b(gagal|bodoh|buruk|tidak mampu|nggak mampu|gak mampu|tidak cukup|tidak berguna|tidak layak|payah|jelek|rendah diri|tidak pintar|tidak hebat|tidak kompeten)\b",
            r"\b(saya|aku)\b.{0,100}\b(merasa|menganggap|menilai|melihat diri)\b.{0,100}\b(gagal|tidak mampu|tidak cukup|tidak layak|tidak berguna|buruk|payah|tidak pintar)\b",
            r"\b(saya|aku)\b.{0,100}\b(bukan siapa-siapa|tidak ada gunanya|tidak punya kemampuan|tidak punya masa depan)\b"
        ],
        "phrases": [
            "saya gagal","aku gagal","saya bodoh","saya tidak mampu","saya tidak cukup",
            "saya tidak layak","saya payah","saya tidak pintar","saya tidak kompeten"
        ]
    }
}

CONTRAST = re.compile(r"\b(tetapi|namun|sedangkan|sementara|walaupun|meskipun|padahal|hanya saja)\b")
CAUSE = re.compile(r"\b(karena|sehingga|akibatnya|setelah|gara-gara|membuat|menyebabkan|oleh karena)\b")
SELF = re.compile(r"\b(aku|saya|diriku|diri saya)\b")
OTHER = re.compile(r"\b(teman|mereka|dia|orang lain|lawan|rekan|kenalan)\b")
WORRY = re.compile(r"\b(khawatir|cemas|takut|ragu|bingung|waswas|gelisah)\b")
NEGATIVE_SELF = re.compile(r"\b(tidak mampu|nggak mampu|gak mampu|tidak cukup|tidak berguna|tidak layak|gagal|bodoh|buruk|payah|tidak pintar|tidak kompeten)\b")
NEGATION = re.compile(r"\b(tidak|tak|bukan|belum|nggak|gak|jangan)\b")
INTENSIFIER = re.compile(r"\b(sangat|banget|sekali|terlalu|benar-benar|benar benar|begitu|makin|semakin)\b")
UNCERTAINTY = re.compile(r"\b(mungkin|mungkin saja|kemungkinan|entah|belum tahu|tidak yakin|nggak yakin|gak yakin|masih ragu|kapan|apakah|akankah|bisakah|mungkinkah)\b")

def normalize(text):
    text = text.lower().replace("di banding", "dibanding")
    return re.sub(r"\s+", " ", re.sub(r"[^a-zA-ZÀ-ÿ0-9\s.!?,]", " ", text)).strip()

def split_sentences(text):
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+|[\n]+", text) if x.strip()]

def find_evidence(sentences, patterns):
    found = []
    for i, sent in enumerate(sentences, 1):
        if any(re.search(p, sent) for p in patterns):
            found.append((i, sent))
    return found

def sentence_signal(sent):
    return {
        "self": bool(SELF.search(sent)),
        "other": bool(OTHER.search(sent)),
        "worry": bool(WORRY.search(sent)),
        "negative_self": bool(NEGATIVE_SELF.search(sent)),
        "uncertainty": bool(UNCERTAINTY.search(sent)),
        "contrast": bool(CONTRAST.search(sent)),
        "cause": bool(CAUSE.search(sent)),
        "negation": bool(NEGATION.search(sent)),
        "intensifier": bool(INTENSIFIER.search(sent)),
    }

def context_links(sentences):
    links = []
    for i in range(len(sentences)-1):
        a, b = sentences[i], sentences[i+1]
        pair = a + " " + b
        sa, sb = sentence_signal(a), sentence_signal(b)
        reasons = []
        if (sa["self"] and sb["other"]) or (sa["other"] and sb["self"]):
            reasons.append("diri ↔ pihak lain")
        if sa["worry"] or sb["worry"]:
            reasons.append("emosi ↔ konteks")
        if CONTRAST.search(pair):
            reasons.append("kontras")
        if CAUSE.search(pair):
            reasons.append("sebab-akibat")
        if sa["uncertainty"] or sb["uncertainty"]:
            reasons.append("ketidakpastian")
        if reasons:
            links.append((i+1, i+2, ", ".join(dict.fromkeys(reasons))))
    return links

def negation_penalty(sent):
    # Negasi dekat dengan indikator menurunkan skor agar "tidak takut" tidak
    # dibaca sama seperti "takut". Tidak dimaksudkan sebagai parser bahasa penuh.
    return 0.18 if re.search(r"\b(tidak|tak|bukan|jangan|nggak|gak)\b.{0,35}\b(khawatir|cemas|takut|tertinggal|gagal|bodoh|membandingkan)\b", sent) else 0

def score_indicator(name, sentences, full_text, links):
    cfg = INDICATORS[name]
    evidence = find_evidence(sentences, cfg["patterns"])
    phrase_hits = [p for p in cfg["phrases"] if p in full_text]

    if phrase_hits and not evidence:
        evidence = [(i, sent) for i, sent in enumerate(sentences, 1)
                    if any(p in sent for p in phrase_hits)]

    score = 0.0
    if evidence:
        score += min(0.58, 0.30 + 0.09 * len(evidence))
    if phrase_hits:
        score += min(0.16, 0.04 * len(phrase_hits))

    related_links = 0
    for x, y, reason in links:
        if name == "Social Comparison" and "diri ↔ pihak lain" in reason:
            related_links += 1
        elif name == "Perceived Lagging" and "diri ↔ pihak lain" in reason:
            related_links += 1
        elif name == "Future Uncertainty" and ("ketidakpastian" in reason or "emosi ↔ konteks" in reason):
            related_links += 1
        elif name == "Negative Self-Evaluation" and ("emosi ↔ konteks" in reason or "sebab-akibat" in reason):
            related_links += 1
        elif name == "Achievement Exposure" and "diri ↔ pihak lain" in reason:
            related_links += 1
    score += min(0.14, 0.035 * related_links)

    # Penguatan berbasis kombinasi sinyal, bukan keyword tunggal.
    if name == "Achievement Exposure":
        if OTHER.search(full_text) and re.search(r"\b(sudah|telah|berhasil|sukses|menang|lulus|diterima|prestasi|jabatan|penghasilan|pencapaian)\b", full_text):
            score += 0.16

    if name == "Social Comparison":
        if SELF.search(full_text) and OTHER.search(full_text):
            if re.search(r"\b(dibanding|dibandingkan|lebih|kalah|seperti|daripada|berbeda)\b", full_text):
                score += 0.22
        if len(sentences) >= 2 and any(SELF.search(s) for s in sentences) and any(OTHER.search(s) for s in sentences):
            score += 0.08

    if name == "Perceived Lagging":
        if SELF.search(full_text) and OTHER.search(full_text) and re.search(r"\b(lebih|sudah|belum|tertinggal|ketinggalan|kapan|terlambat)\b", full_text):
            score += 0.22
        if re.search(r"\b(seharusnya|umur|usia|telat|terlambat)\b", full_text) and re.search(r"\b(belum|masih)\b", full_text):
            score += 0.14

    if name == "Future Uncertainty":
        if WORRY.search(full_text):
            score += 0.22
        if UNCERTAINTY.search(full_text):
            score += 0.18
        if re.search(r"\b(tidak bisa|tidak mampu|gagal|kalah|tidak berhasil|tidak tercapai|belum bisa|belum mampu)\b", full_text):
            score += 0.14
        if WORRY.search(full_text) and re.search(r"\b(tidak|nggak|gak|belum|gagal|mungkin)\b", full_text):
            score += 0.12

    if name == "Negative Self-Evaluation":
        if NEGATIVE_SELF.search(full_text) and SELF.search(full_text):
            score += 0.24
        if re.search(r"\b(merasa|menganggap|menilai|diri)\b", full_text) and NEGATIVE_SELF.search(full_text):
            score += 0.12
        if re.search(r"\b(tidak bisa menang|tidak mampu menang|takut kalah)\b", full_text) and not re.search(r"\b(saya|aku)\b.{0,50}\b(gagal|bodoh|payah|tidak mampu|tidak cukup)\b", full_text):
            score = min(score, 0.22)

    # Kurangi skor bila kalimat secara eksplisit menyangkal sinyal.
    if evidence:
        penalty = sum(negation_penalty(s) for _, s in evidence)
        score -= min(0.25, penalty)

    # Intensifier memperkuat sinyal yang memang sudah punya bukti.
    if evidence and INTENSIFIER.search(full_text):
        score += 0.05

    return round(max(0.0, min(score, 1.0)), 2), list(dict.fromkeys(evidence))

def analyze_text(text):
    full = normalize(text)
    sentences = split_sentences(full)
    links = context_links(sentences)
    scores, evidence = {}, {}
    for name in INDICATORS:
        scores[name], evidence[name] = score_indicator(name, sentences, full, links)
    overall = round(sum(scores.values()) / len(scores) * 100)
    peak = max(scores, key=scores.get) if any(scores.values()) else "Belum terdeteksi"
    level = "Rendah" if overall < 35 else "Sedang" if overall < 65 else "Tinggi"
    return scores, evidence, overall, level, peak, sentences, links

# Persist analysis so the result does not disappear after Streamlit reruns.
if "saed_result" not in st.session_state:
    st.session_state.saed_result = None
if "saed_last_text" not in st.session_state:
    st.session_state.saed_last_text = ""

if reset:
    st.session_state.saed_result = None
    st.session_state.saed_last_text = ""
    st.session_state.saed_text = ""
    st.rerun()

if analyze:
    clean_text = st.session_state.get("saed_text", "").strip()
    if not clean_text:
        st.session_state.saed_result = None
        st.warning("⚠️ Masukkan teks terlebih dahulu sebelum menekan ANALISIS TEKS.")
    else:
        try:
            st.session_state.saed_result = analyze_text(clean_text)
            st.session_state.saed_last_text = clean_text
            st.success("✅ Teks berhasil dianalisis. Hasil indikator dan saran diperbarui.")
        except Exception as exc:
            st.error("❌ Analisis gagal diproses. Silakan coba lagi dengan teks yang lebih singkat.")
            st.session_state.saed_result = None
            st.caption(f"Detail teknis: {type(exc).__name__}")

if st.session_state.saed_result:
    scores, evidence, overall, level, peak, sentences, links = st.session_state.saed_result
else:
    scores = {k: 0.0 for k in INDICATORS}
    evidence = {k: [] for k in INDICATORS}
    overall, level, peak, sentences, links = 0, "Rendah", "Belum dianalisis", [], []

labels = list(scores.keys())
colors = ["#20a9ff","#ffae32","#22c4ca","#7446f5","#f23883"]

def severity(v):
    return "Rendah" if v < .35 else "Sedang" if v < .65 else "Tinggi"

def detail(k, v):
    return INDICATORS[k]["label"]

# ---------- Result Summary ----------
st.markdown("## 📊 Hasil Analisis")
if peak == "Belum dianalisis":
    st.info("Masukkan teks lalu tekan **ANALISIS TEKS** untuk melihat hasil.")
else:
    st.markdown(f"**Pola dominan:** `{peak}`")
    st.markdown(f"**Tingkat keseluruhan:** **{level}** ({overall}%)")

st.markdown("## 📌 Ringkasan 5 Indikator")
st.caption("Hasil setiap indikator ditentukan dari pola kalimat, konteks, negasi, intensifier, dan hubungan antar-kalimat.")

for k, v in scores.items():
    sev = severity(v)
    icon = "🔴" if sev == "Tinggi" else ("🟠" if sev == "Sedang" else "🟢")
    ev = evidence.get(k, [])
    st.markdown(f"### {icon} {k} — {sev} ({int(v*100)}%)")
    st.caption(INDICATORS)
