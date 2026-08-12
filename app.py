import streamlit as st
import re
import random
import pandas as pd

st.set_page_config(page_title="SAED", page_icon="🧠", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.block-container {max-width: 850px; padding: 1.2rem 1rem 3rem;}
.hero {padding: 1.4rem; border-radius: 22px; background: linear-gradient(135deg,#172554,#312e81); color:white; margin-bottom:1rem;}
.hero h1 {font-size:2.2rem; margin:0;}.hero p {margin:.4rem 0 0; opacity:.9;}
.result {padding:1rem; border-radius:18px; background:#f8fafc; border:1px solid #e2e8f0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🧠 SAED</h1>
<p>Social Achievement Exposure Detection</p>
<p style="font-size:.85rem;color:#cbd5e1">Prototype NLP untuk mengenali pola perbandingan pencapaian dalam teks media sosial.</p>
</div>
""", unsafe_allow_html=True)

st.info("SAED merupakan prototype penelitian berbasis pola teks, bukan alat diagnosis psikologis.")

patterns = {
    "Achievement Exposure": [
        r"\bteman\w*\b.*\b(sukses|berhasil|kerja|bekerja|bisnis|gaji|rumah|lulus|prestasi|menang)\b",
        r"\b(orang|teman|mereka)\b.*\b(sudah|telah)\b.*\b(sukses|berhasil|kerja|bekerja|punya|mendapat|lulus)\b",
        r"\b(pencapaian|kesuksesan|keberhasilan|prestasi)\b"
    ],
    "Social Comparison": [
        r"\b(sedangkan|sementara|dibandingkan|bandingkan|dibanding)\b",
        r"\bmembandingkan\b",
        r"\b(seperti|kalah dari)\b.*\b(teman|orang|mereka)\b"
    ],
    "Negative Self-Evaluation": [
        r"\b(saya|aku)\b.*\b(gagal|tidak mampu|tidak punya apa-apa|tidak cukup|tidak berguna|payah|buruk)\b",
        r"\b(merasa|ngerasa|rasanya)\b.*\b(gagal|tidak mampu|buruk|rendah|tidak cukup|kurang|payah)\b"
    ],
    "Perceived Lagging": [
        r"\b(tertinggal|ketinggalan|berjalan lambat|jalan lambat|belum berkembang|belum maju)\b",
        r"\bbelum\b.*\b(apa-apa|mencapai|berhasil|sukses|punya|lulus|kerja)\b"
    ],
    "Future Uncertainty": [
        r"\b(tidak tahu|bingung|khawatir|takut|cemas)\b.*\b(masa depan|arah|ke depan|karier|kuliah|hidup)\b",
        r"\b(masa depan|ke depan)\b.*\b(tidak jelas|tidak tahu|takut|khawatir|bingung)\b"
    ]
}

# Banyak variasi respons agar output tidak terasa berulang.
RESPONSES = {
    "RENDAH": [
        "Teks menunjukkan sedikit pola perbandingan pencapaian. Fokus terhadap perkembangan diri masih terlihat cukup terjaga.",
        "Indikasi yang muncul relatif ringan. Tidak banyak tanda bahwa pencapaian orang lain sedang menjadi pusat perhatian dalam teks.",
        "Pola yang terdeteksi masih terbatas. Secara umum, teks belum menunjukkan kecenderungan perbandingan pencapaian yang kuat."
    ],
    "SEDANG": [
        "Beberapa pola perbandingan mulai terlihat. Pencapaian orang lain tampaknya cukup memengaruhi cara penulis melihat perkembangan dirinya.",
        "Terdapat indikasi moderat bahwa keberhasilan orang lain sedang dijadikan tolok ukur pribadi. Pola ini belum tentu menetap dan perlu dilihat dari konteks yang lebih luas.",
        "Hasil menunjukkan adanya beberapa sinyal yang perlu diperhatikan, terutama ketika pencapaian orang lain mulai dikaitkan dengan penilaian terhadap diri sendiri."
    ],
    "TINGGI": [
        "Teks memperlihatkan kombinasi indikator yang cukup kuat: paparan pencapaian orang lain, perbandingan sosial, serta evaluasi terhadap diri sendiri.",
        "Beberapa pola muncul secara bersamaan sehingga indikasinya tergolong tinggi. Fokus pada keberhasilan orang lain tampak berkaitan dengan persepsi terhadap posisi atau masa depan diri.",
        "Hasil menunjukkan sinyal yang lebih dominan. Teks banyak menghubungkan pencapaian orang lain dengan perasaan tertinggal, penilaian diri, atau kekhawatiran mengenai masa depan."
    ]
}

INDICATOR_DESC = {
    "Achievement Exposure": [
        "Teks menyinggung keberhasilan, pekerjaan, prestasi, atau pencapaian orang lain.",
        "Ada paparan terhadap cerita atau kondisi pencapaian pihak lain yang dapat menjadi bahan perbandingan.",
        "Pencapaian orang lain menjadi salah satu informasi penting dalam teks."
    ],
    "Social Comparison": [
        "Terdapat hubungan perbandingan antara kondisi diri dan orang lain.",
        "Teks menunjukkan bahwa posisi atau pencapaian orang lain digunakan sebagai pembanding.",
        "Ada kecenderungan melihat perkembangan diri melalui kondisi orang lain."
    ],
    "Negative Self-Evaluation": [
        "Penulis menggunakan penilaian yang kurang positif terhadap kemampuan atau kondisi dirinya.",
        "Terdapat ungkapan yang mengarah pada evaluasi diri secara negatif.",
        "Cara penulis menggambarkan dirinya mengandung unsur merendahkan atau meragukan kemampuan pribadi."
    ],
    "Perceived Lagging": [
        "Teks menggambarkan adanya perasaan belum mencapai posisi yang diharapkan.",
        "Terlihat persepsi bahwa perkembangan diri berjalan lebih lambat dibandingkan pihak lain.",
        "Penulis mengindikasikan adanya jarak antara kondisi sekarang dan pencapaian yang diinginkan."
    ],
    "Future Uncertainty": [
        "Terdapat keraguan atau kekhawatiran mengenai arah perkembangan di masa mendatang.",
        "Teks mengandung ketidakpastian tentang masa depan, karier, atau arah hidup.",
        "Penulis tampak belum yakin mengenai langkah atau kondisi yang akan datang."
    ]
}

RECOMMENDATIONS = {
    "RENDAH": [
        "Pertahankan fokus pada target pribadi dan jadikan media sosial sebagai sumber informasi, bukan ukuran nilai diri.",
        "Lanjutkan kebiasaan mengevaluasi kemajuan berdasarkan perkembangan diri sendiri dari waktu ke waktu.",
        "Gunakan pencapaian orang lain sebagai inspirasi seperlunya, sambil tetap menetapkan standar keberhasilan yang realistis untuk diri sendiri."
    ],
    "SEDANG": [
        "Coba kurangi paparan konten yang paling sering memicu perbandingan dan alihkan perhatian pada target yang dapat dikendalikan.",
        "Buat catatan perkembangan pribadi agar kemajuan tidak hanya diukur dari apa yang terlihat pada orang lain.",
        "Saat mulai membandingkan diri, identifikasi apakah informasi tersebut benar-benar relevan dengan tujuan pribadi atau hanya berasal dari paparan media sosial."
    ],
    "TINGGI": [
        "Pertimbangkan jeda dari konten yang memicu perbandingan, kemudian susun kembali target berdasarkan kondisi dan kebutuhan pribadi.",
        "Cobalah membatasi waktu atau akun yang membuat pencapaian orang lain terasa seperti ukuran keberhasilan diri. Jika perasaan ini terus mengganggu aktivitas sehari-hari, pertimbangkan berbicara dengan orang yang dipercaya atau tenaga profesional.",
        "Fokuskan evaluasi pada proses dan kemajuan diri sendiri. Bila tekanan atau kekhawatiran terasa semakin berat dan menetap, mencari dukungan dari orang tepercaya dapat menjadi langkah yang baik."
    ]
}

EXTRA_INSIGHTS = [
    "Perlu diingat bahwa satu teks belum cukup untuk menggambarkan kondisi seseorang secara keseluruhan.",
    "Hasil ini bergantung pada kata dan konteks yang muncul dalam teks yang dimasukkan.",
    "Interpretasi sebaiknya digunakan sebagai bahan refleksi atau penelitian, bukan sebagai label terhadap seseorang.",
    "Pola bahasa dapat berubah tergantung konteks, gaya menulis, dan situasi saat teks dibuat."
]

def normalize(text):
    t = text.lower()
    repl = {
        "temen":"teman", "temen2":"teman", "udh":"sudah", "udah":"sudah", "yg":"yang",
        "ga":"tidak", "gak":"tidak", "nggak":"tidak", "gk":"tidak", "blm":"belum",
        "org":"orang", "gue":"saya", "gw":"saya", "aku":"saya", "ngerasa":"merasa"
    }
    t = re.sub(r"http\S+|www\S+|@\w+|#\w+", " ", t)
    t = re.sub(r"[^a-zA-ZÀ-ÿ\s]", " ", t)
    return re.sub(r"\s+", " ", " ".join(repl.get(x, x) for x in t.split())).strip()

def detect(t):
    return {name: any(re.search(p, t) for p in pats) for name, pats in patterns.items()}

def level_from_score(score):
    if score >= 4:
        return "TINGGI", "🔴"
    if score >= 2:
        return "SEDANG", "🟡"
    return "RENDAH", "🟢"

def varied_response(level, active):
    seed = sum(ord(c) for c in (level + "|" + "|".join(active))) + len(active) * 17
    rng = random.Random(seed)
    return rng.choice(RESPONSES[level])

def varied_recommendation(level, active):
    seed = sum(ord(c) for c in (level + "|" + "|".join(active))) + 71
    rng = random.Random(seed)
    return rng.choice(RECOMMENDATIONS[level])

def indicator_description(name, detected, active):
    if not detected:
        return "Tidak ditemukan pola bahasa utama yang mengarah pada indikator ini."
    seed = sum(ord(c) for c in (name + "|" + "|".join(active)))
    return random.Random(seed).choice(INDICATOR_DESC[name])

text = st.text_area(
    "Masukkan teks yang ingin dianalisis",
    height=170,
    placeholder="Contoh: Teman saya sudah sukses semua, sedangkan saya masih bingung dengan masa depan saya."
)

col1, col2 = st.columns([3, 1])
with col1:
    analyze = st.button("🔎 ANALISIS TEKS", use_container_width=True, type="primary")
with col2:
    clear = st.button("↻ Reset", use_container_width=True)

if clear:
    st.rerun()

if analyze:
    if not text.strip():
        st.warning("Masukkan teks terlebih dahulu agar SAED dapat melakukan analisis.")
        st.stop()

    clean = normalize(text)
    ind = detect(clean)
    active = [k for k, v in ind.items() if v]
    score = len(active)
    level, icon = level_from_score(score)

    st.markdown(
        f'<div class="result"><h2>{icon} Indikasi {level}</h2>'
        f'<p>SAED menemukan <b>{score} dari 5</b> indikator utama pada teks.</p></div>',
        unsafe_allow_html=True
    )

    st.subheader("📊 Ringkasan indikator")
    chart = pd.DataFrame({
        "Indikator": list(ind.keys()),
        "Terdeteksi": [1 if ind[x] else 0 for x in ind]
    }).set_index("Indikator")
    st.bar_chart(chart)

    for name, detected in ind.items():
        st.write(("✅ " if detected else "⚪ ") + f"**{name}**")
        st.caption(indicator_description(name, detected, active))

    st.subheader("💬 Interpretasi SAED")
    st.write(varied_response(level, active))

    if active:
        st.write("**Pola yang muncul:** " + ", ".join(active) + ".")
    else:
        st.write("Belum ditemukan indikator utama dari lima kategori yang digunakan dalam prototype ini.")

    st.subheader("🌱 Saran yang sesuai")
    st.write(varied_recommendation(level, active))

    st.info(random.Random(score + len(clean)).choice(EXTRA_INSIGHTS))

    with st.expander("🔍 Lihat teks setelah preprocessing"):
        st.code(clean)

st.divider()
st.caption("SAED Prototype • NLP berbasis aturan untuk penelitian KTI • Bukan alat diagnosis psikologis.")
