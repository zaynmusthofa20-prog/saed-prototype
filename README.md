# SAED Prototype v3 — Sentence & Paragraph Analysis

Versi ini mengubah analisis dari keyword-only menjadi **sentence + paragraph context**.

Fitur:
- segmentasi kalimat
- evidence berbasis pola kalimat
- hubungan antar-kalimat
- kontras (tetapi, namun, sedangkan, dll.)
- sebab-akibat (karena, sehingga, setelah, dll.)
- relasi diri vs orang lain
- evidence snippet per indikator
- rekomendasi kondisional berdasarkan indikator

Catatan: tetap merupakan prototype rule-based, bukan diagnosis psikologis. Untuk produksi disarankan menambahkan model NLP/transformer dan dataset berlabel.

