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
    st.session_state.saed_result = None
    st.rerun()

# ---------- NLP engine v7: contextual sentence/paragraph analysis ----------
# Analisis berbasis relasi makna dalam kalimat/paragraf, bukan satu keyword.
# Prototype rule-based; bukan diagnosis psikologis.

INDICATORS = {
    "Achievement Exposure": {
        "label": "Paparan terhadap pencapaian, keberhasilan, atau keunggulan pihak lain.",
        "patterns": [
            r"\b(teman|orang lain|mereka|dia|lawan|rekan|kenalan)\b.{0,100}\b(sudah|telah|punya|memiliki|mendapat|berhasil|sukses|menang|lulus|diterima|naik jabatan|berpengalaman|lebih maju)\b",
            r"\b(saya|aku)\b.{0,100}\b(melihat|melihat postingan|mendengar|mengetahui|tahu|menyadari)\b.{0,100}\b(teman|orang lain|mereka|dia)\b"
        ],
        "phrases": ["teman saya sudah", "orang lain sudah", "teman saya berhasil", "teman saya punya",
                    "lawan saya berpengalaman", "teman saya lebih maju"]
    },
    "Social Comparison": {
        "label": "Perbandingan antara kemampuan, kondisi, atau pencapaian diri dengan pihak lain.",
        "patterns": [
            r"\b(dibanding|di banding|dibandingkan|berbeda dengan|kalah dari|lebih rendah dari|tidak sebaik|tidak seperti)\b.{0,100}\b(saya|aku|diriku|diri saya|lawan|teman|mereka|dia)\b",
            r"\b(saya|aku)\b.{0,100}\b(dibanding|di banding|dibandingkan|berbeda dengan|kalah dari)\b",
            r"\b(lawan|teman|mereka|dia)\b.{0,100}\b(lebih berpengalaman|lebih sukses|lebih maju|lebih baik|lebih mampu|lebih hebat)\b.{0,100}\b(saya|aku)\b",
            r"\b(saya|aku)\b.{0,100}\b(seperti|kayak|sama seperti)\b.{0,100}\b(teman|mereka|dia|orang lain)\b",
            r"\b(kapan|kapan ya)\b.{0,80}\b(bisa|mampu|punya|memiliki|mencapai)\b.{0,80}\b(seperti|kayak)\b.{0,60}\b(teman|mereka|dia)\b"
        ],
        "phrases": ["dibanding saya", "di banding saya", "dibandingkan dengan saya",
                    "lebih berpengalaman dari saya", "lebih berpengalaman dibanding saya",
                    "seperti teman saya", "kalah dari"]
    },
    "Perceived Lagging": {
        "label": "Perasaan bahwa perkembangan atau kemampuan diri tertinggal dari pihak pembanding.",
        "patterns": [
            r"\b(lawan|teman|mereka|dia)\b.{0,100}\b(sudah|telah|lebih|lebih dulu)\b.{0,100}\b(saya|aku)\b",
            r"\b(saya|aku)\b.{0,80}\b(tertinggal|ketinggalan|terlambat|belum bisa|belum punya|masih belum)\b",
            r"\b(kapan|kapan ya)\b.{0,100}\b(bisa|mampu|punya|memiliki|mencapai)\b.{0,100}\b(seperti|kayak|teman|mereka|dia)\b",
            r"\b(umur|usia)\b.{0,60}\b(sudah|telah)\b.{0,100}\b(saya|aku|teman|mereka)\b"
        ],
        "phrases": ["tertinggal", "ketinggalan", "belum bisa", "masih belum",
                    "kapan ya bisa seperti", "belum punya seperti"]
    },
    "Future Uncertainty": {
        "label": "Kekhawatiran, keraguan, pertanyaan, atau ketidakpastian tentang hasil, kemampuan, waktu, atau keadaan yang akan datang.",
        "patterns": [
            # Emosi ketidakpastian + masa depan/hasil
            r"\b(saya|aku)\b.{0,100}\b(khawatir|cemas|takut|ragu|bingung|waswas|gelisah)\b.{0,160}\b(akan|bisa|mampu|nanti|ke depan|masa depan|suatu hari|berhasil|menang|gagal|mencapai|mendapat|punya|memiliki)\b",
            # "takut tidak..." / "khawatir tidak..." tanpa kata future eksplisit
            r"\b(khawatir|cemas|takut|waswas|ragu)\b.{0,100}\b(tidak|nggak|gak|belum)\b.{0,100}\b(bisa|mampu|berhasil|menang|mencapai|mendapat|punya|memiliki|sempat)\b",
            # Pertanyaan/ketidakpastian waktu dan kemungkinan
            r"\b(kapan|kapan ya|kapan kira.?kira|entah kapan)\b.{0,140}\b(bisa|mampu|akan|mendapat|mencapai|punya|memiliki|berhasil|terjadi|tercapai)\b",
            # Ketidakpastian eksplisit
            r"\b(belum tahu|tidak tahu|nggak tahu|gak tahu|entah|tidak yakin|nggak yakin|gak yakin|belum yakin|masih ragu)\b.{0,160}\b(akan|bisa|mampu|nanti|ke depan|masa depan|berhasil|menang|gagal|mencapai|mendapat|punya|memiliki|terjadi)\b",
            # "apakah saya..." / "bisa nggak..." / "akankah..."
            r"\b(apakah|akankah)\b.{0,160}\b(saya|aku|kita)\b.{0,100}\b(bisa|mampu|berhasil|menang|mencapai|mendapat|punya|memiliki)\b",
            r"\b(saya|aku|kita)\b.{0,100}\b(bisa nggak|bisa tidak|bisa gak|bisa kah|bisakah|mungkinkah)\b.{0,120}\b(nanti|ke depan|suatu hari|berhasil|menang|mencapai|mendapat|punya|memiliki)\b",
            r"\b(saya|aku)\b.{0,100}\b(akan|tidak akan|mungkin akan|mungkin tidak akan)\b.{0,120}\b(berhasil|menang|gagal|kalah|mencapai|mendapat|punya|memiliki|terjadi)\b",
            # Prediksi negatif masa depan
            r"\b(saya|aku)\b.{0,100}\b(mungkin|kemungkinan|takutnya|jangan.?jangan)\b.{0,140}\b(gagal|kalah|tidak bisa|tidak mampu|tidak berhasil|tidak tercapai|tidak mendapat)\b",
            r"\b(mungkin|kemungkinan|takutnya|jangan.?jangan)\b.{0,100}\b(saya|aku)\b.{0,140}\b(tidak bisa|tidak akan bisa|tidak mampu|tidak akan mampu|tidak berhasil|tidak akan berhasil|gagal|kalah|tidak tercapai|tidak mendapat)\b",
            # Future-oriented goals where uncertainty is expressed by "belum"
            r"\b(saya|aku)\b.{0,100}\b(belum|masih belum)\b.{0,100}\b(tahu|yakin|pasti|bisa|mampu)\b"
        ],
        "phrases": [
            "saya khawatir", "aku khawatir", "saya takut", "aku takut",
            "saya cemas", "aku cemas", "saya ragu", "aku ragu",
            "kapan ya bisa", "kapan kira-kira", "entah kapan",
            "belum tahu", "tidak tahu", "nggak tahu", "gak tahu",
            "tidak yakin", "nggak yakin", "gak yakin", "belum yakin",
            "masih ragu", "apakah saya bisa", "bisakah saya",
            "mungkinkah saya", "takutnya saya", "jangan-jangan saya"
        ]
    },
    "Negative Self-Evaluation": {
        "label": "Penilaian negatif yang diarahkan langsung kepada nilai/kemampuan diri.",
        "patterns": [
            r"\b(saya|aku)\b.{0,80}\b(gagal|bodoh|buruk|tidak mampu|nggak mampu|gak mampu|tidak cukup|tidak berguna|tidak layak|payah|jelek|rendah diri)\b",
            r"\b(saya|aku)\b.{0,80}\b(merasa|menganggap|menilai)\b.{0,80}\b(gagal|tidak mampu|tidak cukup|tidak layak|tidak berguna|buruk)\b"
        ],
        "phrases": ["saya gagal", "saya bodoh", "saya tidak mampu", "saya tidak cukup", "saya tidak layak"]
    }
}

