import re
import html
from collections import defaultdict
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title='SAED — Semantic Pattern Analyzer', page_icon='◈', layout='wide', initial_sidebar_state='expanded')

# ============================================================
# SAED v7 — Detailed Indonesian semantic-pattern analyzer
# ============================================================

st.markdown(r'''
<style>
.stApp{background:radial-gradient(circle at 85% -10%,#182b63 0%,#07102b 34%,#020616 72%);color:#eef4ff}
.block-container{max-width:1280px;padding:1rem 1.2rem 3rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#07122f,#04091d);border-right:1px solid #20386f}
.card{background:linear-gradient(145deg,rgba(13,27,63,.97),rgba(5,13,33,.97));border:1px solid #243c73;border-radius:20px;padding:20px;margin:0 0 16px;box-shadow:0 10px 35px rgba(0,0,0,.18)}
.hero{background:linear-gradient(110deg,rgba(15,35,83,.98),rgba(8,17,43,.98));border:1px solid #2a4b91;border-radius:22px;padding:22px;margin-bottom:16px}
.logo{width:52px;height:52px;border-radius:15px;background:linear-gradient(135deg,#21d4fd,#7446f5);display:inline-flex;align-items:center;justify-content:center;font-size:28px;font-weight:900;box-shadow:0 0 28px rgba(32,207,255,.25);vertical-align:middle;margin-right:12px}
.small{color:#9eafd2;font-size:.88rem}.muted{color:#7f91b8}.badge{display:inline-block;padding:5px 10px;border-radius:999px;background:#102d5f;color:#67d9ff;font-weight:800;font-size:.82rem}
.metric{background:#0a1737;border:1px solid #223967;border-radius:16px;padding:15px}.metric b{font-size:1.55rem}
.insight{background:#0a1737;border:1px solid #213765;border-radius:16px;padding:15px;margin:8px 0}
.evidence{background:#07122d;border-left:4px solid #20cfff;border-radius:12px;padding:12px 14px;margin:8px 0}.sentence{background:#07122d;border:1px solid #1c315f;border-radius:14px;padding:14px;margin:8px 0}
.pattern{display:flex;gap:12px;align-items:flex-start;background:#091735;border:1px solid #203968;border-radius:14px;padding:13px;margin:8px 0}.dot{width:12px;height:12px;border-radius:50%;margin-top:6px;flex:0 0 12px;background:#20cfff;box-shadow:0 0 12px rgba(32,207,255,.5)}
.tip{background:linear-gradient(90deg,#073a3e,#102e3c);border:1px solid #118e87;border-radius:18px;padding:18px}
div[data-testid="stTextArea"] textarea{background:#081432!important;color:#edf4ff!important;border:1px solid #294474!important;border-radius:15px!important}
.stButton>button{border-radius:12px;font-weight:800;min-height:44px}
hr{border-color:#1d315d}
</style>
''', unsafe_allow_html=True)

# ---------- Logo / Header ----------
st.markdown('''
<div class="hero">
  <span class="logo">S</span>
  <span style="font-size:2rem;font-weight:900;vertical-align:middle">SAED</span>
  <div class="small" style="margin:8px 0 0 67px">Social Achievement Exposure Detector · Semantic Pattern Analyzer v7</div>
</div>
''', unsafe_allow_html=True)

