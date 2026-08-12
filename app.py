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


# ---------- NLP / sentence-aware engine ----------
INDICATORS = {
    "Achievement Exposure": {
        "label": "Paparan terhadap pencapaian orang lain, standar sosial, atau konten keberhasilan.",
        "terms": {
            "sukses": .22, "berhasil": .20, "prestasi": .22, "pencapaian": .24,
            "gaji": .16, "jabatan": .16, "lulus": .16, "menang": .16,
            "orang lain": .22, "teman": .15, "linkedin": .20, "instagram": .18,
            "media sosial": .20, "konten": .10
        },
        "phrases": [
            (r"\bteman(?:-teman)?\s+(?:saya|ku|aku)\s+(?:sudah|telah|lebih)\b", .30),
            (r"\b(?:melihat|lihat|melihatkan)\b.{0,45}\b(?:sukses|berhasil|prestasi|pencapaian)\b", .30),
            (r"\b(?:di|dari)\s+instagram\b|\b(?:di|dari)\s+linkedin\b", .25),
        ]
    },
    "Social Comparison": {
        "label": "Pola membandingkan kondisi, kemampuan, usia, atau pencapaian diri dengan orang lain.",
        "terms": {
            "dibanding": .30, "bandingkan": .30, "dibandingkan": .30, "lebih sukses": .34,
            "lebih maju": .32, "lebih berhasil": .32, "lebih pintar": .28,
            "mereka lebih": .32, "dia lebih": .30, "teman-teman": .16,
            "orang lain": .16, "seumuran": .25, "seusia": .25, "umur": .12, "usia": .12
        },
        "phrases": [
            (r"\baku\s+(?:jauh\s+)?(?:kalah|tertinggal)\s+(?:dari|dibanding)\b", .35),
            (r"\b(?:sementara|sedangkan)\s+(?:mereka|dia|teman)\b", .28),
            (r"\b(?:mereka|dia|teman(?:-teman)?)\b.{0,55}\b(?:lebih|sudah)\b", .26),
        ]
    },
    "Perceived Lagging": {
        "label": "Perasaan tertinggal dari target pribadi, teman sebaya, atau ritme perkembangan tertentu.",
        "terms": {
            "tertinggal": .34, "ketinggalan": .34, "belum punya": .25, "belum mencapai": .30,
            "belum berhasil": .28, "belum sukses": .28, "telat": .30, "terlambat": .30,
            "lambat": .20, "terlambat dari": .34
        },
        "phrases": [
            (r"\bmerasa\s+(?:sangat\s+)?tertinggal\b", .40),
            (r"\bbelum\s+(?:mencapai|mendapatkan|memiliki|bisa|berhasil)\b", .25),
            (r"\b(?:di usia|umur)\s+\d+\b.{0,60}\b(?:belum|tidak)\b", .28),
            (r"\bseharusnya\s+(?:saya|aku)\s+(?:sudah|telah)\b", .32),
        ]
    },
    "Future Uncertainty": {
        "label": "Kekhawatiran, ketidakpastian, prediksi negatif, atau keraguan tentang masa depan.",
        "terms": {
            "takut": .28, "khawatir": .30, "masa depan": .28, "besok": .10, "nanti": .10,
            "gagal": .22, "cemas": .28, "tidak yakin": .28, "bingung": .18,
            "waswas": .28, "gelisah": .25, "tidak tahu": .20, "bagaimana nanti": .30
        },
        "phrases": [
            (r"\baku\s+(?:takut|khawatir|cemas)\b.{0,70}\b(?:masa depan|gagal|tidak akan)\b", .38),
            (r"\b(?:bagaimana|gimana)\s+(?:kalau|jika)\b.{0,70}\b(?:gagal|tidak berhasil|tidak bisa)\b", .34),
            (r"\btidak tahu\s+(?:harus|akan)\b", .25),
        ]
    },
    "Negative Self-Evaluation": {
        "label": "Penilaian diri negatif, keraguan kemampuan, atau pelabelan diri yang merendahkan.",
        "terms": {
            "saya tidak": .10, "aku tidak": .10, "kurang": .18, "jelek": .28,
            "bodoh": .36, "gagal": .22, "tidak mampu": .34, "tidak cukup": .34,
            "rendah diri": .34, "tidak berguna": .38, "tidak pintar": .34,
            "tidak bisa": .20, "payah": .34, "buruk": .20
        },
        "phrases": [
            (r"\b(?:aku|saya)\s+(?:merasa|adalah)\s+(?:gagal|bodoh|payah|tidak mampu|tidak cukup)\b", .45),
            (r"\baku\s+(?:tidak|nggak|gak)\s+(?:bisa|mampu|pintar|cukup)\b", .36),
            (r"\b(?:saya|aku)\s+(?:selalu|sering)\s+(?:gagal|kalah|tidak bisa)\b", .36),
        ]
    }
}

