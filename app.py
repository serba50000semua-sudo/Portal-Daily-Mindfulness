import streamlit as st
import requests
import datetime

# --- SISTEM LOGIN MENGGUNAKAN API KEY ---
def login_dengan_api():
    if "api_terverifikasi" not in st.session_state:
        st.session_state["api_terverifikasi"] = False

    if not st.session_state["api_terverifikasi"]:
        st.title("🌱 Login Portal Renungan Harian")
        st.write("Silakan masukkan **API Key Google (Gemini)** Anda untuk membuka akses portal panduan harian ini.")
        
        masukan_api = st.text_input("Kunci API (API Key):", type="password", placeholder="AIzaSy...")
        
        if st.button("Masuk"):
            if not masukan_api:
                st.error("API Key tidak boleh kosong.")
            else:
                with st.spinner("Memverifikasi keaslian API Key..."):
                    url_cek = f"https://generativelanguage.googleapis.com/v1beta/models?key={masukan_api}"
                    try:
                        response = requests.get(url_cek, timeout=10)
                        if response.status_code == 200:
                            st.session_state["api_terverifikasi"] = True
                            st.session_state["API_KEY"] = masukan_api
                            st.rerun()
                        else:
                            st.error("❌ API Key tidak valid. Silakan periksa kembali.")
                    except Exception as e:
                        st.error("Gagal terhubung ke server. Periksa koneksi internet Anda.")
        return False
    return True

def generate_renungan_harian(api_key, tgl_lahir, gender, jam_lahir, kota_lahir):
    nama_mesin = "models/gemini-3.5-flash"
    tanggal_sekarang = datetime.date.today().strftime("%d %B %Y")
    
    # Prompt Rahasia: Memerintahkan AI menjadi Master Bazi tapi mengunci output bahasanya
    prompt_sistem = f"""
    Bertindaklah sebagai Kalkulator Ahli Metafisika BaZi (Zi Ping) dan Wan Nian Li tingkat tinggi yang sangat presisi. 
    Lakukan analisa mendalam berdasarkan aturan klasik. Hindari kata-kata hiperbola (berlebihan). Bersikaplah jujur, realistis, dan jelas.
    
    Hari ini adalah: {tanggal_sekarang}
    
    Data Klien:
    - Tanggal Lahir: {tgl_lahir}
    - Jenis Kelamin: {gender}
    - Jam Kelahiran: {jam_lahir}
    - Kota Kelahiran: {kota_lahir}
    
    INSTRUKSI PEMROSESAN INTERNAL (HANYA DI PIKIRANMU):
    1. Konversikan tanggal lahir klien secara presisi ke sistem Ganzhi untuk menemukan Day Master (Elemen Diri).
    2. Konversikan {tanggal_sekarang} untuk menemukan Pilar Hari Ini dan Cabang Bumi Bulan berjalan.
    3. Hitung dan evaluasi interaksi Day Master klien terhadap energi hari ini.
    4. Hitung posisi klien dalam siklus 12 Fase Kehidupan (12 Life Stages) berdasarkan interaksi hari ini dengan bulan berjalan.
    
    ATURAN KETAT OUTPUT (WAJIB DITAATI):
    - DILARANG KERAS menggunakan istilah teknis BaZi sedikitpun! (Jangan gunakan kata: BaZi, Day Master, Yin/Yang, Kayu/Api/Tanah/Logam/Air, nama pinyin seperti Jia/Yi/Zi/Chou, Clash, Harm, Yong Shen, 12 Fase, dll).
    - DILARANG menyiratkan bahwa ini adalah hasil pembacaan astrologi, ramalan, atau metafisika. 
    - Output harus murni berupa "Renungan Harian" atau narasi perenungan diri yang elegan, logis, dan mudah dicerna.
    - Sampaikan bagaimana ritme energinya hari ini bekerja, dan apa saran tindakan terbaik untuk menyikapinya secara spesifik berdasarkan hasil hitungan teknis di pikiranmu.
    
    FORMAT OUTPUT MARKDOWN:
    
    🌅 **Fokus Utama Hari Ini:**
    [Jelaskan tema utama hari ini untuk klien secara langsung dan jelas]
    
    🌊 **Dinamika Diri & Potensi:**
    [Gambarkan bagaimana energi klien berinteraksi dengan lingkungan hari ini (hasil terjemahan dari 12 fase). Jelaskan kondisinya dengan jujur, apakah sedang memuncak, butuh istirahat, rentan konflik, atau saat yang tepat untuk mengambil keputusan]
    
    💡 **Langkah Bijak & Saran:**
    [Berikan petunjuk tindakan yang paling rasional dan aplikatif untuk hari ini]
    """

    url_gemini = f"https://generativelanguage.googleapis.com/v1beta/{nama_mesin}:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt_sistem}]}]}

    try:
        response = requests.post(url_gemini, json=payload, headers={'Content-Type': 'application/json'}, timeout=90)
        data = response.json()
        
        if 'error' in data:
            return None, f"Error API Gemini: {data['error']['message']}"
            
        hasil_ai = data['candidates'][0]['content']['parts'][0]['text'].strip()
        return hasil_ai, None
    except Exception as e:
        return None, f"Gagal menghubungi server teks. Error: {e}"