# ---------- Lexicons ----------
SELF = ['aku','saya','gue','gua','gw','diriku','diri saya','diri aku','saya sendiri','aku sendiri','hidup saya','hidupku']
OTHERS = ['teman','teman-teman','temen','temen-temen','mereka','orang lain','orang-orang','rekan','kenalan','seumuran','sebaya','teman sebaya','circle saya','circle aku']
ACHIEVEMENT = ['sukses','berhasil','prestasi','pencapaian','lulus','wisuda','diterima kerja','dapat kerja','dapat pekerjaan','mendapat kerja','mendapat pekerjaan','punya pekerjaan','naik jabatan','promosi','gaji besar','penghasilan besar','penghasilan tinggi','menang','juara','menikah','punya rumah','punya mobil','punya bisnis','buka usaha','karier bagus','karir bagus','mapan','masuk kampus','diterima kuliah']
EXPOSURE = ['lihat','melihat','postingan','posting','story','feed','instagram','tiktok','linkedin','media sosial','sosmed','mendengar','dengar','dengar kabar','tahu kabar','melihat kabar','konten']
COMPARISON = ['dibanding','dibandingkan','bandingkan','perbandingan','berbeda dengan','tidak seperti','nggak seperti','gak seperti','seperti mereka','kayak mereka','seperti teman','kayak teman','lebih sukses','lebih maju','lebih kaya','lebih baik','lebih rendah','lebih tinggi','kalah dari','kalah dibanding','tidak selevel','tidak setara','kok mereka','kenapa mereka','kenapa aku','kenapa saya','kapan aku','kapan saya','sementara mereka','sedangkan mereka','mereka sudah','teman sudah']
LAGGING = ['tertinggal','ketinggalan','terlambat','belum mencapai','belum punya','belum berhasil','belum dapat','belum mendapatkan','belum kerja','belum bekerja','belum lulus','belum menikah','belum mapan','belum sukses','jalan di tempat','stuck','tidak berkembang','nggak berkembang','gak berkembang','masih belum','belum sampai','belum bisa seperti','belum seperti','masih di sini','masih bingung','belum ada']
FUTURE = ['masa depan','ke depan','nanti','besok','tahun depan','karier','karir','pekerjaan','hidup ke depan','akan','rencana','tujuan','arah hidup','setelah ini','nantinya','5 tahun','beberapa tahun']
UNCERTAINTY = ['takut','khawatir','cemas','bingung','ragu','tidak yakin','nggak yakin','gak yakin','tidak tahu','nggak tahu','gak tahu','belum tahu','entah','was-was','kepikiran','takut gagal','panik','gelisah','insecure','overthinking']
NEGATIVE_SELF = ['aku gagal','saya gagal','gue gagal','aku bodoh','saya bodoh','aku payah','saya payah','aku tidak mampu','saya tidak mampu','aku nggak mampu','saya nggak mampu','aku gak mampu','saya gak mampu','aku tidak cukup','saya tidak cukup','aku nggak cukup','saya nggak cukup','aku gak cukup','saya gak cukup','aku tidak berguna','saya tidak berguna','aku tidak layak','saya tidak layak','aku jelek','saya jelek','rendah diri','tidak berharga','nggak berharga','gak berharga','tidak pintar','nggak pintar','gak pintar','mengecewakan']

INDICATOR_INFO = {
    'Achievement Exposure':'Paparan atau perhatian pada pencapaian orang lain.',
    'Social Comparison':'Evaluasi diri dengan menjadikan orang lain sebagai pembanding.',
    'Perceived Lagging':'Persepsi bahwa diri sendiri tertinggal dari target atau orang lain.',
    'Future Uncertainty':'Keraguan, takut, bingung, atau cemas mengenai arah masa depan.',
    'Negative Self-Evaluation':'Penilaian negatif yang diarahkan secara langsung kepada diri sendiri.'
}