NEGATIONS = {"tidak", "tak", "bukan", "belum", "nggak", "gak", "jangan"}
INTENSIFIERS = {"sangat": 1.25, "terlalu": 1.20, "banget": 1.20, "benar-benar": 1.18, "sering": 1.12, "selalu": 1.20, "cukup": 1.08}
EMOTION_WORDS = {"takut", "khawatir", "cemas", "gelisah", "waswas", "tertekan", "kecewa", "sedih", "malu", "frustrasi"}

def split_sentences(text):
    text = re.sub(r'\s+', ' ', text.strip())
    if not text:
        return []
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+|(?<=[.!?])$', text) if x.strip()]

def split_paragraphs(text):
    return [p.strip() for p in re.split(r'\n\s*\n+', text.strip()) if p.strip()] or ([text.strip()] if text.strip() else [])

def term_is_negated(sentence, term):
    words = sentence.lower().split()
    target = term.lower().split()
    for i in range(len(words) - len(target) + 1):
        if words[i:i+len(target)] == target:
            before = words[max(0, i-4):i]
            if any(n in before for n in NEGATIONS):
                return True
    return False

def sentence_intensity(sentence):
    low = sentence.lower()
    mult = 1.0
    for word, factor in INTENSIFIERS.items():
        if word in low:
            mult = max(mult, factor)
    if "!" in sentence or sentence.count("?") >= 2:
        mult *= 1.05
    return min(mult, 1.35)

def analyze_text(text):
    sentences = split_sentences(text)
    paragraphs = split_paragraphs(text)
    scores = {k: 0.0 for k in INDICATORS}
    evidence = {k: [] for k in INDICATORS}
    hits = {k: [] for k in INDICATORS}

    if not sentences:
        return scores, hits, evidence, 0, "Rendah", "Belum dianalisis", [], []

    # Sentence-level scoring: every sentence is evaluated independently,
    # then paragraph repetition/context is added.
    sentence_flags = []
    for idx, sentence in enumerate(sentences, 1):
        low = sentence.lower()
        row = {}
        for ind, cfg in INDICATORS.items():
            local = 0.0
            reasons = []

            for term, weight in cfg["terms"].items():
                if term in low:
                    if term_is_negated(low, term) and ind not in {"Negative Self-Evaluation"}:
                        continue
                    local += weight
                    reasons.append(term)
                    if term not in hits[ind]:
                        hits[ind].append(term)

            for pattern, weight in cfg["phrases"]:
                try:
                    if re.search(pattern, low):
                        local += weight
                        reasons.append("pola frasa")
                except re.error:
                    pass

            if local > 0:
                local *= sentence_intensity(sentence)
                # A sentence containing several independent cues is stronger.
                local += min(.16, max(0, len(set(reasons)) - 1) * .035)
                local = min(local, 1.0)
                row[ind] = local
                evidence[ind].append({
                    "sentence": idx,
                    "text": sentence,
                    "reasons": list(dict.fromkeys(reasons))[:5],
                    "score": local
                })
            else:
                row[ind] = 0.0
        sentence_flags.append(row)

    # Cross-sentence / paragraph sensitivity.
    for ind in INDICATORS:
        vals = [r[ind] for r in sentence_flags if r[ind] > 0]
        if vals:
            # Strongest sentence + supporting sentences, with repetition bonus.
            strongest = max(vals)
            support = sum(vals[1:]) * 0.32 if len(vals) > 1 else 0
            repeat_bonus = min(.16, max(0, len(vals)-1) * .04)
            scores[ind] = min(1.0, strongest + support + repeat_bonus)

    # Contextual cross-indicator patterns.
    joined = " ".join(sentences).lower()
    if re.search(r"\b(?:mereka|teman|orang lain)\b.{0,70}\b(?:lebih|sudah)\b", joined):
        scores["Achievement Exposure"] = min(1, scores["Achievement Exposure"] + .10)
        scores["Social Comparison"] = min(1, scores["Social Comparison"] + .14)
    if re.search(r"\b(?:merasa|terasa)\s+(?:sangat\s+)?tertinggal\b", joined):
        scores["Perceived Lagging"] = min(1, scores["Perceived Lagging"] + .12)
    if re.search(r"\b(?:takut|khawatir|cemas)\b.{0,80}\b(?:masa depan|nanti|besok|gagal)\b", joined):
        scores["Future Uncertainty"] = min(1, scores["Future Uncertainty"] + .12)
    if re.search(r"\b(?:aku|saya)\b.{0,25}\b(?:tidak|nggak|gak)\b.{0,25}\b(?:bisa|mampu|cukup|pintar)\b", joined):
        scores["Negative Self-Evaluation"] = min(1, scores["Negative Self-Evaluation"] + .12)

    # Paragraph repetition bonus.
    if len(paragraphs) > 1:
        for ind in scores:
            paragraph_hits = sum(
                1 for para in paragraphs
                if any(
                    (term in para.lower() and not term_is_negated(para.lower(), term))
                    for term in INDICATORS[ind]["terms"]
                )
            )
            scores[ind] = min(1.0, scores[ind] + min(.10, max(0, paragraph_hits-1)*.05))

    # Sort evidence by sentence strength.
    for ind in evidence:
        evidence[ind].sort(key=lambda x: x["score"], reverse=True)
        evidence[ind] = evidence[ind][:5]

    overall = round(sum(scores.values()) / len(scores) * 100)
    peak = max(scores, key=scores.get)
    level = "Rendah" if overall < 35 else "Sedang" if overall < 65 else "Parah"

    # If no meaningful signal, do not fabricate a strong pattern.
    if max(scores.values()) < .10:
        peak = "Belum ada pola kuat"
        level = "Rendah"

    return scores, hits, evidence, overall, level, peak, sentences, paragraphs

