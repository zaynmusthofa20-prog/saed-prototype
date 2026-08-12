import re
import html
from collections import Counter

import streamlit as st
import plotly.graph_objects as go


# ============================================================
# SAED v9 — SEMANTIC CONTEXT ANALYZER
# ============================================================

st.set_page_config(
    page_title="SAED — Semantic Analyzer",
    page_icon="◈",
    layout="wide"
)


# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(
            circle at 90% 0%,
            #16366d55,
            transparent 35%
        ),
        linear-gradient(
            180deg,
            #030817,
            #020611
        );
    color: #eef5ff;
}

.block-container {
    max-width: 1200px;
    padding: 1rem 1rem 3rem;
}

.hero,
.card {
    background:
        linear-gradient(
            145deg,
            #0c1d42ee,
            #050d20f5
        );
    border: 1px solid #244275;
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 10px 35px #0005;
}

.hero {
    border-color: #3561a8;
}

.small {
    color: #9eb2d8;
    font-size: 0.88rem;
}

.badge {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 99px;
    background: #0c315f;
    color: #6de5ff;
    font-weight: 800;
    font-size: 0.78rem;
}

.step,
.metric,
.evidence,
.sentence,
.pattern,
.context {
    background: #081633;
    border: 1px solid #203866;
    border-radius: 14px;
    padding: 12px;
    margin: 7px 0;
}

.step {
    min-height: 72px;
}

.stepno {
    display: inline-flex;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #153166;
    color: #70e0ff;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    margin-right: 7px;
}

.metric {
    min-height: 95px;
}

.evidence {
    border-left: 4px solid #20cfff;
}

.pattern {
    border-color: #29457b;
}

.dot {
    display: inline-block;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #20cfff;
    margin-right: 8px;
}

.tip {
    background:
        linear-gradient(
            100deg,
            #062e35,
            #102c3c
        );
    border: 1px solid #147f7a;
    border-radius: 18px;
    padding: 17px;
}

.warning {
    background: #33280c;
    border: 1px solid #6d5a20;
    border-radius: 14px;
    padding: 12px;
}

div[data-testid="stTextArea"] textarea {
    background: #07142d !important;
    color: #eef5ff !important;
    border: 1px solid #294579 !important;
    border-radius: 15px !important;
}

.stButton > button {
    border-radius: 12px !important;
    font-weight: 800 !important;
    min-height: 42px !important;
}