# ---------- Text engine ----------
def normalize(text):
    text = text.lower().replace('’', "'")
    text = re.sub(r'[^a-z0-9\s.!?,\-\']+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def split_sentences(text):
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+|\n+', text) if x.strip()]

def has(text, phrase):
    return bool(re.search(r'(?<!\w)'+re.escape(phrase)+r'(?!\w)', text))

def hits(text, lexicon):
    return list(dict.fromkeys([p for p in sorted(lexicon,key=len,reverse=True) if has(text,p)]))

def positions(text, phrase):
    return [m.start() for m in re.finditer(r'(?<!\w)'+re.escape(phrase)+r'(?!\w)', text)]

def near(text, group_a, group_b, window=90):
    aa=[x for p in group_a for x in positions(text,p)]; bb=[x for p in group_b for x in positions(text,p)]
    return any(abs(a-b)<=window for a in aa for b in bb)

def negated(text, phrase):
    # Simple Indonesian negation guard: "tidak takut" should not score as takut.
    for m in re.finditer(r'(?<!\w)'+re.escape(phrase)+r'(?!\w)', text):
        before=text[max(0,m.start()-18):m.start()].strip()
        if re.search(r'\b(tidak|tak|bukan|nggak|gak|ga)\s*$', before):
            continue
        return True
    return False

def evidence_for(sentences, phrases):
    out=[]
    for i,s in enumerate(sentences,1):
        if any(has(s,p) for p in phrases): out.append((i,s))
    return out[:6]

def pattern_rules(sentence):
    s=sentence
    self_h=hits(s,SELF); other_h=hits(s,OTHERS); ach_h=hits(s,ACHIEVEMENT); exp_h=hits(s,EXPOSURE)
    comp_h=hits(s,COMPARISON); lag_h=hits(s,LAGGING); future_h=hits(s,FUTURE); unc_h=hits(s,UNCERTAINTY); neg_h=hits(s,NEGATIVE_SELF)
    rules=[]
    # Direct semantic constructions
    if other_h and ach_h:
        rules.append(('Pencapaian Orang Lain','Orang lain + pencapaian',0.86,other_h[:2]+ach_h[:3]))
    if self_h and other_h and (comp_h or near(s,SELF,OTHERS,100)):
        rules.append(('Perbandingan Langsung','Diri sendiri ↔ orang lain',0.92,self_h[:2]+other_h[:2]+comp_h[:2]))
    if (other_h and ach_h) and re.search(r'\b(aku|saya|gue|gua|gw)\b.{0,100}\b(masih|belum)\b',s):
        rules.append(('Konstruksi Ketinggalan','Orang lain sudah X, diri masih/belum Y',0.96,other_h[:2]+ach_h[:2]+['masih/belum']))
    if lag_h:
        rules.append(('Bahasa Ketinggalan','Belum/tertinggal/stuck',0.86,lag_h[:3]))
    if (unc_h and future_h) or (unc_h and re.search(r'\b(kapan|bagaimana|gimana|apakah|entah)\b',s)):
        rules.append(('Ketidakpastian Masa Depan','Emosi tidak pasti + orientasi masa depan',0.91,unc_h[:3]+future_h[:3]))
    if neg_h and self_h:
        rules.append(('Evaluasi Diri Negatif','Label negatif melekat pada diri',0.95,neg_h[:3]+self_h[:2]))
    if exp_h and (other_h or ach_h):
        rules.append(('Paparan Sosial','Media/kabar + orang lain/pencapaian',0.82,exp_h[:3]+other_h[:2]+ach_h[:2]))
    if re.search(r'\b(lebih|kalah|tidak selevel|tidak setara)\b',s) and (self_h or other_h):
        rules.append(('Hierarki Perbandingan','Bahasa lebih/kalah/setara',0.88,self_h[:2]+other_h[:2]+comp_h[:2]))
    if re.search(r'\b(kenapa|kok|kapan)\b',s) and (self_h or other_h) and (ach_h or lag_h):
        rules.append(('Pertanyaan Timeline','Pertanyaan tentang kapan/kenapa dibanding pencapaian',0.84,['kenapa/kok/kapan']))
    return rules

def analyze(text):
    clean=normalize(text); sentences=split_sentences(clean)
    scores={k:0.0 for k in INDICATOR_INFO}; evidence={k:[] for k in INDICATOR_INFO}; matched={k:[] for k in INDICATOR_INFO}; patterns=[]; sentence_reports=[]
    if not clean: return scores,evidence,matched,patterns,sentence_reports,sentences

    for idx,s in enumerate(sentences,1):
        rules=pattern_rules(s); sentence_reports.append({'index':idx,'text':s,'rules':rules})
        for name,desc,conf,ev in rules: patterns.append({'name':name,'desc':desc,'confidence':conf,'sentence':idx,'evidence':list(dict.fromkeys(ev))})

    # Indicator scoring: independent evidence + semantic relations.
    for ind in scores:
        vals=[]; ev=[]
        for s in sentences:
            self_h=hits(s,SELF); other_h=hits(s,OTHERS); ach_h=hits(s,ACHIEVEMENT); exp_h=hits(s,EXPOSURE)
            comp_h=hits(s,COMPARISON); lag_h=hits(s,LAGGING); fut_h=hits(s,FUTURE); unc_h=hits(s,UNCERTAINTY); neg_h=hits(s,NEGATIVE_SELF)
            v=0; e=[]
            if ind=='Achievement Exposure':
                if other_h and ach_h: v=max(v,.72); e+=other_h[:2]+ach_h[:3]
                if exp_h and (other_h or ach_h): v=max(v,.62); e+=exp_h[:3]
                elif ach_h and other_h: v=max(v,.72)
            elif ind=='Social Comparison':
                if self_h and other_h: v=max(v,.62); e+=self_h[:2]+other_h[:2]
                if comp_h: v=min(1,v+.26*min(2,len(comp_h))); e+=comp_h[:3]
                if self_h and ach_h and other_h: v=max(v,.82); e+=ach_h[:2]
                if re.search(r'\b(lebih|kalah|dibanding|sedangkan|sementara)\b',s) and (self_h or other_h): v=max(v,.78)
            elif ind=='Perceived Lagging':
                if lag_h: v=max(v,min(.76,.32*len(lag_h))); e+=lag_h[:3]
                if other_h and ach_h and (lag_h or re.search(r'\b(masih|belum)\b',s)): v=max(v,.88); e+=other_h[:2]+ach_h[:2]
                if self_h and lag_h: v=max(v,.86); e+=self_h[:2]
            elif ind=='Future Uncertainty':
                active_unc=[p for p in unc_h if negated(s,p)]
                if active_unc: v=max(v,min(.72,.34*len(active_unc))); e+=active_unc[:3]
                if fut_h: v=max(v,.30); e+=fut_h[:3]
                if active_unc and fut_h: v=max(v,.86)
                if re.search(r'\b(kapan|bagaimana|gimana|entah|apakah)\b',s) and (fut_h or active_unc): v=max(v,.82)
            elif ind=='Negative Self-Evaluation':
                if neg_h and self_h: v=max(v,.93); e+=neg_h[:3]+self_h[:2]
                elif neg_h: v=max(v,.48); e+=neg_h[:3]
                # adjective near self
                if near(s,SELF,['gagal','bodoh','payah','jelek','buruk','rendah diri','tidak mampu','nggak mampu','gak mampu','tidak cukup','nggak cukup','gak cukup'],65):
                    v=max(v,.84); e+=self_h[:2]
            if v>0: vals.append(v); ev+=e
        joined=' '.join(sentences)
        # Cross-sentence links
        if ind=='Achievement Exposure' and near(joined,OTHERS,ACHIEVEMENT,180): vals.append(.70); ev+=hits(joined,OTHERS)[:2]+hits(joined,ACHIEVEMENT)[:3]
        if ind=='Social Comparison' and near(joined,SELF,OTHERS,180) and (hits(joined,COMPARISON) or hits(joined,ACHIEVEMENT)): vals.append(.72); ev+=hits(joined,SELF)[:2]+hits(joined,OTHERS)[:2]
        if ind=='Perceived Lagging' and near(joined,OTHERS,ACHIEVEMENT,180) and re.search(r'\b(belum|masih|tertinggal)\b',joined): vals.append(.82); ev+=['hubungan lintas kalimat']
        if ind=='Future Uncertainty' and hits(joined,UNCERTAINTY) and hits(joined,FUTURE): vals.append(.80); ev+=['hubungan emosi + masa depan']
        if ind=='Negative Self-Evaluation' and near(joined,SELF,['gagal','bodoh','payah','jelek','tidak mampu','tidak cukup'],80): vals.append(.82); ev+=['diri + evaluasi negatif']
        if vals:
            strongest=max(vals); support=sum(vals)/len(vals)
            # Several independent signals should raise confidence, but cap at 1.
            diversity=min(len(set(ev)),5)
            score=min(1.0, strongest*0.72 + support*0.18 + min(.10, diversity*.025))
            scores[ind]=round(score,2)
            matched[ind]=list(dict.fromkeys(ev))[:10]
            evidence[ind]=evidence_for(sentences,matched[ind])
    return scores,evidence,matched,patterns,sentence_reports,sentences

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('### ◈ SAED')
    st.caption('Semantic Context Engine')
    mode=st.radio('Mode analisis',['Ringkas','Rinci'],index=1)
    st.markdown('---')
    st.markdown('**Indikator yang dianalisis**')
    for k in INDICATOR_INFO: st.write('• '+k)
    st.markdown('---')
    st.caption('Analisis bahasa berbasis pola dan konteks. Bukan diagnosis psikologis.')

# ---------- Input ----------
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('### ✦ Masukkan teks untuk dianalisis')
example='Teman-teman saya sudah lulus dan punya pekerjaan bagus. Mereka sering memposting pencapaian di media sosial, sedangkan saya masih bingung arah hidup dan belum punya pekerjaan tetap. Kadang saya merasa tertinggal, insecure, dan takut gagal di masa depan.'
text=st.text_area('Teks',value='',placeholder=example,height=180,max_chars=4000,label_visibility='collapsed')
c1,c2,c3=st.columns([3,1,1])
run=c1.button('◈ ANALISIS SEKARANG',type='primary',use_container_width=True)
use_example=c2.button('Contoh',use_container_width=True)
reset=c3.button('Reset',use_container_width=True)
if use_example: text=example; st.session_state['saed_text']=text
if reset: st.session_state.clear(); st.rerun()
if 'saed_text' in st.session_state and not text: text=st.session_state['saed_text']
if run: st.session_state['saed_text']=text
st.caption(f'{len(text)}/4000 karakter · Mode: {mode}')
st.markdown('</div>',unsafe_allow_html=True)

if 'saed_result' in st.session_state and not run:
    result=st.session_state['saed_result']
elif run and text.strip():
    result=analyze(text); st.session_state['saed_result']=result
else:
    result=analyze(text) if text.strip() else ({k:0.0 for k in INDICATOR_INFO},{k:[] for k in INDICATOR_INFO},{k:[] for k in INDICATOR_INFO},[],[],[])

scores,evidence,matched,patterns,sentence_reports,sentences=result
ranked=sorted(scores.items(),key=lambda x:x[1],reverse=True)
overall=round(ranked[0][1]*100) if ranked and ranked[0][1]>0 else 0
peak=ranked[0][0] if overall else 'Belum terdeteksi'
level='Rendah' if overall<35 else 'Sedang' if overall<65 else 'Tinggi'

# ---------- Overview ----------
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('### ◎ Ringkasan Analisis')
a,b,c,d=st.columns(4)
a.markdown(f'<div class="metric"><span class="small">Tingkat pola tertinggi</span><br><b>{overall}%</b><br><span class="badge">{level}</span></div>',unsafe_allow_html=True)
b.markdown(f'<div class="metric"><span class="small">Indikator terkuat</span><br><b style="font-size:1.15rem">{html.escape(peak)}</b></div>',unsafe_allow_html=True)
c.markdown(f'<div class="metric"><span class="small">Pola terdeteksi</span><br><b>{len(patterns)}</b><br><span class="small">aturan semantik</span></div>',unsafe_allow_html=True)
d.markdown(f'<div class="metric"><span class="small">Kalimat dianalisis</span><br><b>{len(sentences)}</b><br><span class="small">segmentasi</span></div>',unsafe_allow_html=True)
st.markdown('</div>',unsafe_allow_html=True)

# ---------- Score chart ----------
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('### ◈ Profil Indikator')
labels=list(scores.keys()); vals=[round(scores[k]*100) for k in labels]
fig=go.Figure(go.Bar(x=vals,y=labels,orientation='h',text=[f'{v}%' for v in vals],textposition='outside',marker=dict(color=['#20cfff','#ff6680','#8b5cf6','#22c4ca','#f6ad55'])))
fig.update_xaxes(range=[0,105],dtick=20,ticksuffix='%',gridcolor='#1a2d56')
fig.update_layout(height=320,margin=dict(l=0,r=40,t=10,b=10),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',font_color='#dce7ff',showlegend=False)
st.plotly_chart(fig,use_container_width=True,config={'displayModeBar':False})
st.markdown('</div>',unsafe_allow_html=True)

# ---------- Detailed sentence analysis ----------
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('### ⌁ Analisis Pola Kalimat (Rinci)')
st.caption('Setiap kalimat diuji terhadap hubungan diri–orang lain, pencapaian, ketinggalan, masa depan, paparan media, dan evaluasi diri.')
if not sentences:
    st.info('Masukkan teks lalu tekan ANALISIS SEKARANG.')
else:
    for report in sentence_reports:
        st.markdown(f'<div class="sentence"><b>Kalimat {report["index"]}</b><br>{html.escape(report["text"])}</div>',unsafe_allow_html=True)
        if report['rules']:
            for name,desc,conf,ev in report['rules']:
                st.markdown(f'<div class="pattern"><span class="dot"></span><div><b>{html.escape(name)}</b> · {round(conf*100)}%<br><span class="small">{html.escape(desc)}</span><br><span class="small">Bukti: {html.escape(", ".join(ev))}</span></div></div>',unsafe_allow_html=True)
        else:
            st.caption('↳ Belum ada pola semantik yang cukup kuat pada kalimat ini.')
st.markdown('</div>',unsafe_allow_html=True)

# ---------- Indicator detail ----------
st.markdown('<div class="card">',unsafe_allow_html=True)
st.markdown('### ◉ Detail Bukti per Indikator')
cols=st.columns(2)
for i,(name,val) in enumerate(ranked):
    pct=round(val*100); sev='Rendah' if pct<35 else 'Sedang' if pct<65 else 'Tinggi'
    ev=evidence[name]; phrases=matched[name]
    evidence_text=' '.join([f'Kalimat {n}: {s}' for n,s in ev]) if ev else 'Belum ada bukti kalimat yang memenuhi aturan deteksi.'
    with cols[i%2]:
        st.markdown(f'''<div class="insight"><b>{html.escape(name)}</b><span style="float:right"><b>{sev}</b> · {pct}%</span><br><span class="small">{html.escape(INDICATOR_INFO[name])}</span><div style="margin:10px 0;height:9px;background:#182a58;border-radius:99px;overflow:hidden"><div style="width:{pct}%;height:100%;background:linear-gradient(90deg,#20cfff,#7446f5);border-radius:99px"></div></div><span class="small"><b>Frasa terpicu:</b> {html.escape(', '.join(phrases) if phrases else '—')}</span></div>''',unsafe_allow_html=True)
        if ev:
            with st.expander('Lihat bukti kalimat'):
                for n,s in ev: st.markdown(f'<div class="evidence"><b>Kalimat {n}</b><br>{html.escape(s)}</div>',unsafe_allow_html=True)
st
