# SAED — Social Achievement Exposure Detector

Versi perbaikan detector berbasis rule/context untuk bahasa Indonesia.

## Menjalankan
```bash
pip install -r requirements.txt
streamlit run app.py
```

Detector tidak hanya mencari satu kata. Skor dihitung dari kombinasi kata diri, orang lain, pencapaian, perbandingan, lagging, ketidakpastian masa depan, serta evaluasi diri negatif. Bukti kalimat dan kata/frasa yang terdeteksi ditampilkan pada hasil.