hr {
    border-color: #1b315c;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# LEXICON / INDIKATOR
# ============================================================

LEX = {

    "Achievement Exposure": [
        "sukses",
        "berhasil",
        "prestasi",
        "pencapaian",
        "lulus",
        "wisuda",
        "diterima kerja",
        "dapat kerja",
        "pekerjaan",
        "naik jabatan",
        "promosi",
        "gaji besar",
        "menang",
        "juara",
        "menikah",
        "punya rumah",
        "punya mobil",
        "bisnis",
        "karier bagus",
        "karir bagus",
        "mapan",
        "diterima kuliah"
    ],

    "Social Comparison": [
        "dibanding",
        "dibandingkan",
        "perbandingan",
        "berbeda dengan",
        "tidak seperti",
        "nggak seperti",
        "gak seperti",
        "seperti mereka",
        "kayak mereka",
        "lebih sukses",
        "lebih maju",
        "lebih kaya",
        "lebih baik",
        "lebih rendah",
        "lebih tinggi",
        "kalah dari",
        "tidak selevel",
        "tidak setara",
        "kok mereka",
        "kenapa mereka",
        "kenapa aku",
        "kenapa saya",
        "sementara mereka",
        "sedangkan mereka",
        "mereka sudah",
        "teman sudah"
    ],

    "Perceived Lagging": [
        "tertinggal",
        "ketinggalan",
        "terlambat",
        "belum mencapai",
        "belum punya",
        "belum berhasil",
        "belum dapat",
        "belum mendapatkan",
        "belum kerja",
        "belum bekerja",
        "belum lulus",
        "belum menikah",
        "belum mapan",
        "belum sukses",
        "jalan di tempat",
        "stuck",
        "tidak berkembang",
        "nggak berkembang",
        "gak berkembang",
        "masih belum",
        "belum sampai",
        "belum seperti",
        "masih bingung",
        "belum ada"
    ],

    "Negative Self-Evaluation": [
        "aku merasa bodoh",
        "saya merasa bodoh",
        "aku merasa gagal",
        "saya merasa gagal",
        "aku gagal",
        "saya gagal",
        "gue gagal",
        "aku bodoh",
        "saya bodoh",
        "aku payah",
        "saya payah",
        "aku tidak mampu",
        "saya tidak mampu",
        "aku nggak mampu",
        "saya nggak mampu",
        "aku gak mampu",
        "saya gak mampu",
        "aku tidak cukup",
        "saya tidak cukup",
        "aku gak cukup",
        "saya gak cukup",
        "aku tidak berguna",
        "saya tidak berguna",
        "aku tidak layak",
        "saya tidak layak",
        "aku jelek",
        "saya jelek",
        "rendah diri",
        "tidak berharga",
        "nggak berharga",
        "gak berharga",
        "tidak pintar",
        "nggak pintar",
        "gak pintar",
        "mengecewakan"
    ],

    "Future Uncertainty": [
        "masa depan",
        "ke depan",
        "nanti",
        "besok",
        "tahun depan",
        "karier",
        "karir",
        "pekerjaan",
        "akan",
        "rencana",
        "tujuan",
        "arah hidup",
        "setelah ini",
        "nantinya",
        "5 tahun",
        "beberapa tahun",
        "takut",
        "khawatir",
        "cemas",
        "bingung",
        "ragu",
        "tidak yakin",
        "nggak yakin",
        "gak yakin",
        "tidak tahu",
        "nggak tahu",
        "gak tahu",
        "belum tahu",
        "entah",
        "was-was",
        "kepikiran",
        "takut gagal",
        "panik",
        "gelisah",
        "insecure",
        "overthinking"
    ]
}


EXPOSURE = [
    "lihat",
    "melihat",
    "postingan",
    "posting",
    "story",
    "feed",
    "instagram",
    "tiktok",
    "linkedin",
    "media sosial",
    "sosmed",
    "mendengar",
    "dengar",
    "kabar",
    "konten"
]


OTHERS = [
    "teman",
    "teman-teman",
    "temen",
    "mereka",
    "orang lain",
    "orang-orang",
    "rekan",
    "kenalan",
    "seumuran",
    "sebaya",
    "circle"
]


EMOTION = {

    "Cemas": [
        "takut",
        "khawatir",
        "cemas",
        "panik",
        "gelisah",
        "was-was",
        "overthinking"
    ],

    "Tidak Aman": [
        "insecure",
        "ragu",
        "tidak yakin",
        "nggak yakin",
        "gak yakin"
    ],

    "Sedih": [
        "sedih",
        "kecewa",
        "menyesal",
        "murung"
    ],

    "Frustrasi": [
        "stuck",
        "jalan di tempat",
        "kesal",
        "frustrasi",
        "capek",
        "lelah"
    ],

    "Harapan": [
        "berharap",
        "ingin",
        "mau",
        "semoga",
        "berusaha",
        "mencoba"
    ]
}


CONTEXT = {

    "Media Sosial": EXPOSURE,

    "Lingkungan Sosial": OTHERS,

    "Pencapaian": LEX["Achievement Exposure"],

    "Evaluasi Diri": LEX["Negative Self-Evaluation"],

    "Karier & Masa Depan": LEX["Future Uncertainty"]
}


INFO = {

    "Achievement Exposure":
        "Paparan atau perhatian pada pencapaian orang lain.",

    "Social Comparison":
        "Evaluasi diri dengan menjadikan orang lain sebagai pembanding.",

    "Perceived Lagging":
        "Persepsi bahwa diri sendiri tertinggal dari target atau orang lain.",

    "Negative Self-Evaluation":
        "Penilaian negatif yang diarahkan kepada diri sendiri.",

    "Future Uncertainty":
        "Keraguan, takut, bingung, atau cemas mengenai arah masa depan."
}


RECS = {

    "Achievement Exposure": [
        "Pisahkan fakta pencapaian orang lain dari nilai dirimu sendiri.",
        "Batasi paparan konten pencapaian bila setelah melihatnya kamu langsung menilai diri."
    ],

    "Social Comparison": [
        "Ganti pembanding eksternal dengan milestone pribadi yang terukur.",
        "Bandingkan dirimu dengan kondisi beberapa bulan lalu, bukan timeline orang lain."
    ],

    "Perceived Lagging": [
        "Ubah kata 'tertinggal' menjadi target spesifik: apa yang sebenarnya belum tercapai?",
        "Pilih satu langkah kecil yang realistis untuk 24 jam ke depan."
    ],

    "Negative Self-Evaluation": [
        "Hindari label menyeluruh seperti 'aku gagal'; ubah menjadi masalah yang spesifik.",
        "Catat bukti kemampuan, usaha, dan kemajuan yang sudah ada."
    ],

    "Future Uncertainty": [
        "Pisahkan hal yang bisa dikendalikan hari ini dari hal yang belum bisa dipastikan.",
        "Buat rencana 1–4 minggu daripada mencoba memastikan seluruh masa depan."
    ]
}


# ============================================================
# FUNGSI NLP
# ============================================================

def norm(text):

    text = text.lower()

    text = text.replace("’", "'")

    text = re.sub(
        r"[^a-z0-9\s.!?,'\-]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def split_sentences(text):

    return [
        x.strip()
        for x in re.split(
            r"(?<=[.!?])\s+|\n+",
            text
        )
        if x.strip()
    ]


def hit(text, phrase):

    return bool(
        re.search(
            r"(?<!\w)"
            + re.escape(phrase)
            + r"(?!\w)",
            text
        )
    )


def active(text, phrase):

    for match in re.finditer(
        r"(?<!\w)"
        + re.escape(phrase)
        + r"(?!\w)",
        text
    ):

        before = text[
            max(0, match.start() - 18):
            match.start()
        ]

        if re.search(
            r"\b(tidak|tak|bukan|nggak|gak|ga)\s*$",
            before
        ):
            continue

        return True

    return False


def score_level(score):

    if score < 35:
        return "Rendah"

    if score < 65:
        return "Sedang"

    return "Tinggi"


# ============================================================
# ANALYZER
# ============================================================

def analyze(text):

    clean = norm(text)

    sentence_list = split_sentences(clean)

    scores = {
        key: 0.0
        for key in LEX
    }

    triggers = {
        key: []
        for key in LEX
    }

    evidence = {
        key: []
        for key in LEX
    }

    reports = []

    for index, sentence in enumerate(
        sentence_list,
        1
    ):

        rules = []

        for name, words in LEX.items():

            found = [
                word
                for word in words
                if active(sentence, word)
            ]

            if not found:
                continue

            confidence = min(
                0.98,
                0.35 + (0.12 * len(found))
            )

            if (
                name == "Social Comparison"
                and (
                    hit(sentence, "teman")
                    or hit(sentence, "mereka")
                )
            ):
                confidence = min(
                    1.0,
                    confidence + 0.08
                )

            if (
                name == "Perceived Lagging"
                and any(
                    x in sentence
                    for x in [
                        "aku",
                        "saya",
                        "gue",
                        "gua",
                        "gw"
                    ]
                )
            ):
                confidence = min(
                    1.0,
                    confidence + 0.08
                )

            if (
                name == "Negative Self-Evaluation"
                and any(
                    x in sentence
                    for x in [
                        "aku",
                        "saya",
                        "gue",
                        "gua",
                        "gw"
                    ]
                )
            ):
                confidence = min(
                    1.0,
                    confidence + 0.12
                )

            rules.append(
                (
                    name,
                    confidence,
                    found,
                    INFO[name]
                )
            )

            triggers[name].extend(found)

            evidence[name].append(
                (
                    index,
                    sentence
                )
            )

            scores[name] = max(
                scores[name],
                confidence
            )

        reports.append(
            {
                "index": index,
                "text": sentence,
                "rules": rules
            }
        )

    full_text = " ".join(sentence_list)

    # Reinforcement antar konteks

    if (
        active(full_text, "melihat")
        and (
            active(full_text, "teman")
            or active(full_text, "mereka")
        )
        and scores["Achievement Exposure"] > 0
    ):

        scores["Achievement Exposure"] = min(
            1.0,
            scores["Achievement Exposure"] + 0.10
        )

    if (
        scores["Social Comparison"] > 0
        and scores["Perceived Lagging"] > 0
    ):

        scores["Social Comparison"] = min(
            1.0,
            scores["Social Comparison"] + 0.08
        )

        scores["Perceived Lagging"] = min(
            1.0,
            scores["Perceived Lagging"] + 0.08
        )

    # Hilangkan duplikat trigger

    for key in triggers:

        triggers[key] = list(
            dict.fromkeys(
                triggers[key]
            )
        )

    # Emosi

    emotions = Counter()

    for emotion_name, words in EMOTION.items():

        count = sum(
            1
            for word in words
            if active(full_text, word)
        )

        if count:
            emotions[emotion_name] = count

    # Konteks

    contexts = Counter()

    for context_name, words in CONTEXT.items():

        count = sum(
            1
            for word in words
            if active(full_text, word)
        )

        if count:
            contexts[context_name] = count

    pattern_count = sum(
        len(item["rules"])
        for item in reports
    )

    return {
        "scores": scores,
        "triggers": triggers,
        "evidence": evidence,
        "reports": reports,
        "sentences": sentence_list,
        "emotions": emotions,
        "contexts": contexts,
        "patterns": pattern_count
    }


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>◈ SAED</h1>
        <h3>Semantic Context Analyzer</h3>
        <span class="small">
        Analisis pola kalimat Bahasa Indonesia secara rinci
        dengan indikator, bukti, konteks, dan saran.
        </span>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## ⚙️ Pengaturan")

    st.caption(
        "Rule-based NLP • tanpa API eksternal"
    )

    example = (
        "Aku sering melihat teman-teman sukses "
        "di media sosial. Mereka sudah punya "
        "pekerjaan dan aku merasa tertinggal. "
        "Aku takut masa depanku tidak jelas "
        "dan merasa gagal."
    )

    if st.button(
        "Muat contoh",
        use_container_width=True
    ):

        st.session_state["text"] = example

    if st.button(
        "Reset",
        use_container_width=True
    ):

        st.session_state["text"] = ""

    st.markdown("---")

    st.markdown("**Indikator yang dianalisis:**")

    for key in LEX:

        st.caption(
            "• " + key
        )


# ============================================================
# INPUT
# ============================================================

text = st.text_area(
    "📝 Masukkan teks yang ingin dianalisis",
    value=st.session_state.get(
        "text",
        ""
    ),
    height=190,
    max_chars=4000,
    placeholder=(
        "Contoh: Aku melihat teman-temanku "
        "sudah berhasil, sementara aku masih "
        "bingung dengan masa depan..."
    )
)


col1, col2 = st.columns(
    [1, 1]
)


with col1:

    run = st.button(
        "🔎 ANALISIS SEKARANG",
        type="primary",
        use_container_width=True
    )


with col2:

    st.caption(
        f"{len(text)}/4000 karakter"
    )


# ============================================================
# ANALYSIS TRIGGER
# ============================================================

if not run and not text.strip():

    st.info(
        "Masukkan teks lalu tekan "
        "**ANALISIS SEKARANG**."
    )

    st.stop()


result = analyze(text)


scores = result["scores"]

ranked = sorted(
    scores.items(),
    key=lambda item: item[1],
    reverse=True
)

reports = result["reports"]

emotions = result["emotions"]

contexts = result["contexts"]

overall = (
    round(ranked[0][1] * 100)
    if ranked
    and ranked[0][1] > 0
    else 0
)

peak = (
    ranked[0][0]
    if overall
    else "Belum terdeteksi"
)

level = score_level(
    overall
)


# ============================================================
# PROCESS
# ============================================================

st.markdown(
    "### 1 · Proses Analisis"
)

process = [

    (
        "01",
        "Preprocessing",
        "Normalisasi teks",
        bool(text.strip())
    ),

    (
        "02",
        "Segmentasi",
        f"{len(result['sentences'])} kalimat",
        bool(result["sentences"])
    ),

    (
        "03",
        "Pola Bahasa",
        f"{result['patterns']} pola",
        result["patterns"] > 0
    ),

    (
        "04",
        "Semantic Context",
        f"{len(contexts)} konteks",
        bool(contexts)
    ),

    (
        "05",
        "Confidence",
        f"{overall}%",
        overall > 0
    )
]


cols = st.columns(5)


for col, item in zip(
    cols,
    process
):

    number, title, description, done = item

    with col:

        st.markdown(
            f"""
            <div class="step">
                <span class="stepno">
                    {"✓" if done else number}
                </span>

                <b>{title}</b>

                <br>

                <span class="small">
                    {description}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# MAIN RESULT
# ============================================================

st.markdown(
    "### 2 · Hasil Utama"
)


g1, g2, g3 = st.columns(
    [1.1, 1, 1]
)


with g1:

    gauge = go.Figure(
        go.Pie(
            values=[
                overall,
                max(
                    100 - overall,
                    0
                )
            ],
            hole=0.76,
            sort=False,
            marker=dict(
                colors=[
                    "#20cfff",
                    "#162b5d"
                ]
            ),
            textinfo="none"
        )
    )
    gauge.update_layout(
        height=270,
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        ),
        paper_bgcolor=(
            "rgba(0,0,0,0)"
        ),
        showlegend=False,
        annotations=[
            dict(
                text=(
                    f"<b>{overall}%</b>"
                    f"<br>"
                    f"<span style='font-size:15px'>"
                    f"{level}"
                    f"</span>"
                ),
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(
                    size=30,
                    color="white"
                )
            )
        ]
    )

    st.plotly_chart(
        gauge,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )


with g2:

    st.markdown(
        f"""
        <div class="metric">

        <b>Indikator Terkuat</b>

        <h3>
        {html.escape(peak)}
        </h3>

        <span class="badge">
        {overall}% · {level}
        </span>

        <p class="small">
        {html.escape(
            INFO.get(
                peak,
                "Belum ada indikator kuat."
            )
        )}
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


with g3:

    st.markdown(
        f"""
        <div class="metric">

        <b>Ringkasan</b>

        <p>
        • {len(reports)} kalimat
        </p>

        <p>
        • {result["patterns"]} pola
        </p>

        <p>
        • {sum(emotions.values())}
        sinyal emosi
        </p>

        <p>
        • {len(contexts)}
        konteks
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PROFILE INDICATORS
# ============================================================

st.markdown(
    "### 3 · Profil 5 Indikator"
)


labels = list(LEX)

values = [
    round(
        scores[key] * 100
    )
    for key in labels
]


chart = go.Figure(
    go.Bar(
        x=values,
        y=labels,
        orientation="h",
        text=[
            f"{value}%"
            for value in values
        ],
        textposition="outside",
        marker=dict(
            color=[
                "#20cfff",
                "#ff6680",
                "#8b5cf6",
                "#f6ad55",
                "#22c4ca"
            ]
        )
    )
)


chart.update_xaxes(
    range=[0, 105],
    dtick=20,
    ticksuffix="%",
    gridcolor="#1a2d56"
)


chart.update_layout(
    height=330,
    margin=dict(
        l=0,
        r=45,
        t=10,
        b=10
    ),
    paper_bgcolor=(
        "rgba(0,0,0,0)"
    ),
    plot_bgcolor=(
        "rgba(0,0,0,0)"
    ),
    font_color="#dce7ff",
    showlegend=False
)


st.plotly_chart(
    chart,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)


# ============================================================
# DETAILED SENTENCE ANALYSIS
# ============================================================

st.markdown(
    "### 4 · Analisis Pola Kalimat Rinci"
)


for report in reports:

    st.markdown(
        f"""
        <div class="sentence">

        <b>
        Kalimat {report["index"]}
        </b>

        <br>

        {html.escape(
            report["text"]
        )}

        </div>
        """,
        unsafe_allow_html=True
    )

    if report["rules"]:

        for (
            name,
            confidence,
            found,
            description
        ) in report["rules"]:

            st.markdown(
                f"""
                <div class="pattern">

                <span class="dot"></span>

                <div>

                <b>
                {html.escape(name)}
                </b>

                <span class="badge">
                {round(confidence * 100)}%
                </span>

                <br>

                <span class="small">
                {html.escape(description)}
                </span>

                <br>

                <span class="small">
                <b>Pemicu:</b>
                {html.escape(
                    ", ".join(found)
                )}
                </span>

                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.caption(
            "↳ Belum ada pola kuat pada kalimat ini."
        )


# ============================================================
# EVIDENCE
# ============================================================

st.markdown(
    "### 5 · Bukti, Emosi & Konteks"
)


left, right = st.columns(2)


with left:

    st.markdown(
        "<div class='card'>"
        "<h4>🔎 Bukti Deteksi</h4>",
        unsafe_allow_html=True
    )

    found_any = False

    for key in labels:

        percentage = round(
            scores[key] * 100
        )

        if percentage == 0:
            continue

        found_any = True

        st.markdown(
            f"""
            <div class="evidence">

            <b>
            {html.escape(key)}
            </b>

            <span style="float:right">
            {percentage}%
            </span>

            <br>

            <span class="small">
            {html.escape(INFO[key])}
            </span>

            <br>

            <span class="small">
            <b>Frasa:</b>
            {html.escape(
                ", ".join(
                    result["triggers"][key]
                )
                or "—"
            )}
            </span>

            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander(
            "Lihat kalimat bukti · "
            + key
        ):

            for number, sentence in result[
                "evidence"
            ][key]:

                st.write(
                    f"Kalimat {number}: "
                    f"{sentence}"
                )

    if not found_any:

        st.caption(
            "Belum ada indikator kuat."
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# EMOTION + CONTEXT
# ============================================================

with right:

    st.markdown(
        "<div class='card'>"
        "<h4>🧠 Emosi</h4>",
        unsafe_allow_html=True
    )

    if emotions:

        total = sum(
            emotions.values()
        )

        for name, count in emotions.most_common():

            st.progress(
                count / total,
                text=(
                    f"{name} · "
                    f"{round(count / total * 100)}%"
                )
            )

    else:

        st.caption(
            "Belum ada sinyal emosi kuat."
        )


    st.markdown(
        "<h4>🌐 Konteks</h4>",
        unsafe_allow_html=True
    )


    if contexts:

        for name, count in contexts.most_common():

            st.markdown(
                f"""
                <div class="context">

                <b>
                {html.escape(name)}
                </b>

                <br>

                <span class="small">
                {count} sinyal kata/frasa
                </span>

                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.caption(
            "Belum ada konteks utama."
        )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# INSIGHT & RECOMMENDATION
# ============================================================

st.markdown(
    "### 6 · Insight & Saran"
)


left, right = st.columns(2)


active_keys = [
    key
    for key, value in ranked
    if value >= 0.35
]


with left:

    st.markdown(
        "<div class='card'>"
        "<h4>💡 Insight Utama</h4>",
        unsafe_allow_html=True
    )

    if overall:

        st.write(
            f"Pola paling kuat: "
            f"**{peak} ({overall}%)**."
        )

        if (
            "Social Comparison"
            in active_keys
            and
            "Perceived Lagging"
            in active_keys
        ):

            st.info(
                "Terlihat hubungan antara "
                "membandingkan diri dengan "
                "orang lain dan merasa tertinggal."
            )

        elif (
            "Achievement Exposure"
            in active_keys
            and
            "Social Comparison"
            in active_keys
        ):

            st.info(
                "Pencapaian orang lain tampak "
                "menjadi bahan pembanding "
                "terhadap diri sendiri."
            )

        elif (
            "Future Uncertainty"
            in active_keys
        ):

            st.info(
                "Ada sinyal ketidakpastian "
                "atau kekhawatiran mengenai "
                "masa depan."
            )

    else:

        st.write(
            "Belum ada pola kuat yang "
            "terdeteksi. Tambahkan beberapa "
            "kalimat yang memiliki konteks "
            "lebih jelas."
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


with right:

    st.markdown(
        "<div class='tip'>"
        "<h4>🌱 Saran yang Sesuai</h4>",
        unsafe_allow_html=True
    )

    recommendations = []

    for key in active_keys:

        recommendations.extend(
            RECS[key]
        )

    if not recommendations:

        recommendations = [

            "Gunakan milestone pribadi "
            "yang spesifik untuk mengukur progres.",

            "Pisahkan fakta pencapaian "
            "orang lain dari penilaian "
            "terhadap dirimu.",

            "Catat satu kemajuan kecil "
            "yang sudah terjadi minggu ini."
        ]

    for index, recommendation in enumerate(
        recommendations[:7],
        1
    ):

        st.markdown(
            f"**{index}.** {recommendation}"
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#7185ad;
        padding:25px;
    ">

    ◈ <b>SAED v9</b>
    · Detailed Semantic Pattern Analyzer

    <br>

    <span class="small">
    Rule-based NLP,
    bukan diagnosis psikologis
    atau penilaian klinis.
    </span>

    </div>
    """,
    unsafe_allow_html=True
    )
    
