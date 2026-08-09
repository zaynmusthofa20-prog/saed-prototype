
import streamlit as st
import re, pandas as pd
from pathlib import Path

st.set_page_config(page_title="SAED", page_icon="🧠", layout="centered", initial_sidebar_state="collapsed")

# ---------- Style ----------
st.markdown("""
<style>
.block-container {max-width: 850px; padding: 1.2rem 1rem 3rem;}
.hero {padding: 1.4rem; border-radius: 22px; background: linear-gradient(135deg,#172554,#312e81); color:white; margin-bottom:1rem;}
.hero h1 {font-size:2.2rem; margin:0;}
.hero p {margin:.4rem 0 0; opacity:.9;}
.card {padding:1rem; border:1px solid #e5e7eb; border-radius:16px; margin:.5rem 0; background:#fff;}
.small {font-size:.85rem; color:#64748b;}
.result {padding:1rem; border-radius:18px; background:#f8fafc; border:1px solid #e2e8f0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🧠 SAED</h1>
<p>Social Achievement Exposure Detection</p>
<p class="small" style="color:#cbd5e1">Prototype NLP untuk mengenali pola perbandingan pencapaian di media sosial</p>
</div>
""", unsafe_allow_html=True)

st.info("SAED adalah prototype penelitian. Hasil berupa indikasi berbasis pola teks, bukan diagnosis psikologis.")

# ---------- Simple demo classifier ----------
patterns = {
"Achievement Exposure": [r"\bteman\w*\b.*\b(sukses|berhasil|kerja|bekerja|bisnis|gaji|rumah|lulus|prestasi)\b",
                         r"\b(orang|teman|mereka)\b.*\b(sudah|telah)\b.*\b(sukses|berhasil|kerja|bekerja|punya|mendapat)\b",
                         r"\b(pencapaian|kesuksesan|keberhasilan)\b"],
"Social Comparison": [r"\b(sedangkan|sementara|dibandingkan|bandingkan|dibanding)\b",
                      r"\bmembandingkan\b", r"\bseperti\b.*\b(teman|orang|mereka)\b"],
"Negative Self-Evaluation": [r"\b(saya|aku)\b.*\b(gagal|tidak mampu|tidak punya apa-apa|tidak cukup)\b",
                             r"\bmerasa\b.*\b(gagal|tidak mampu|buruk|rendah|tidak cukup)\b"],
"Perceived Lagging": [r"\b(tertinggal|ketinggalan|berjalan lambat|jalan lambat|belum berkembang)\b",
                      r"\bbelum\b.*\b(apa-apa|mencapai|berhasil|sukses|punya)\b"],
"Future Uncertainty": [r"\b(tidak tahu|bingung|khawatir|takut)\b.*\b(masa depan|arah|ke depan)\b",
                       r"\b(masa depan|ke depan)\b.*\b(tidak jelas|tidak tahu|takut|khawatir)\b"]
}

def normalize(text):
    t = text.lower()
    repl = {"temen":"teman","temen2":"teman","udh":"sudah","udah":"sudah","yg":"yang",
            "ga":"tidak","gak":"tidak","nggak":"tidak","blm":"belum","org":"orang",
            "gini2":"seperti ini"}
    t = re.sub(r"http\S+|www\S+|@\w+|#\w+", " ", t)
    t = re.sub(r"[^a-zA-ZÀ-ÿ\s]", " ", t)
    return re.sub(r"\s+"," ", " ".join(repl.get(x,x) for x in t.split())).strip()

def detect(t):
    out={}
    for name, pats in patterns.items():
        out[name]=any(re.search(p,t) for p in pats)
    return out

text = st.text_area("Masukkan teks yang ingin dianalisis", height=170,
                    placeholder="Contoh: Teman saya sudah sukses semua, sedangkan saya masih bingung dengan masa depan saya.")

col1, col2 = st.columns([3,1])
with col1:
    analyze = st.button("🔎 ANALISIS TEKS", use_container_width=True, type="primary")
with col2:
    clear = st.button("↻ Reset", use_container_width=True)

if clear:
    st.rerun()

if analyze:
    if not text.strip():
        st.warning("Masukkan teks terlebih dahulu.")
        st.stop()

    clean=normalize(text)
    ind=detect(clean)
    score=sum(ind.values())

    # Prototype rule-based level. In the research version, replace this with trained SVM.
    if score >= 4: level="TINGGI"; icon="🔴"
    elif score >= 2: level="SEDANG"; icon="🟡"
    else: level="RENDAH"; icon="🟢"

    st.markdown(f'<div class="result"><h2>{icon} Indikasi {level}</h2>'
                f'<p>Teridentifikasi <b>{score}/5</b> indikator utama.</p></div>', unsafe_allow_html=True)

    st.subheader("📊 Indikator")
    labels=list(ind.keys())
    vals=[1 if ind[x] else 0 for x in labels]
    chart=pd.DataFrame({"Indikator":labels,"Terdeteksi":vals}).set_index("Indikator")
    st.bar_chart(chart)

    for k,v in ind.items():
        st.write(("✅ " if v else "⚪ ")+k)

    st.subheader("💡 Interpretasi")
    active=[k for k,v in ind.items() if v]
    if active:
        st.write("Pola yang terdeteksi: " + ", ".join(active) + ".")
    else:
        st.write("Tidak ditemukan pola indikator utama.")

    st.subheader("🌱 Rekomendasi")
    if level=="RENDAH":
        st.write("Pertahankan fokus pada tujuan pribadi dan gunakan media sosial secara seimbang.")
    elif level=="SEDANG":
        st.write("Coba kurangi paparan konten yang memicu perbandingan, tetapkan target pribadi, dan evaluasi perkembangan secara berkala.")
    else:
        st.write("Pertimbangkan membatasi paparan konten pemicu, berbicara dengan orang yang dipercaya, dan mencari bantuan profesional apabila kondisi terus mengganggu aktivitas sehari-hari.")

    with st.expander("🔍 Lihat teks setelah preprocessing"):
        st.code(clean)

st.divider()
st.caption("SAED Prototype • Untuk penelitian KTI. Bukan alat diagnosis psikologis.")