# ---------- Session state ----------
if "saed_result" not in st.session_state:
    st.session_state.saed_result = None

if reset:
    st.session_state.saed_result = None
    st.rerun()

if analyze:
    if not text.strip():
        st.warning("⚠️ Masukkan teks terlebih dahulu.")
        st.session_state.saed_result = None
    else:
        st.session_state.saed_result = analyze_text(text)

if st.session_state.saed_result:
    scores, hits, evidence, overall, level, peak, sentences, paragraphs = st.session_state.saed_result
else:
    scores = {k: 0.0 for k in INDICATORS}
    hits = {k: [] for k in INDICATORS}
    evidence = {k: [] for k in INDICATORS}
    overall, level, peak, sentences, paragraphs = 0, "Rendah", "Belum dianalisis", [], []

def severity(v):
    return "Rendah" if v < .35 else "Sedang" if v < .65 else "Parah"

def detail(k):
    return INDICATORS[k]["label"]

def evidence_reason(item):
    reasons = item.get("reasons") or []
    if not reasons:
        return "Pola konteks kalimat terdeteksi."
    if "pola frasa" in reasons and len(reasons) > 1:
        return "Teridentifikasi frasa kontekstual serta kata pemicu: " + ", ".join(reasons[:-1])
    if "pola frasa" in reasons:
        return "Teridentifikasi pola frasa yang sesuai dengan indikator."
    return "Kata/frasa terdeteksi: " + ", ".join(reasons)