CONTRAST = re.compile(r"\b(tetapi|namun|sedangkan|sementara|walaupun|meskipun|padahal)\b")
CAUSE = re.compile(r"\b(karena|sehingga|akibatnya|setelah|gara-gara|membuat|menyebabkan)\b")
SELF = re.compile(r"\b(aku|saya|diriku|diri saya)\b")
OTHER = re.compile(r"\b(teman|mereka|dia|orang lain|lawan|rekan|kenalan)\b")
WORRY = re.compile(r"\b(khawatir|cemas|takut|ragu|bingung|waswas|gelisah)\b")
NEGATIVE_SELF = re.compile(r"\b(tidak mampu|nggak mampu|gak mampu|tidak cukup|tidak berguna|tidak layak|gagal|bodoh|buruk|payah)\b")

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

def context_links(sentences):
    links = []
    for i in range(len(sentences)-1):
        pair = sentences[i] + " " + sentences[i+1]
        if (SELF.search(pair) and OTHER.search(pair)) or CONTRAST.search(pair) or CAUSE.search(pair):
            links.append((i+1, i+2))
    return links

def score_indicator(name, sentences, full_text, links):
    cfg = INDICATORS[name]
    evidence = find_evidence(sentences, cfg["patterns"])
    phrase_hits = [p for p in cfg["phrases"] if p in full_text]

    # Evidence from a natural phrase may span a whole sentence.
    if phrase_hits and not evidence and sentences:
        evidence = [(i, sent) for i, sent in enumerate(sentences, 1)
                    if any(p in sent for p in phrase_hits)]

    score = 0.0
    if evidence:
        score += min(0.55, 0.32 + 0.10 * (len(evidence)-1))
    if phrase_hits:
        score += min(0.18, 0.06 * len(phrase_hits))
    if evidence and links:
        score += min(0.12, 0.04 * len(links))

    # Contextual reinforcement: worry + inability is future uncertainty,
    # while comparison with an opponent is social comparison.
    if name == "Future Uncertainty":
        # Sangat peka terhadap sinyal uncertainty, tetapi tetap membutuhkan
        # orientasi hasil/waktu/kemungkinan agar tidak menandai semua keluhan.
        if WORRY.search(full_text):
            score += 0.24
        if re.search(r"\b(kapan|nanti|ke depan|masa depan|suatu hari|akan|mungkin|kemungkinan|entah|belum|masih ragu|tidak yakin|nggak yakin|gak yakin|apakah|akankah|bisakah|mungkinkah)\b", full_text):
            score += 0.18
        if re.search(r"\b(tidak bisa|tidak mampu|gagal|kalah|tidak berhasil|tidak tercapai|tidak mendapat|belum bisa|belum mampu)\b", full_text):
            score += 0.16
        # Kombinasi khawatir/takut + outcome negatif adalah sinyal kuat.
        if WORRY.search(full_text) and re.search(r"\b(tidak|nggak|gak|belum|gagal|kalah)\b", full_text):
            score += 0.16
    if name == "Social Comparison" and SELF.search(full_text) and OTHER.search(full_text):
        if re.search(r"\b(dibanding|dibandingkan|lebih|seperti|lawan|teman)\b", full_text):
            score += 0.20
    if name == "Perceived Lagging" and SELF.search(full_text) and OTHER.search(full_text):
        if re.search(r"\b(lebih|berpengalaman|sudah|belum|kapan|dibanding)\b", full_text):
            score += 0.14
    # Do not confuse a competition-specific fear ("tidak bisa menang")
    # with global negative self-evaluation.
    if name == "Negative Self-Evaluation":
        if NEGATIVE_SELF.search(full_text):
            score += 0.20
        elif re.search(r"\b(tidak bisa menang|tidak mampu menang|takut kalah)\b", full_text):
            score = min(score, 0.15)

    return round(min(score, 1.0), 2), list(dict.fromkeys(evidence))

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

