import re
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="SAED - Social Achievement Exposure Detector",
    page_icon="🧠",
    layout="centered"
)

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at top left, #171c4a 0%, #0b1020 38%, #080b14 100%);
        color: #f5f7ff;
    }
    .block-container { max-width: 900px; padding-top: 1.2rem; padding-bottom: 3rem; }
    .top-header {
        padding: 1.1rem 1.3rem; border-radius: 22px;
        background: linear-gradient(135deg, #182b72, #22215c 55%, #301d68);
        border: 1px solid rgba(110, 130, 255, .35);
        box-shadow: 0 12px 35px rgba(30, 45, 130, .25); margin-bottom: 1rem;
    }
    .logo-title { font-size: 2rem; font-weight: 800; margin: 0; }
    .subtitle { color: #b8c4e8; font-size: .95rem; margin-top: .15rem; }
    .section-title { font-size: 1.35rem; font-weight: 800; margin-top: 1.25rem; margin-bottom: .7rem; }
    .result-card {
        padding: 1.2rem; border-radius: 22px;
        background: linear-gradient(135deg, rgba(31, 44, 101, .92), rgba(25, 22, 67, .94));
        border: 1px solid rgba(100, 130, 255, .28);
        box-shadow: 0 12px 30px rgba(0,0,0,.25); margin-top: 1rem;
    }
    .result-title { font-size: 1.3rem; font-weight: 800; }
    .pattern-badge {
        display: inline-block; padding: .35rem .75rem; border-radius: 999px;
        background: linear-gradient(90deg, #315cf5, #7048ff);
        color: white; font-weight: 700; margin: .35rem 0;
    }
    .level-box { text-align: center; padding: 1rem; border-radius: 18px; background: rgba(7, 10, 28, .48); }
    .level-number { font-size: 2rem; font-weight: 900; }
    .level-label { font-size: 1rem; font-weight: 700; color: #dbe4ff; }
    .indicator-card {
        padding: 1rem; border-radius: 17px; background: rgba(24, 30, 59, .85);
        border: 1px solid rgba(130, 145, 210, .18); margin-bottom: .7rem;
    }
    .indicator-name { font-weight: 800; font-size: 1rem; }
    .indicator-desc { color: #b7bed4; font-size: .87rem; line-height: 1.45; margin-top: .3rem; }
    .badge-low { background: #18a866; color: white; padding: .25rem .65rem; border-radius: 999px; font-weight: 800; font-size: .78rem; }
    .badge-medium { background: #e6a52e; color: #17120a; padding: .25rem .65rem; border-radius: 999px; font-weight: 800; font-size: .78rem; }
    .badge-high { background: #f04f5f; color: white; padding: .25rem .65rem; border-radius: 999px; font-weight: 800; font-size: .78rem; }
    .advice-box {
        padding: 1.15rem; border-radius: 22px;
        background: linear-gradient(135deg, rgba(9, 103, 98, .78), rgba(15, 68, 80, .82));
        border: 1px solid rgba(61, 225, 193, .25); margin-top: 1rem;
    }
    .advice-item { padding: .65rem .7rem; margin: .35rem 0; border-radius: 13px; background: rgba(4, 20, 28, .32); color: #e8ffff; }
    .quote-box {
        margin-top: .8rem; padding: .85rem 1rem; border-radius: 14px;
        background: rgba(238, 190, 61, .18); border: 1px solid rgba(238, 190, 61, .35);
        color: #fff0b0; font-style: italic;
    }
    .footer { color: #858ca5; font-size: .8rem; text-align: center; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid rgba(150,160,190,.15); }
    div.stButton > button { border-radius: 14px; font-weight: 800; min-height: 2.8rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-header">
    <div class="logo-title">🧠 SAED</div>
    <div class="subtitle">Social Achievement Exposure Detector · Prototype NLP</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">📝 Masukkan teks yang ingin dianalisis</div>', unsafe_allow_html=True)

text = st.text_area(
    "",
    placeholder="Tulis teks di sini... (misalnya keluhan, curhatan, atau opini)",
    height=150,
    max_chars=1000,
    label_visibility="collapsed"
)

st.caption(f"{len(text)}/1000")

col1, col2 = st.columns([3, 1])
with col1:
    analyze = st.button("🔎  ANALISIS TEKS  →", use_container_width=True, type="primary")
with col2:
    reset = st.button("↻  Reset", use_container_width=True)

if reset:
    st.rerun()

INDICATORS = {
    "Achievement Exposure": {
        "keywords": ["sukses", "berhasil", "prestasi", "pencapaian", "juara", "gaji", "kerja bagus", "naik jabatan", "wisuda", "lulus", "promosi", "achievement", "pencapaian orang", "orang lain berhasil"],
        "description": "Paparan terhadap pencapaian atau keberhasilan pihak lain.",
        "color": "#2997ff"
    },
    "Future Uncertainty": {
        "keywords": ["masa depan", "takut gagal", "khawatir", "cemas", "tidak tahu", "bingung", "nanti", "besok", "masa depanku", "tidak punya arah", "takut tidak berhasil"],
        "description": "Kekhawatiran atau ketidakpastian mengenai masa depan.",
        "color": "#ffae35"
    },
    "Negative Self-Evaluation": {
        "keywords": ["aku tidak bisa", "aku gagal", "aku buruk", "aku bodoh", "aku kurang", "tidak cukup", "tidak berguna", "tidak mampu", "rendah diri", "jelek", "tidak sehebat", "merasa gagal"],
        "description": "Munculnya penilaian diri yang cenderung negatif.",
        "color": "#24c5c7"
    },
    "Perceived Lagging": {
        "keywords": ["tertinggal", "ketinggalan", "telat", "teman sudah", "orang lain sudah", "sementara aku", "aku belum", "belum mencapai", "jauh di belakang", "semua sudah"],
        "description": "Perasaan bahwa perkembangan diri tertinggal dari orang lain.",
        "color": "#7a4cff"
    },
    "Social Comparison": {
        "keywords": ["membandingkan", "dibandingkan", "bandingkan", "lebih sukses", "lebih kaya", "lebih pintar", "lebih baik", "kalah dari", "saingan", "teman-teman", "orang lain lebih"],
        "description": "Kecenderungan membandingkan diri dengan orang lain.",
        "color": "#ec3d87"
    }
}

def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def calculate_scores(text):
    text = clean_text(text)
    scores = {}
    for name, data in INDICATORS.items():
        hits = sum(1 for keyword in data["keywords"] if keyword in text)
        scores[name] = round(min(hits / 4, 1.0), 2)
    return scores

def predicate(score):
    if score >= 0.70:
        return "Parah"
    elif score >= 0.40:
        return "Sedang"
    return "Rendah"

def predicate_class(level):
    if level == "Parah":
        return "badge-high"
    elif level == "Sedang":
        return "badge-medium"
    return "badge-low"

def overall_level(scores):
    highest = max(scores.values())
    if highest >= 0.70:
        return "Parah"
    elif highest >= 0.40:
        return "Sedang"
    return "Rendah"

def detect_pattern(scores):
    strongest = max(scores, key=scores.get)
    if scores[strongest] == 0:
        return "Belum ada pola dominan"
    return strongest

ADVICE = {
    "Achievement Exposure": [
        "Fokus pada target dan perkembangan pribadimu. Bandingkan dirimu dengan versi dirimu yang kemarin, bukan dengan pencapaian orang lain.",
        "Gunakan media sosial sebagai sumber inspirasi dan informasi, bukan sebagai tolok ukur nilai dirimu.",
        "Kurangi paparan konten pencapaian ketika mulai membuatmu merasa kurang atau tertinggal.",
        "Catat pencapaian kecil yang sudah kamu raih agar perkembanganmu sendiri tetap terlihat.",
        "Ingat bahwa setiap orang memiliki waktu, kondisi, dan jalur keberhasilan yang berbeda."
    ],
    "Future Uncertainty": [
        "Pecah kekhawatiran tentang masa depan menjadi target kecil yang bisa dikerjakan hari ini.",
        "Fokus pada hal yang masih bisa kamu kendalikan daripada mencoba memastikan semua hal yang belum terjadi.",
        "Buat rencana sederhana untuk satu minggu ke depan agar masa depan terasa lebih terarah.",
        "Tidak semua ketidakpastian harus segera memiliki jawaban. Beri ruang untuk proses.",
        "Evaluasi kemajuan secara berkala, bukan menuntut diri untuk langsung mengetahui seluruh arah hidup."
    ],
    "Negative Self-Evaluation": [
        "Hindari memberi label negatif pada dirimu hanya karena satu kegagalan atau kekurangan.",
        "Ganti kalimat 'aku tidak bisa' menjadi 'aku belum bisa dan masih bisa belajar'.",
        "Catat kemampuan dan hal-hal yang sudah berhasil kamu lakukan sebagai pengingat bahwa kemampuanmu terus berkembang.",
        "Berikan dirimu kesempatan untuk melakukan kesalahan tanpa menjadikannya ukuran nilai diri.",
        "Fokus pada proses belajar dan perbaikan, bukan hanya hasil akhir."
    ],
    "Perceived Lagging": [
        "Kecepatan perkembangan setiap orang berbeda. Tidak terlambat bukan berarti harus mengikuti jadwal orang lain.",
        "Tentukan ukuran keberhasilan yang sesuai dengan kondisi dan tujuanmu sendiri.",
        "Kurangi kebiasaan melihat pencapaian orang lain ketika hal tersebut membuatmu merasa tertinggal.",
        "Pilih satu kemajuan kecil yang bisa kamu lakukan minggu ini dan jadikan itu prioritas.",
        "Perjalanan yang lebih lambat tetap merupakan perjalanan selama kamu terus bergerak."
    ],
    "Social Comparison": [
        "Gunakan pencapaian orang lain sebagai referensi atau inspirasi, bukan sebagai ukuran harga dirimu.",
        "Batasi kebiasaan membandingkan kehidupan nyata dengan potongan kehidupan orang lain di media sosial.",
        "Ketika muncul perbandingan, tanyakan: 'Apa yang sebenarnya ingin aku capai untuk diriku sendiri?'",
        "Alihkan perhatian dari siapa yang lebih unggul menjadi apa yang bisa kamu tingkatkan.",
        "Bangun standar keberhasilan berdasarkan nilai dan tujuan pribadi."
    ]
}

def get_advice(scores):
    strongest = max(scores, key=scores.get)
    advice = ADVICE[strongest].copy()
    if scores[strongest] >= 0.70:
        advice.append("Pertimbangkan untuk mengambil jeda dari konten yang memicu tekanan dan mengembalikan fokus pada aktivitas yang membuatmu merasa lebih stabil.")
    return advice[:6]

if analyze:
    if not text.strip():
        st.warning("⚠️ Silakan masukkan teks terlebih dahulu.")
        st.stop()

    scores = calculate_scores(text)
    levels = {name: predicate(score) for name, score in scores.items()}
    overall = overall_level(scores)
    pattern = detect_pattern(scores)
    strongest_score = max(scores.values())

    st.markdown('<div class="section-title">📊 Hasil Analisis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.7])
    with col1:
        percent = int(strongest_score * 100)
        st.markdown(f"""
        <div class="level-box">
            <div style="font-size:.9rem;color:#aeb8d5;">Tingkat keseluruhan</div>
            <div class="level-number">{overall}</div>
            <div class="level-label">({percent}%)</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="result-card" style="margin-top:0;">
            <div class="result-title">📈 Pola yang terdeteksi</div>
            <div class="pattern-badge">{pattern}</div>
            <p style="color:#c7cee3;line-height:1.5;">
                Hasil menunjukkan indikator yang paling menonjol adalah <b>{pattern}</b>.
                Nilai indikator lain tetap ditampilkan agar hasil dapat dilihat secara lebih menyeluruh.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 Ringkasan Indikator</div>', unsafe_allow_html=True)

    names = list(scores.keys())
    values = [scores[n] for n in names]
    colors = [INDICATORS[n]["color"] for n in names]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=names, y=values,
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.2f}" for v in values],
        textposition="outside",
        textfont=dict(color="#ffffff", size=13),
        hovertemplate="<b>%{x}</b><br>Skor: %{y:.2f}<extra></extra>"
    ))
    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=30, b=100),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e9edff", size=12),
        yaxis=dict(range=[0, 1.12], tickformat=".1f", gridcolor="rgba(160,170,210,.14)", zerolinecolor="rgba(160,170,210,.20)", title="Skor"),
        xaxis=dict(tickangle=-25, gridcolor="rgba(0,0,0,0)"),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("Semakin tinggi skor, semakin kuat indikasi pola yang terdeteksi.")

    st.markdown('<div class="section-title">☷ Detail Indikator</div>', unsafe_allow_html=True)

    for name, score in scores.items():
        level = levels[name]
        badge = predicate_class(level)
        percent = int(score * 100)
        st.markdown(f"""
        <div class="indicator-card">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;">
                <div class="indicator-name">{name}</div>
                <span class="{badge}">{level}</span>
            </div>
            <div class="indicator-desc">
                {INDICATORS[name]["description"]}<br>
                <b style="color:#dfe5ff;">Skor: {percent}%</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🌱 Saran yang sesuai</div>', unsafe_allow_html=True)

    advice_list = get_advice(scores)
    st.markdown("""
    <div class="advice-box">
        <div style="font-size:1.35rem;font-weight:800;">🌱 Rekomendasi personal</div>
        <div style="color:#bdebe4;margin:.25rem 0 .7rem;">Berdasarkan indikator yang paling menonjol:</div>
    """, unsafe_allow_html=True)

    for advice in advice_list:
        st.markdown(f'<div class="advice-item">✓ &nbsp; {advice}</div>', unsafe_allow_html=True)

    quotes = {
        "Achievement Exposure": "Keberhasilan orang lain bukan bukti bahwa kamu gagal.",
        "Future Uncertainty": "Kamu tidak harus mengetahui seluruh jalan untuk mulai melangkah.",
        "Negative Self-Evaluation": "Satu kesalahan tidak menentukan seluruh kemampuanmu.",
        "Perceived Lagging": "Setiap orang memiliki garis waktu yang berbeda.",
        "Social Comparison": "Fokus pada perjalananmu sendiri, bukan perlombaan dengan orang lain.",
        "Belum ada pola dominan": "Tidak semua teks harus memiliki pola tertentu. Coba lihat kembali konteks dan makna keseluruhan teks."
    }

    st.markdown(f'<div class="quote-box">💡 “{quotes[pattern]}”</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("🔎 Lihat teks setelah preprocessing"):
        st.code(clean_text(text))

st.markdown("""
<div class="footer">
    SAED Prototype • NLP berbasis aturan untuk penelitian KTI
    <br>
    Bukan alat diagnosis psikologis.
</div>
""", unsafe_allow_html=True)
        
