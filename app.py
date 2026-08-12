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

# ---------- NLP prototype v3: sentence + paragraph context ----------
# Tidak sekadar mencocokkan kata. Sistem mencari pola hubungan antarkalimat,
# kontras, sebab-akibat, self-reference, social reference, dan evaluasi.
# Tetap rule-based prototype; untuk produksi dapat diganti/ditambah model transformer.

INDICATORS = {
    "Achievement Exposure": {
        "evidence": [
            r"(teman|orang lain|mereka|dia|rekan|kenalan).{0,80}(sukses|berhasil|prestasi|pencapaian|diterima kerja|naik jabatan|gaji|lulus|menang)",
            r"(melihat|melihat postingan|membaca|mendengar|mengetahui|menyaksikan).{0,80}(sukses|berhasil|prestasi|pencapaian)"
        ],
        "label": "Paparan terhadap pencapaian pihak lain."
    },
    "Social Comparison": {
        "evidence": [
            r"(aku|saya|diriku|diri saya).{0,80}(dibanding|berbeda dengan|kalah dari|lebih rendah|tidak sebaik|tidak seperti).{0,80}(mereka|dia|teman|orang lain)",
            r"(mereka|dia|teman|orang lain).{0,60}(lebih sukses|lebih maju|lebih kaya|lebih baik).{0,60}(daripada|dibanding|sedangkan|sementara).{0,60}(aku|saya)",
            r"(seumuran|satu usia|umur kami sama).{0,100}(sedangkan|sementara|tetapi).{0,100}(aku|saya)"
        ],
        "label": "Perbandingan eksplisit antara diri dan pihak lain."
    },
    "Perceived Lagging": {
        "evidence": [
            r"(aku|saya|diriku|diri saya).{0,80}(merasa|terasa|sepertinya).{0,50}(tertinggal|ketinggalan|terlambat)",
            r"(aku|saya).{0,80}(belum|masih belum).{0,80}(punya|mencapai|mendapatkan|berhasil).{0,100}(seperti|selevel|seusia|dibanding)",
            r"(mereka|teman|orang lain).{0,100}(sudah|telah).{0,100}(sedangkan|sementara).{0,100}(aku|saya)"
        ],
        "label": "Persepsi bahwa perkembangan diri tertinggal dari target atau kelompok pembanding."
    },
    "Future Uncertainty": {
        "evidence": [
            r"(aku|saya).{0,80}(takut|khawatir|cemas|bingung|tidak yakin).{0,100}(masa depan|ke depan|nanti|karier|pekerjaan)",
            r"(aku|saya).{0,80}(tidak tahu|belum tahu).{0,100}(harus|mau|akan).{0,100}(ke mana|bagaimana|apa yang dilakukan)",
            r"(takut|khawatir|cemas).{0,80}(gagal|tidak berhasil|tidak punya masa depan)"
        ],
        "label": "Ketidakpastian atau kekhawatiran yang diarahkan ke masa depan."
    },
    "Negative Self-Evaluation": {
        "evidence": [
            r"(aku|saya|diriku|diri saya).{0,60}(tidak cukup|tidak mampu|tidak berguna|bodoh|buruk|gagal|mengecewakan|rendah diri)",
            r"(aku|saya).{0,80}(merasa|menganggap|menilai).{0,80}(gagal|tidak mampu|tidak cukup|tidak bagus|tidak berguna)",
            r"(aku|saya).{0,80}(tidak percaya diri|meragukan kemampuan|merasa tidak layak)"
        ],
        "label": "Evaluasi negatif yang diarahkan kepada diri sendiri."
    }
}

CONTRAST = re.compile(r"\b(tetapi|namun|sedangkan|sementara|walaupun|meskipun)\b")
CAUSAL = re.compile(r"\b(karena|sehingga|akibatnya|setelah|gara-gara|membuat|menyebabkan)\b")
SELF = re.compile(r"\b(aku|diriku|diri saya|saya sendiri)\b|\bsaya\b(?!\s+(teman|kakak|adik|ibu|ayah|orang tua))")
OTHERS = re.compile(r"\b(teman|mereka|dia|orang lain|rekan|kenalan)\b")
NEGATION = re.compile(r"\b(tidak|tak|bukan|belum|tanpa)\b")

def split_sentences(text):
    text = re.sub(r"\s+", " ", text.strip())
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+|[\n]+", text) if x.strip()]

def normalize(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-zA-ZÀ-ÿ0-9\s.!?]", " ", text.lower())).strip()

def sentence_evidence(sentences, patterns):
    found = []
    for i, sent in enumerate(sentences):
        for pat in patterns:
            if re.search(pat, sent):
                found.append((i + 1, sent))
                break
    return found

