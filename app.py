
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

# ---------- NLP prototype ----------
def analyze_text(t):
    s=t.lower()
    groups = {
        "Achievement Exposure": ["sukses","berhasil","prestasi","gaji","jabatan","lulus","menang","pencapaian","orang lain","teman","linkedin","instagram"],
        "Future Uncertainty": ["takut","khawatir","masa depan","besok","nanti","gagal","cemas","tidak yakin","bingung"],
        "Negative Self-Evaluation": ["aku tidak","saya tidak","kurang","jelek","bodoh","gagal","tidak mampu","rendah diri","tidak cukup","ketinggalan"],
        "Perceived Lagging": ["tertinggal","ketinggalan","belum punya","sementara mereka","sedangkan dia","telat","lambat"],
        "Social Comparison": ["dibanding","bandingkan","mereka lebih","dia lebih","teman-teman","orang lain","seumuran","lebih sukses"]
    }
    weights = {"Achievement Exposure":1.0,"Future Uncertainty":.82,"Negative Self-Evaluation":.78,"Perceived Lagging":.68,"Social Comparison":.72}
    scores={}
    hits={}
    for k, words in groups.items():
        found=[w for w in words if w in s]
        hits[k]=found
        base=min(1.0, len(found)*0.18 + (0.25 if found else 0))
        # richer heuristic for longer texts
        scores[k]=round(min(1.0, base + (0.08 if len(s)>180 and found else 0)),2)
    if not any(hits.values()):
        scores={"Achievement Exposure":.32,"Future Uncertainty":.24,"Negative Self-Evaluation":.20,"Perceived Lagging":.16,"Social Comparison":.14}
    overall=round(sum(scores.values())/len(scores)*100)
    peak=max(scores,key=scores.get)
    level="Rendah" if overall<35 else "Sedang" if overall<65 else "Tinggi"
    return scores,hits,overall,level,peak

if analyze:
    scores,hits,overall,level,peak=analyze_text(text)
else:
    scores={"Achievement Exposure":1.0,"Future Uncertainty":.58,"Negative Self-Evaluation":.42,"Perceived Lagging":.28,"Social Comparison":.21}
    hits={k:[] for k in scores}
    overall=56; level="Sedang"; peak="Achievement Exposure"

labels=list(scores.keys())
colors=["#20a9ff","#ffae32","#22c4ca","#7446f5","#f23883"]
def severity(v):
    return "Rendah" if v<.35 else "Sedang" if v<.65 else "Parah"
def detail(k,v):
    d={
    "Achievement Exposure":"Paparan terhadap pencapaian orang lain dan standar sosial yang terlihat dalam teks.",
    "Future Uncertainty":"Terdapat sinyal kekhawatiran, ketidakpastian, atau tekanan terhadap masa depan.",
    "Negative Self-Evaluation":"Muncul penilaian diri yang kurang positif atau keraguan terhadap kemampuan pribadi.",
    "Perceived Lagging":"Ada kesan tertinggal dari target, teman sebaya, atau ritme perkembangan yang diharapkan.",
    "Social Comparison":"Ada kecenderungan membandingkan kondisi diri dengan pencapaian orang lain."
    }
    return d[k]

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
    if peak=="Achievement Exposure":
        desc="Teks menunjukkan adanya paparan terhadap pencapaian pihak lain. Pola ini dapat berkaitan dengan fokus pada standar sosial, namun belum otomatis berarti perbandingan diri yang kuat."
    else:
        desc=f"Teks paling kuat menunjukkan pola **{peak}**. Indikasinya perlu dilihat bersama konteks kalimat, intensitas emosi, dan indikator lainnya."
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
        <br><span class="small">{detail(k,v)}</span></div>""",unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------- Deep analysis ----------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 🔍 Analisis Mendalam")
patterns = [
("🔵 Pola Utama", f"Indikator utama adalah {peak} dengan skor {scores[peak]:.2f}. Kata/frasa yang terdeteksi: {', '.join(hits.get(peak,[])) or 'belum ada kata kunci spesifik; skor menggunakan baseline prototipe'}."),
("🟠 Emosi & Tekanan", "Bahasa yang mengandung target, keberhasilan, kekhawatiran, atau evaluasi diri dapat menunjukkan campuran motivasi dan tekanan. Konteks kalimat tetap penting sebelum menarik kesimpulan."),
("🟣 Dampak Potensial", "Jika pola ini sering muncul, pengguna dapat terbantu dengan membatasi pemicu perbandingan, memecah target menjadi langkah kecil, dan mengukur kemajuan berdasarkan perkembangan diri sendiri."),
("🟢 Kekuatan", "Kemampuan mengenali pola pikiran dan menuliskan pengalaman secara reflektif merupakan modal untuk membangun kebiasaan evaluasi diri yang lebih sehat.")
]
for title,body in patterns:
    st.markdown(f"<div class='insight'><b>{title}</b><br>{body}</div>",unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ---------- Recommendations ----------
st.markdown('<div class="tip">', unsafe_allow_html=True)
st.markdown("### 🌱 Saran yang sesuai")
st.write("Berdasarkan pola analisis, berikut beberapa saran yang dapat kamu terapkan:")
recs=[
"Fokus pada target dan progres pribadimu. Bandingkan diri dengan versi dirimu yang kemarin, bukan dengan pencapaian orang lain.",
"Gunakan media sosial sebagai sumber inspirasi dan informasi, bukan sebagai tolok ukur nilai diri.",
"Batasi paparan konten yang memicu perbandingan, terutama saat merasa cemas atau kurang percaya diri.",
"Rayakan pencapaian kecil yang kamu raih. Konsistensi kecil tetap berarti besar dalam jangka panjang.",
"Jaga rutinitas dasar: tidur cukup, bergerak/olahraga ringan, makan teratur, dan melakukan aktivitas yang kamu nikmati.",
"Bicarakan perasaan dengan orang yang dipercaya ketika tekanan mulai terasa berat.",
"Coba journaling singkat: tulis 1 hal yang sudah berhasil dilakukan dan 1 langkah kecil untuk besok.",
"Ubah target besar menjadi tugas 10–20 menit agar kemajuan terasa lebih konkret.",
"Gunakan kalimat yang lebih realistis: 'Aku sedang belajar' daripada 'Aku tidak mampu'.",
"Atur jeda dari aplikasi atau akun yang membuatmu terus membandingkan diri.",
"Catat pencapaian pribadi mingguan agar kemajuan yang sering tidak terlihat menjadi lebih nyata.",
]
for r in recs:
    st.markdown(f"✅ {r}")
st.markdown("<div style='margin-top:12px;padding:12px;border-radius:12px;background:#3b3a1d'>💡 <i>“Progres yang lambat tetaplah progres. Fokus pada perjalananmu sendiri.”</i></div>",unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

with st.expander("🔎 Lihat teks setelah preprocessing"):
    cleaned=re.sub(r'\s+',' ',re.sub(r'[^a-zA-ZÀ-ÿ0-9\s]',' ',text.lower())).strip()
    st.code(cleaned or "Belum ada teks yang dianalisis.")

st.markdown("<div style='text-align:center;color:#66759a;padding:25px'>SAED • Social Achievement Exposure Detector • Prototype NLP</div>",unsafe_allow_html=True)
