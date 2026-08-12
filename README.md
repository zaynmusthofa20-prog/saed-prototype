# SAED Prototype v10 — Sensitive All Indicators

Versi ini mempertahankan fitur yang sudah ada pada SAED Prototype v8 dan hanya memperkuat sensitivitas deteksinya.

## Indikator yang diperkuat
1. Achievement Exposure
2. Social Comparison
3. Perceived Lagging
4. Future Uncertainty
5. Negative Self-Evaluation

## Perubahan inti
- Pola kalimat diperluas dengan variasi bahasa Indonesia yang umum.
- Ditambahkan vocabulary/lexicon per indikator.
- Ditambahkan contextual scoring per kalimat.
- Ditambahkan cross-sentence reinforcement tanpa menghapus mekanisme evidence lama.
- Sistem tetap memakai evidence kalimat, context links, skor keseluruhan, chart, riwayat/session state, rekomendasi, dan tampilan yang sudah ada.
- Ditambahkan label **Sangat Tinggi** pada detail indikator.
- Ditambahkan safeguard sederhana untuk negasi dan false positive yang jelas.

## Catatan
SAED tetap merupakan prototipe analisis pola bahasa, bukan alat diagnosis. Untuk validasi produksi, gunakan dataset berlabel dan ukur precision, recall, F1, serta confusion matrix.
