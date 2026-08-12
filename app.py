import re
import streamlit as st
import plotly.graph_objects as go

# =========================================================
# SAED v3.0 — UI redesigned to match the provided mockup
# =========================================================
st.set_page_config(
    page_title="SAED - Social Achievement Exposure Detector",
    page_icon="🧠",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 50% -10%, rgba(49,70,190,.42), transparent 35%),
        radial-gradient(circle at 0% 30%, rgba(47,25,130,.20), transparent 32%),
        #060b19;
    color:#f7f8ff;
}
.block-container{max-width:900px;padding:1rem .9rem 3rem}
.top-header{
    padding:1.15rem 1.35rem;border-radius:24px;
    background:linear-gradient(135deg,#102a72,#17245e 55%,#24145d);
    border:1px solid rgba(83,119,255,.42);
    box-shadow:0 16px 40px rgba(0,0,0,.32);margin-bottom:1rem;
}
.brand{display:flex;align-items:center;gap:13px}
.brain{font-size:2.6rem;line-height:1}
.logo-title{font-size:2rem;font-weight:900;letter-spacing:-.02em}
.subtitle{color:#b9c7ed;font-size:.92rem;margin-top:.05rem}
.proto{
    float:right;margin-top:-3.2rem;padding:.45rem .8rem;border-radius:999px;
    background:linear-gradient(90deg,#263c9d,#4a32c9);
    border:1px solid rgba(132,151,255,.4);font-weight:700;font-size:.82rem
}
.section-title{font-size:1.35rem;font-weight:900;margin:1rem 0 .65rem}
.input-card,.result-card,.chart-card,.detail-card,.advice-box,.pre-card{
    border-radius:22px;border:1px solid rgba(88,117,207,.30);
    background:linear-gradient(145deg,rgba(16,27,67,.94),rgba(8,17,42,.96));
    box-shadow:0 14px 35px rgba(0,0,0,.22)
}
.input-card{padding:1rem 1.05rem}
textarea{border-radius:16px!important}
div.stButton>button{border-radius:14px;font-weight:850;min-height:2.8rem}
.result-wrap{display:grid;grid-template-columns:210px 1fr;gap:1rem;margin-top:1rem}
.result-card{padding:1.2rem}
.level{
    min-height:210px;display:flex;flex-direction:column;align-items:center;
    justify-content:center;text-align:center;border-radius:22px;
    background:radial-gradient(circle,#172b69,#09132e 68%);
}
.level-ring{
    width:150px;height:150px;border-radius:50%;
    background:conic-gradient(#16c9ef 0deg,#3158ff 185deg,#7b24ff 250deg,#26356e 250deg);
    display:grid;place-items:center;position:relative;
}
.level-ring:after{content:"";width:116px;height:116px;border-radius:50%;background:#09132e;position:absolute}
.level-inside{position:relative;z-index:2}
.level-number{font-size:1.8rem;font-weight:950}
.level-percent{color:#dbe3ff}
.result-title{font-size:1.35rem;font-weight:900}
.pattern{display:inline-block;margin:.45rem 0;padding:.42rem .8rem;border-radius:999px;background:linear-gradient(90deg,#176fc8,#384cff);font-weight:800;color:#7fe7ff}
.result-text{color:#cbd3eb;line-height:1.55}
.chart-card{padding:1rem;margin-top:1rem}
.badge{display:inline-block;padding:.28rem .68rem;border-radius:999px;font-size:.75rem;font-weight:900}
.low{background:#0b9f68;color:#eafff6}.medium{background:#e6a72d;color:#1d1605}.high{background:#ef4f69;color:#fff}
.detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:.75rem}
.detail-card{padding:.9rem}
.detail-top{display:flex;align-items:center;justify-content:space-between;gap:8px}
.detail-name{font-weight:850}.detail-desc{color:#b8c2df;font-size:.82rem;line-height:1.4;margin-top:.4rem}
.icon{width:34px;height:34px;display:inline-grid;place-items:center;border-radius:9px;background:#2949ff;margin-right:8px}
.advice-box{padding:1rem;margin-top:1rem;background:linear-gradient(135deg,rgba(0,99,91,.78),rgba(7,48,62,.90));border-color:rgba(38,211,178,.35)}
.advice-item{padding:.6rem .7rem;margin:.35rem 0;border-radius:13px;background:rgba(0,18,28,.30);color:#e5ffff}
.quote{margin-top:.65rem;padding:.75rem 1rem;border-radius:13px;background:rgba(228,181,53,.17);border:1px solid rgba(228,181,53,.35);color:#fff1ad;font-style:italic}
.footer{text-align:center;color:#77819e;font-size:.76rem;margin-top:1.4rem}
@media(max-width:650px){.result-wrap{grid-template-columns:1fr}.detail-grid{grid-template-columns:1fr}.proto{float:none;margin:.7rem 0 0;display:inline-block}}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-header">
  <div class="brand">
    <div class="brain">🧠</div>
    <div>
      <div class="logo-title">SAED</div>
      <div class="subtitle">Social Achievement Exposure Detector</div>
    </div>
  </div>
  <div class="proto">✦ Prototype NLP</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">📝 Masukkan teks yang ingin dianalisis</div>', unsafe_allow_html=True)
text = st.text_area(
    "",
    placeholder="Tulis teks di sini... (misalnya keluhan, curhatan, atau opini)",
    height=130, max_chars=1000, label_visibility="collapsed"
)
st.caption(f"{len(text)}/1000")

c1,c2=st.columns([3,1])
with c1: analyze=st.button("🔎  ANALISIS TEKS  →",use_container_width=True,type="primary")
with c2: reset=st.button("↻  Reset",use_container_width=True)
if reset: st.rerun()

INDICATORS={
"Achievement Exposure":{"keywords":["sukses","berhasil","prestasi","pencapaian","juara","gaji","kerja bagus","naik jabatan","wisuda","lulus","promosi","achievement","pencapaian orang","orang lain berhasil"],"description":"Paparan terhadap pencapaian atau keberhasilan pihak lain.","color":"#2997ff","icon":"🏆"},
"Future Uncertainty":{"keywords":["masa depan","takut gagal","khawatir","cemas","tidak tahu","bingung","nanti","besok","masa depanku","tidak punya arah","takut tidak berhasil"],"description":"Kekhawatiran atau ketidakpastian mengenai masa depan.","color":"#ffae35","icon":"📅"},
"Negative Self-Evaluation":{"keywords":["aku tidak bisa","aku gagal","aku buruk","aku bodoh","aku kurang","tidak cukup","tidak berguna","tidak mampu","rendah diri","jelek","tidak sehebat","merasa gagal"],"description":"Muncul penilaian diri yang cenderung negatif.","color":"#24c5c7","icon":"👤"},
"Perceived Lagging":{"keywords":["tertinggal","ketinggalan","telat","teman sudah","orang lain sudah","sementara aku","aku belum","belum mencapai","jauh di belakang","semua sudah"],"description":"Perasaan bahwa perkembangan diri tertinggal dari orang lain.","color":"#7a4cff","icon":"◷"},
"Social Comparison":{"keywords":["membandingkan","dibandingkan","bandingkan","lebih sukses","lebih kaya","lebih pintar","lebih baik","kalah dari","saingan","teman-teman","orang lain lebih"],"description":"Kecenderungan membandingkan diri dengan orang lain.","color":"#ec3d87","icon":"👥"}
}

def clean_text(t):
    return re.sub(r"\s+"," ",t.lower()).strip()

def calculate_scores(t):
    t=clean_text(t); out={}
    for name,data in INDICATORS.items():
        hits=sum(1 for k in data["keywords"] if k in t)
        out[name]=round(min(hits/4,1),2)
    return out

def level(score):
    return "Parah" if score>=.70 else ("Sedang" if score>=.40 else "Rendah")

def badge_class(x): return "high" if x=="Parah" else ("medium" if x=="Sedang" else "low")

def pattern(scores):
    strongest=max(scores,key=scores.get)
    return strongest if scores[strongest]>0 else "Belum ada pola dominan"

ADVICE={
"Achievement Exposure":["Fokus pada target dan progres pribadimu. Bandingkan diri dengan versi dirimu yang kemarin, bukan dengan pencapaian orang lain.","Gunakan media sosial sebagai sumber inspirasi dan informasi, bukan sebagai tolok ukur nilai diri.","Batasi paparan konten yang memicu perbandingan, terutama saat merasa cemas atau kurang percaya diri.","Rayakan pencapaian kecil yang kamu raih. Konsistensi kecil tetap berarti besar dalam jangka panjang.","Jaga keseimbangan dengan tidur cukup, aktivitas fisik ringan, dan kegiatan yang kamu nikmati."],
"Future Uncertainty":["Pecah kekhawatiran tentang masa depan menjadi target kecil yang bisa dikerjakan hari ini.","Fokus pada hal yang masih bisa kamu kendalikan daripada mencoba memastikan semua hal yang belum terjadi.","Buat rencana sederhana untuk satu minggu ke depan agar masa depan terasa lebih terarah.","Tidak semua ketidakpastian harus segera memiliki jawaban. Beri ruang untuk proses.","Evaluasi kemajuan secara berkala, bukan menuntut diri untuk langsung mengetahui seluruh arah hidup."],
"Negative Self-Evaluation":["Hindari memberi label negatif pada diri hanya karena satu kegagalan atau kekurangan.","Ganti kalimat 'aku tidak bisa' menjadi 'aku belum bisa dan masih bisa belajar'.","Catat kemampuan dan hal-hal yang sudah berhasil dilakukan sebagai pengingat bahwa kemampuan terus berkembang.","Berikan diri kesempatan untuk melakukan kesalahan tanpa menjadikannya ukuran nilai diri.","Fokus pada proses belajar dan perbaikan, bukan hanya hasil akhir."],
"Perceived Lagging":["Kecepatan perkembangan setiap orang berbeda. Tidak terlambat bukan berarti harus mengikuti jadwal orang lain.","Tentukan ukuran keberhasilan yang sesuai dengan kondisi dan tujuanmu sendiri.","Kurangi kebiasaan melihat pencapaian orang lain ketika hal tersebut membuatmu merasa tertinggal.","Pilih satu kemajuan kecil yang bisa dilakukan minggu ini dan jadikan itu prioritas.","Perjalanan yang lebih lambat tetap merupakan perjalanan selama kamu terus bergerak."],
"Social Comparison":["Gunakan pencapaian orang lain sebagai referensi atau inspirasi, bukan sebagai ukuran harga diri.","Batasi kebiasaan membandingkan kehidupan nyata dengan potongan kehidupan orang lain di media sosial.","Ketika muncul perbandingan, tanyakan: 'Apa yang sebenarnya ingin aku capai untuk diriku sendiri?'","Alihkan perhatian dari siapa yang lebih unggul menjadi apa yang bisa kamu tingkatkan.","Bangun standar keberhasilan berdasarkan nilai dan tujuan pribadi."]
}

quotes={
"Achievement Exposure":"Progres yang lambat tetaplah progres. Fokus pada perjalananmu sendiri.",
"Future Uncertainty":"Kamu tidak harus mengetahui seluruh jalan untuk mulai melangkah.",
"Negative Self-Evaluation":"Satu kesalahan tidak menentukan seluruh kemampuanmu.",
"Perceived Lagging":"Setiap orang memiliki garis waktu yang berbeda.",
"Social Comparison":"Fokus pada perjalananmu sendiri, bukan perlombaan dengan orang lain.",
"Belum ada pola dominan":"Tidak semua teks harus memiliki pola tertentu."
}

if analyze:
    if not text.strip():
        st.warning("⚠️ Silakan masukkan teks terlebih dahulu.")
        st.stop()
    scores=calculate_scores(text)
    overall=level(max(scores.values()))
    pat=pattern(scores)
    percent=int(max(scores.values())*100)

    st.markdown('<div class="section-title">📊 Hasil Analisis</div>',unsafe_allow_html=True)
    st.markdown(f"""
    <div class="result-wrap">
      <div class="level">
        <div style="color:#aeb8d5;margin-bottom:.55rem">Tingkat</div>
        <div class="level-ring"><div class="level-inside"><div class="level-number">{overall}</div><div class="level-percent">({percent}%)</div></div></div>
      </div>
      <div class="result-card">
        <div class="result-title">📊 Hasil Analisis</div>
        <div style="margin-top:.55rem">Pola yang terdeteksi:</div>
        <div class="pattern">{pat}</div>
        <div class="result-text">Teks menunjukkan indikator yang paling menonjol adalah <b>{pat}</b>. Nilai indikator lain tetap ditampilkan agar hasil dapat dilihat secara lebih menyeluruh.</div>
      </div>
    </div>
    """,unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 Ringkasan Indikator</div>',unsafe_allow_html=True)
    names=list(scores); vals=[scores[n] for n in names]
    fig=go.Figure(go.Bar(x=names,y=vals,marker_color=[INDICATORS[n]["color"] for n in names],
        text=[f"{v:.2f}" for v in vals],textposition="outside",
        hovertemplate="<b>%{x}</b><br>Skor: %{y:.2f}<extra></extra>"))
    fig.update_layout(height=390,margin=dict(l=20,r=20,t=30,b=105),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e9edff"),showlegend=False,yaxis=dict(range=[0,1.12],gridcolor="rgba(160,170,210,.14)",title=""),
        xaxis=dict(tickangle=-20))
    st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})

    st.markdown('<div class="section-title">☷ Detail Indikator</div>',unsafe_allow_html=True)
    html='<div class="detail-grid">'
    for n,s in scores.items():
        lev=level(s)
        html+=f'<div class="detail-card"><div class="detail-top"><div><span class="icon">{INDICATORS[n]["icon"]}</span><span class="detail-name">{n}</span></div><span class="badge {badge_class(lev)}">{lev}</span></div><div class="detail-desc">{INDICATORS[n]["description"]}<br><b>Skor: {int(s*100)}%</b></div></div>'
    html+='</div>'
    st.markdown(html,unsafe_allow_html=True)

    st.markdown('<div class="section-title">🌱 Saran yang sesuai</div>',unsafe_allow_html=True)
    advice=ADVICE.get(pat,["Coba gunakan hasil ini sebagai bahan refleksi, bukan sebagai diagnosis."])
    box='<div class="advice-box"><div style="font-size:1.35rem;font-weight:900">🌱 Saran yang sesuai</div><div style="color:#bdebe4;margin:.2rem 0 .6rem">Berdasarkan hasil analisis, berikut beberapa saran yang dapat kamu terapkan:</div>'
    for a in advice: box+=f'<div class="advice-item">✓ &nbsp; {a}</div>'
    box+=f'<div class="quote">💡 “{quotes[pat]}”</div></div>'
    st.markdown(box,unsafe_allow_html=True)

    with st.expander("🔎 Lihat teks setelah preprocessing"):
        st.code(clean_text(text))

st.markdown('<div class="footer">SAED Prototype • NLP berbasis aturan untuk penelitian KTI<br>Bukan alat diagnosis psikologis.</div>',unsafe_allow_html=True)
    
