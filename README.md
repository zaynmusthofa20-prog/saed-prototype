# SAED Streamlit v3.0

Versi UI SAED yang diperbarui mengikuti mockup yang diberikan.

## File utama
- `app.py`
- `requirements.txt`

## Deploy / update di Streamlit Cloud
1. Upload `app.py` dan `requirements.txt` ke repository GitHub.
2. Commit perubahan.
3. Buka aplikasi di Streamlit Cloud.
4. Streamlit Cloud akan otomatis mendeteksi commit baru dan melakukan redeploy.
5. Jika belum berubah, buka Manage app lalu pilih Reboot app.

## Jalankan lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```