# Persist analysis so the result does not disappear on a Streamlit rerun.
if "saed_result" not in st.session_state:
    st.session_state.saed_result = None

if analyze and text.strip():
    st.session_state.saed_result = analyze_text(text)

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
    st.markdown(f"Pola yang terdeteksi: <span class='badge'>{peak}</span>",unsafe_allow_html=True)
    if peak=="Belum dianalisis":
        desc="Masukkan teks lalu tekan **ANALISIS TEKS**. SAED tidak mengisi skor secara otomatis agar hasil tidak menyesatkan."
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
fig.add_trace(go.Bar(x=labels,y=list(scores.values()),text=[f"{v:.2f}" for v in scores.values()],
                     textposition="outside",marker_color=colors))
fig.update_yaxes(range=[0,1.12],dtick=.2)
fig.update_layout(height=370,margin=dict(l=20,r=20,t=30,b=90),paper_bgcolor="rgba(0,0,0,0)",
                  plot_bgcolor="rgba(0,0,0,0)",font_color="#dbe6ff",showlegend=False)
st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

st.markdown("### ☷ Detail Indikator")
cols=st.columns(2)
for i,(k,v) in enumerate(scores.items()):
    with cols[i%2]:
        sev=severity(v)
        st.markdown(f"""<div class="insight"><b>{k}</b>
        <span style="float:right"><b>{sev}</b> · {v:.2f}</span>
        <br><span class="small">{detail(k,v)}</span>
        <br><span class="small">Bukti kalimat: {" | ".join([f"Kalimat {n}: {sent}" for n, sent in evidence.get(k, [])]) if evidence.get(k) else "Tidak ada bukti kalimat yang memenuhi pola."}</span></div>""",unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------- Deep analysis ----------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 🔍 Analisis Mendalam")
peak_hits = evidence.get(peak, []) if peak not in ("Belum dianalisis", "Belum terdeteksi") else []
peak_evidence_text = (
    " | ".join([f"Kalimat {n}: {sent}" for n, sent in peak_hits])
    if peak_hits else "Belum ada bukti kalimat spesifik."
)
patterns = [
("🔵 Pola Utama", f"Indikator tertinggi: {peak} ({scores.get(peak,0):.2f}). Bukti kalimat: {peak_evidence_text}"),
("🟠 Pembedaan Indikator", "Achievement Exposure hanya mengukur penyebutan/paparan terhadap pencapaian orang lain. Social Comparison baru naik jika teks menunjukkan tindakan atau penilaian membandingkan diri dengan orang lain."),
("🟣 Konteks & Negasi", "Kata seperti 'tidak takut' atau 'tidak tertinggal' tidak seharusnya dihitung sama dengan pernyataan positif yang menunjukkan kekhawatiran. Prototype ini menggunakan pemeriksaan negasi sederhana."),
("🟢 Batasan", "Skor berasal dari rule-based keyword/phrase matching. Untuk akurasi produksi, sistem sebaiknya dilatih dan diuji dengan dataset berlabel serta evaluasi precision, recall, F1, dan confusion matrix.")
]
for title, body in patterns:
    st.markdown(f"<div class='insight'><b>{title}</b><br>{body}</div>",unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------- Recommendations ----------
st.markdown('<div class="tip">', unsafe_allow_html=True)
st.markdown("### 🌱 Saran yang sesuai")
st.write("Berdasarkan pola analisis")