def contextual_links(sentences):
    links = []
    for i in range(len(sentences) - 1):
        pair = sentences[i] + " " + sentences[i+1]
        if (SELF.search(pair) and OTHERS.search(pair)) or CONTRAST.search(pair) or CAUSAL.search(pair):
            links.append((i + 1, i + 2, pair))
    return links

def score_indicator(name, sentences, links):
    cfg = INDICATORS[name]
    evidence = sentence_evidence(sentences, cfg["evidence"])
    joined = " ".join(sentences)

    # Contextual patterns: these capture natural Indonesian phrasing where
    # the relationship is clear even when no explicit "aku vs mereka" phrase exists.
    contextual = {
        "Achievement Exposure": [
            r"\b(teman|orang lain|mereka|dia|rekan)\b.{0,120}\b(sudah|telah|punya|memiliki|mendapat|berhasil|sukses|lulus|naik|diterima)\b",
            r"\b(melihat|lihat|melihat postingan|mendengar|tahu|mengetahui)\b.{0,120}\b(teman|orang lain|mereka|dia)\b.{0,100}\b(sukses|berhasil|punya|memiliki|pencapaian|prestasi)\b"
        ],
        "Social Comparison": [
            r"\b(kapan|kapan ya|ingin|pengen|semoga)\b.{0,60}\b(bisa|dapat|punya|memiliki|seperti|kayak)\b.{0,80}\b(teman|mereka|dia|orang lain)\b",
            r"\b(seperti|kayak|sama seperti|sebanding dengan)\b.{0,80}\b(teman|mereka|dia|orang lain)\b",
            r"\b(teman|mereka|dia|orang lain)\b.{0,100}\b(sudah|telah|punya|memiliki)\b.{0,100}\b(kapan|ingin|pengen|bisa)\b"
        ],
        "Perceived Lagging": [
            r"\b(teman|mereka|dia|orang lain)\b.{0,80}\b(sudah|telah)\b.{0,100}\b(kapan|kapan ya|sementara|sedangkan)\b",
            r"\b(kapan|kapan ya)\b.{0,80}\b(bisa|punya|memiliki|mencapai)\b.{0,100}\b(seperti|kayak|teman|mereka)\b",
            r"\b(umur|usia)\b.{0,60}\b(20|21|22|23|24|25|26|27|28|29|30)\b.{0,120}\b(sudah|telah|punya|memiliki)\b"
        ],
        "Future Uncertainty": [
            r"\b(kapan|kapan ya|entah kapan|belum tahu|tidak tahu)\b.{0,100}\b(bisa|akan|mampu|punya|mencapai|mendapat)\b",
            r"\b(nggak tahu|gak tahu|tidak tahu|belum tahu)\b.{0,100}\b(masa depan|ke depan|nanti|karier|pekerjaan|hidup)\b"
        ],
        "Negative Self-Evaluation": [
            r"\b(aku|saya|diriku|diri saya)\b.{0,80}\b(gagal|bodoh|buruk|tidak mampu|nggak mampu|gak mampu|tidak cukup|nggak cukup|tidak berguna|tidak layak)\b",
            r"\b(aku|saya)\b.{0,80}\b(lebih rendah|kalah|payah|jelek)\b"
        ]
    }

    contextual_hits = []
    for pat in contextual.get(name, []):
        m = re.search(pat, joined)
        if m:
            contextual_hits.append(m.group(0))

    # Merge evidence from exact sentence patterns and contextual paragraph patterns.
    if contextual_hits:
        for hit in contextual_hits:
            # Attach the nearest sentence as evidence.
            nearest = next(((i+1, sent) for i, sent in enumerate(sentences) if hit[:25] in sent), None)
            if nearest:
                evidence.append(nearest)
            elif sentences:
                evidence.append((1, sentences[0]))

    evidence = list(dict.fromkeys(evidence))

    # Scoring is evidence-driven. One contextual relation can produce a meaningful
    # signal, but a single generic keyword cannot.
    score = min(0.80, len(evidence) * 0.27)
    if contextual_hits:
        score = max(score, 0.42)
    if evidence and links:
        score += min(0.15, 0.05 * len(links))

    # Strong self/other relation for comparison and lagging.
    if name in ("Social Comparison", "Perceived Lagging"):
        relation = (
            re.search(r"\b(seperti|kayak|dibanding|berbeda dengan|lebih .{0,20} daripada)\b", joined)
            and re.search(r"\b(teman|mereka|dia|orang lain)\b", joined)
        )
        if relation:
            score += 0.12

    return round(min(score, 1.0), 2), evidence

def analyze_text(t):
    clean = normalize(t)
    sentences = split_sentences(clean)
    links = contextual_links(sentences)
    scores, evidence = {}, {}
    for name in INDICATORS:
        scores[name], evidence[name] = score_indicator(name, sentences, links)

    total = sum(scores.values())
    overall = round(total / len(scores) * 100)
    peak = max(scores, key=scores.get) if total else "Belum terdeteksi"
    level = "Rendah" if overall < 35 else "Sedang" if overall < 65 else "Tinggi"
    return scores, evidence, overall, level, peak, sentences, links