# --- JALANKAN APLIKASI WEB ---
if login_dengan_api():
    # SIDEBAR
    st.sidebar.title("⚙️ Status Akses")
    st.sidebar.success("✅ Akses Portal Aktif")
        
    if st.sidebar.button("🚪 Keluar / Ganti API Key"):
        st.session_state["api_terverifikasi"] = False
        st.session_state["API_KEY"] = ""
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.info("Portal ini menghitung siklus ritme personal harian Anda secara presisi untuk memberikan panduan yang jernih dan mendalam.")

    # HALAMAN UTAMA
    st.title("📖 Portal Renungan Harian Personal")
    st.write("Temukan panduan langkah dan ritme diri Anda untuk hari ini. Silakan masukkan data Anda.")
    st.markdown("---")

    # Form Input Data
    col1, col2 = st.columns(2)
    with col1:
        tgl_lahir = st.date_input("📅 Tanggal Lahir", min_value=datetime.date(1920, 1, 1), max_value=datetime.date.today())
        gender = st.selectbox("🚻 Jenis Kelamin", ["Pria", "Wanita"])
    
    with col2:
        kota = st.text_input("🏙️ Kota Kelahiran (Opsional)", placeholder="Contoh: Jakarta")
        tahu_jam = st.checkbox("Saya tahu jam lahir saya")
        if tahu_jam:
            jam_lahir = st.time_input("⏰ Jam Lahir")
        else:
            jam_lahir = "Tidak diketahui"

    # Logika peringatan jika jam/kota kosong
    if not kota or not tahu_jam:
        st.info("💡 **Catatan Penting:** Hasil renungan akan jauh lebih spesifik, mendalam, dan presisi jika Anda melengkapi data **Kota** dan **Jam Kelahiran** Anda.")

    if st.button("✨ Hasilkan Renungan Hari Ini"):
        with st.spinner("Menyelaraskan data dan menyusun renungan personal Anda hari ini..."):
            
            # Format jam untuk dikirim
            jam_kirim = jam_lahir.strftime("%H:%M") if tahu_jam else "Tidak diketahui"
            kota_kirim = kota if kota else "Tidak diketahui"
            
            hasil_renungan, error = generate_renungan_harian(
                st.session_state["API_KEY"], 
                str(tgl_lahir), 
                gender, 
                jam_kirim, 
                kota_kirim
            )
            
            if error:
                st.error(f"[GAGAL] {error}")
            else:
                st.success(f"Renungan untuk Anda di hari ini ({datetime.date.today().strftime('%d %B %Y')}):")
                st.markdown(hasil_renungan)