# ---------- Result ----------
if peak != "Belum dianalisis":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("## 📊 Hasil Analisis")
    if peak == "Belum ada pola kuat":
        st.info("Belum ditemukan pola indikator yang kuat pada teks.")
    else:
        st.markdown(f"**Pola dominan:** `{peak}`")
        st.markdown(f"**Tingkat keseluruhan:** **{level}** · {overall}%")
        st.caption(f"Dianalisis dari {len(sentences)} kalimat dan {len(paragraphs)} paragraf.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("## 📌 Rincian 5 Indikator")
    for k, v in scores.items():
        sev = severity(v)
        icon = "🔴" if sev == "Parah" else ("🟠" if sev == "Sedang" else "🟢")
        st.markdown(f"### {icon} {k} — {sev} ({round(v*100)}%)")
        st.caption(detail(k))
        ev = evidence.get(k, [])
        if ev:
            for item in ev[:3]:
                st.markdown(f"> **Kalimat {item['sentence']}:** {item['text']}")
                st.caption("↳ " + evidence_reason(item))
        else:
            st.caption("↳ Tidak ditemukan bukti kalimat yang cukup kuat.")

# ---------- Dynamic recommendations ----------
def contextual_recommendations(scores, evidence, sentences):
    recs = []

    def add(text):
        if text and text not in recs:
            recs.append(text)

    joined = " ".join(sentences).lower()

    for ind, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        sev = severity(score)
        ev = evidence.get(ind, [])
        strongest = ev[0]["text"] if ev else ""
        low = strongest.lower()

        if ind == "Achievement Exposure" and score >= .25:
            if any(x in joined for x in ["instagram", "linkedin", "media sosial", "konten"]):
                add("Kamu menyebut paparan dari media sosial. Coba atur jeda atau batasi akun/konten pencapaian yang paling sering membuatmu terdorong membandingkan diri.")
            elif any(x in joined for x in ["teman", "orang lain", "mereka"]):
                add("Karena pencapaian orang lain muncul dalam teks, ambil informasi yang berguna dari keberhasilan mereka tanpa menjadikannya patokan kapan kamu harus mencapai hal yang sama.")
            else:
                add("Saat melihat keberhasilan orang lain, pisahkan fakta tentang pencapaian mereka dari penilaian terhadap dirimu sendiri.")
            if sev == "Parah":
                add("Paparan pencapaian terlihat cukup kuat. Buat ruang khusus untuk mengevaluasi targetmu sendiri sebelum kembali melihat pencapaian orang lain.")

        if ind == "Social Comparison" and score >= .25:
            if re.search(r"\b(?:lebih sukses|lebih maju|lebih berhasil|mereka lebih|dia lebih)\b", joined):
                add("Kalimatmu memakai pola 'lebih ...'. Ubah pembanding menjadi target: sebutkan satu kemampuan yang ingin kamu tingkatkan tanpa harus mengejar posisi orang tersebut.")
            elif re.search(r"\b(?:seumuran|seusia|umur|usia)\b", joined):
                add("Perbandingan berdasarkan usia muncul dalam teks. Gunakan usia sebagai konteks, bukan deadline universal; tiap orang memiliki kondisi dan titik awal yang berbeda.")
            else:
                add("Ketika muncul dorongan membandingkan diri, coba tanyakan: 'Apa yang bisa saya pelajari dari situasi ini?' bukan 'Mengapa saya tidak seperti mereka?'")
            if sev == "Parah":
                add("Karena pola perbandingan cukup kuat, catat dua kemajuan pribadimu sebelum menilai posisi diri berdasarkan pencapaian orang lain.")

        if ind == "Perceived Lagging" and score >= .25:
            if re.search(r"\b(?:belum|terlambat|telat)\b", joined):
                add("Kata 'belum/terlambat' muncul dalam teks. Ganti fokus dari batas waktu menjadi langkah berikutnya yang benar-benar bisa dilakukan minggu ini.")
            if re.search(r"\b(?:seharusnya|usia|umur)\b", joined):
                add("Teks mengaitkan kemajuan dengan usia atau sesuatu yang 'seharusnya' sudah terjadi. Buat timeline berdasarkan kondisi dan targetmu sendiri.")
            else:
                add("Rasa tertinggal akan lebih mudah dikelola jika target besar dipecah menjadi satu pencapaian kecil yang dapat diukur.")
            if sev == "Parah":
                add("Jangan mengejar seluruh target sekaligus. Pilih satu indikator kemajuan yang bisa berubah dalam 7 hari dan ukur hasilnya.")

        if ind == "Future Uncertainty" and score >= .25:
            if re.search(r"\b(?:takut|khawatir|cemas|waswas|gelisah)\b", joined):
                add("Karena kalimat mengandung kekhawatiran, tulis dua bagian: 'yang bisa saya kendalikan hari ini' dan 'yang belum bisa saya pastikan'. Kerjakan bagian pertama.")
            if re.search(r"\b(?:gagal|tidak akan|tidak bisa)\b", joined):
                add("Kalimat memprediksi hasil yang belum terjadi. Ubah prediksi menjadi rencana cadangan: jika hasilnya tidak sesuai harapan, apa langkah berikutnya?")
    