if analyze:
    scores, evidence, overall, level, peak, sentences, links = analyze_text(text)
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
peak_hits = evidence.get(peak, []) if peak != "Belum dianalisis" else []
patterns = [
("🔵 Pola Utama", f"Indikator tertinggi: {peak} ({scores.get(peak,0):.2f}). Bukti bahasa: {', '.join(peak_hits) if peak_hits else 'belum ada bukti frasa spesifik'}."),
("🟠 Pembedaan Indikator", "Achievement Exposure hanya mengukur penyebutan/paparan terhadap pencapaian orang lain. Social Comparison baru naik jika teks menunjukkan tindakan atau penilaian membandingkan diri dengan orang lain."),
("🟣 Konteks & Negasi", "Kata seperti 'tidak takut' atau 'tidak tertinggal' tidak seharusnya dihitung sama dengan pernyataan positif yang menunjukkan kekhawatiran. Prototype ini menggunakan pemeriksaan negasi sederhana."),
("🟢 Batasan", "Skor berasal dari rule-based keyword/phrase matching. Untuk akurasi produksi, sistem sebaiknya dilatih dan diuji dengan dataset berlabel serta evaluasi precision, recall, F1, dan confusion matrix.")
]
for title,body in patterns:
    st.markdown(f"<div class='insight'><b>{title}</b><br>{body}</div>",unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------- Recommendations ----------
st.markdown('<div class="tip">', unsafe_allow_html=True)
st.markdown("### 🌱 Saran yang sesuai")
st.write("Berdasarkan pola analisis, berikut beberapa saran yang dapat kamu terapkan:")
recs=[]
if scores["Achievement Exposure"] >= .35:
    recs += ["Pisahkan fakta dari interpretasi: keberhasilan orang lain adalah fakta tentang mereka, bukan ukuran nilai dirimu.",
             "Atur jeda dari konten pencapaian jika setelah melihatnya kamu mulai mengevaluasi hidup sendiri."]
if scores["Social Comparison"] >= .35:
    recs += ["Ketika membandingkan diri, tulis apa yang benar-benar kamu ketahui tentang hidupmu dan apa yang hanya asumsi tentang orang lain.",
             "Ubah pertanyaan 'mengapa aku tidak seperti mereka?' menjadi 'langkah apa yang realistis untuk kondisiku sekarang?'"]
if scores["Perceived Lagging"] >= .35:
    recs += ["Tentukan milestone pribadi berdasarkan kondisi dan prioritasmu, bukan timeline teman sebaya.",
             "Ukur progres dengan perubahan dari titik awalmu sendiri."]
if scores["Negative Self-Evaluation"] >= .35:
    recs += ["Ganti penilaian menyeluruh seperti 'aku gagal' dengan evaluasi spesifik tentang situasi yang belum berhasil.",
             "Catat bukti kemampuan, usaha, dan kemajuan kecil agar evaluasi diri lebih seimbang."]
if scores["Future Uncertainty"] >= .35:
    recs += ["Pisahkan hal yang bisa dikendalikan hari ini dari hal yang belum bisa dipastikan.",
             "Pilih satu tindakan kecil untuk 24 jam ke depan daripada mencoba memecahkan seluruh masa depan sekaligus."]
if not recs:
    recs = ["Belum ada indikator yang cukup kuat. Gunakan hasil ini sebagai refleksi, bukan label diri.",
            "Jika ingin analisis lebih akurat, masukkan satu paragraf utuh agar hubungan antar-kalimat dapat dibaca."]

for r in recs:
    st.markdown(f"✅ {r}")
st.markdown("<div style='margin-top:12px;padding:12px;border-radius:12px;background:#3b3a1d'>💡 <i>“Progres yang lambat tetaplah progres. Fokus pada perjalananmu sendiri.”</i></div>",unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

with st.expander("🔎 Lihat proses analisis kalimat & paragraf"):
    if sentences:
        st.markdown("**Segmentasi kalimat:**")
        for i, sent in enumerate(sentences, 1):
            st.markdown(f"- **Kalimat {i}:** {sent}")
        st.markdown(f"**Hubungan konteks terdeteksi:** {len(links)}")
        for x, y, pair in links:
            st.caption(f"Kalimat {x} ↔ {y}: konteks berpotensi saling terkait.")
    else:
        st.caption("Belum ada teks yang dianalisis.")

st.markdown("<div style='text-align:center;color:#66759a;padding:25px'>SAED • Social Achievement Exposure Detector • Prototype NLP</div>",unsafe_allow_html=True)
