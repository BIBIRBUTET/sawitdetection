import streamlit as st
from ultralytics import RTDETR
from PIL import Image
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import time
import os
from twilio.rest import Client

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="SawitDetection",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SIDEBAR & NAVIGASI
# =========================================================
with st.sidebar:
    st.markdown("## 🎨 **Tema Tampilan**")
    tema = st.radio(
        "Pilih Tema:",
        ["Gelap 🌙", "Terang ☀️"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("## 🧭 **Menu**")
    
    menu = st.radio(
        "Pilih Halaman:",
        ["🏠 Beranda", "📸 Scan Gambar", "📹 Deteksi Langsung"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    if menu in ["📸 Scan Gambar", "📹 Deteksi Langsung"]:
        st.markdown("## ⚙️ Pengaturan AI")
        confidence = st.slider(
            "Kekuatan Deteksi",
            min_value=0.1,
            max_value=1.0,
            value=0.4,
            step=0.05)
        st.markdown("---")
        
    st.markdown("## 📊 Info Model")
    st.success("✅ Model Aktif")

# =========================================================
# CUSTOM CSS (Struktur Dasar, Gelap, & Terang Lembut)
# =========================================================

# 1. CSS STRUKTUR BERSAMA (Ukuran, Bentuk, dan Tata Letak)
css_shared = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

@keyframes gradientHeader {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.main-header {
    background-size: 400% 400%;
    animation: gradientHeader 15s ease infinite;
    padding: 50px 30px;
    border-radius: 28px;
    text-align: center;
    margin-bottom: 35px;
}
.main-header h1 {
    font-size: 3.5rem; font-weight: 800; margin-bottom: 12px;
    line-height: 1.2; letter-spacing: -1px;
}
.main-header p {
    font-size: 1.2rem; font-weight: 400; margin-bottom: 0;
}

@media (max-width: 768px) {
    .main-header { padding: 30px 15px; border-radius: 20px; margin-bottom: 25px; }
    .main-header h1 { font-size: 2.2rem; }
    .main-header p { font-size: 1rem; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem !important; }
}

section[data-testid="stSidebar"] {
    backdrop-filter: blur(15px);
}

[data-testid="metric-container"], div[data-testid="stCard"], .stElementContainer div[data-border="true"], [data-testid="stExpander"] {
    backdrop-filter: blur(12px);
    border-radius: 20px !important;
    padding: 10px !important;
    transition: transform 0.3s ease, border-color 0.3s ease;
}
[data-testid="stExpander"] details { border: none !important; }
[data-testid="stExpander"] summary { font-size: 1.1rem; font-weight: 600; }

div[data-testid="stSpinner"] {
    padding: 20px; border-radius: 15px;
}

.footer {
    text-align: center; margin-top: 60px; padding-bottom: 30px;
    font-size: 0.95rem; letter-spacing: 0.5px;
}

section[data-testid="stSidebar"] .stRadio p {
    font-size: 1.25rem !important; font-weight: 600 !important;   
    padding: 8px 12px; border-radius: 10px; transition: all 0.3s ease;
}
div.row-widget.stRadio > div { flex-direction: column; gap: 10px; }

[data-testid="collapsedControl"] {
    transform: scale(1.6) !important; 
    border-radius: 50% !important; padding: 5px !important;
    margin-top: 5px !important; margin-left: 5px !important;
    transition: all 0.3s ease; z-index: 999999 !important; 
}
</style>
"""

# 2. CSS MODE GELAP (Hitam / Hijau Tua)
css_dark = """
<style>
.stApp {
    background-color: #06110a;
    background-image: 
        radial-gradient(circle at 50% 0%, #11331c 0%, #06110a 70%),
        radial-gradient(circle at 0% 100%, #0a2212 0%, transparent 40%);
}

.main-header {
    background: linear-gradient(-45deg, #124622, #1b5e20, #2e7d32, #16562b);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255,255,255,0.1);
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.main-header h1 { color: #ffffff !important; text-shadow: 0 4px 12px rgba(0,0,0,0.3); }
.main-header p { color: #e8f5e9 !important; opacity: 0.9; }

section[data-testid="stSidebar"] {
    background: rgba(4, 12, 6, 0.95) !important; border-right: 1px solid rgba(255, 255, 255, 0.05);
}

[data-testid="metric-container"], div[data-testid="stCard"], .stElementContainer div[data-border="true"], [data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
}
[data-testid="metric-container"]:hover, .stElementContainer div[data-border="true"]:hover, [data-testid="stExpander"]:hover {
    border-color: rgba(67, 160, 71, 0.4) !important; transform: translateY(-2px);
}

div[data-testid="stSpinner"] {
    background: rgba(67, 160, 71, 0.1); border: 1px solid rgba(67, 160, 71, 0.2);
    box-shadow: 0 0 20px rgba(67, 160, 71, 0.1);
}

.footer { color: #a5d6a7; opacity: 0.6; }

section[data-testid="stSidebar"] .stRadio p:hover {
    background: rgba(67, 160, 71, 0.2); transform: translateX(5px); color: #ffffff !important;
}

[data-testid="collapsedControl"] {
    background-color: rgba(46, 125, 50, 0.9) !important; box-shadow: 0 4px 10px rgba(0,0,0,0.5) !important;
}
[data-testid="collapsedControl"] svg { fill: #ffffff !important; stroke: #ffffff !important; }

/* Kunci Tulisan Mode Gelap */
.stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp li, div[data-testid="stMetricValue"], .stApp label {
    color: #e2e8f0 !important;
}
.main-header h1, .main-header p, .main-header span { color: #ffffff !important; }
</style>
"""

# 3. CSS MODE TERANG (Pastel Sage Green Lembut)
css_light = """
<style>
.stApp {
    background-color: #f7fbf8;
    background-image: 
        radial-gradient(circle at 50% 0%, #edf5ee 0%, #f7fbf8 70%),
        radial-gradient(circle at 0% 100%, #e0ebe1 0%, transparent 40%);
}

.main-header {
    background: linear-gradient(-45deg, #8cbfa0, #a1ccb2, #b5d8c3, #94c4a6);
    box-shadow: 0 15px 35px rgba(140, 191, 160, 0.15), inset 0 1px 1px rgba(255,255,255,0.6);
    border: 1px solid rgba(255, 255, 255, 0.5);
}
.main-header h1 { color: #254031 !important; text-shadow: 0 2px 10px rgba(255,255,255,0.6); }
.main-header p { color: #355242 !important; font-weight: 500; }

section[data-testid="stSidebar"] {
    background: rgba(245, 250, 246, 0.95) !important; border-right: 1px solid rgba(0, 0, 0, 0.05);
}

[data-testid="metric-container"], div[data-testid="stCard"], .stElementContainer div[data-border="true"], [data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.85) !important;
    border: 1px solid rgba(140, 191, 160, 0.25) !important; box-shadow: 0 8px 24px 0 rgba(0, 0, 0, 0.03) !important;
}
[data-testid="metric-container"]:hover, .stElementContainer div[data-border="true"]:hover, [data-testid="stExpander"]:hover {
    border-color: rgba(140, 191, 160, 0.8) !important; transform: translateY(-2px);
}

div[data-testid="stSpinner"] {
    background: rgba(140, 191, 160, 0.15); border: 1px solid rgba(140, 191, 160, 0.3);
    box-shadow: 0 0 15px rgba(140, 191, 160, 0.1);
}

.footer { color: #5a8069; opacity: 0.9; }

section[data-testid="stSidebar"] .stRadio p:hover {
    background: rgba(140, 191, 160, 0.25); transform: translateX(5px); color: #254031 !important;
}

[data-testid="collapsedControl"] {
    background-color: rgba(161, 204, 178, 0.9) !important; box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
}
[data-testid="collapsedControl"] svg { fill: #254031 !important; stroke: #254031 !important; }

/* Kunci Tulisan Mode Terang (Abu-abu Kehijauan Tua - Sangat lembut dan kontras) */
.stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp li, div[data-testid="stMetricValue"], .stApp label {
    color: #355242 !important;
}
.main-header h1 { color: #254031 !important; }
.main-header p, .main-header span { color: #355242 !important; }
div[data-testid="stAlert"] p { color: #355242 !important; }
</style>
"""

# Menyuntikkan CSS berdasarkan pilihan pengguna
st.markdown(css_shared, unsafe_allow_html=True)
if tema == "Gelap 🌙":
    st.markdown(css_dark, unsafe_allow_html=True)
else:
    st.markdown(css_light, unsafe_allow_html=True)

# =========================================================
# HEADER UTAMA
# =========================================================
st.markdown("""
<div class='main-header'>
    <h1>🌿 SISTEM DETEKSI PENYAKIT DAUN SAWIT BERBASIS RT-DETR</h1>
    <p>Mendeteksi beberapa penyakit pada daun sawit</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# LOAD MODEL
# =========================================================
@st.cache_resource
def load_model():
    return RTDETR("best.pt")
    
try:
    model = load_model()
except Exception as e:
    st.error(f"❌ Gagal memuat model: {e}")
    st.stop()

# =========================================================
# REKOMENDASI 
# =========================================================
def get_advice(label):
    label = label.lower()
    
    if "culvularia" in label or "brown spot" in label:
        return {
            "emoji": "🟠",
            "title": "Culvularia",
            "desc": "Penyakit terdeteksi. Segera Berikan pupuk yang sesuai untuk menjaga kesehatan tanaman.",
            "status": "Butuh Pupuk"}
    elif "pestalotiopsis" in label or "white spot" in label:
        return {
            "emoji": "⚪",
            "title": "Pestalotiopsis",
            "desc": "Penyakit terdeteksi. Segera berikan pestisida untuk mengendalikan penyebaran.",
            "status": "Butuh Pesticida"}
    elif "heminthosprium" in label:
        return {
            "emoji": "🔴",
            "title": "Bercak Heminthosprium",
            "desc": "Lakukan sanitasi daun dan rutin lakukan penyiraman serta perawatan.",
            "status": "Penyakit Terdeteksi"}
    
    return {
        "emoji": "🟢",
        "title": "Daun Sehat",
        "desc": "Tanaman dalam kondisi sehat dan normal.",
        "status": "Sehat"}

# =========================================================
# KONTEN UTAMA
# =========================================================
if menu == "🏠 Beranda":
    st.markdown("## 👋 Selamat Datang di Sawit Detection")
    st.write("Web ini menggunakan kecerdasan buatan (AI) untuk mendeteksi jenis penyakit pada daun kelapa sawit secara otomatis. Dengan deteksi dini, Anda dapat mengambil langkah pencegahan yang tepat untuk menjaga produktivitas panen.")
    
    st.info("👈 **Cara Penggunaan:** Buka menu navigasi di sebelah kiri (klik ikon panah/bulat di pojok kiri atas jika menggunakan HP), lalu pilih mode **Scan Gambar** untuk mengambil gambar atau pilih dari galeri. Gunakan mode **Deteksi Langsung** untuk mendeteksi secara langsung via kamera.")
    
    st.markdown("---")
    st.markdown("### 🔍 Kenali Beberapa Penyakit Daun Sawit")
    
    col_a, col_b = st.columns(2)
    with col_a:
        with st.expander("🟠 **Bercak Culvularia**"):
            st.write("Penyakit Curvularia adalah penyakit jamur yang menyerang daun sawit dan menyebabkan bercak coklat atau hitam. Penyakit ini lebih mudah muncul di kondisi lembap dan kebun yang kurang terawat. Jika ditangani sejak awal, penyebarannya bisa dikendalikan sehingga tanaman sawit tetap sehat dan produktif.")
        with st.expander("⚪ **Bercak Pestalotiopsis**"):
            st.write("Pestalotiopsis adalah penyakit jamur yang menyerang daun tanaman kelapa sawit. Penyakit ini cukup sering ditemukan di perkebunan sawit, terutama pada tanaman yang sedang lemah atau berada di lingkungan yang terlalu lembap. Ditandai dengan lesi berwarna pucat atau putih. Infeksi ini membutuhkan penanganan cepat menggunakan **pestisida** untuk menghentikan penyebaran jamur.")
    with col_b:
        with st.expander("🔴 **Bercak Heminthosprium**"):
            st.write("Penyakit Helminthosporium adalah salah satu penyakit jamur yang menyerang daun tanaman kelapa sawit. Penyakit ini biasanya menyebabkan munculnya bercak-bercak pada daun sehingga daun terlihat rusak, mengering, dan pertumbuhan tanaman bisa terganggu.")
        with st.expander("🟢 **Daun Sehat**"):
            st.write("Kondisi daun normal tanpa indikasi infeksi jamur atau hama. Pertahankan jadwal perawatan rutin kebun Anda.")

elif menu == "📸 Scan Gambar":
    st.markdown("## 📸 Upload atau Ambil Foto")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Gambar",
            type=["jpg", "jpeg", "png"])
        camera_image = st.camera_input(
            "Ambil Foto Daun")
    
    image_source = None
    if uploaded_file:
        image_source = uploaded_file
    elif camera_image:
        image_source = camera_image
        
    if image_source:
        img = Image.open(image_source).convert("RGB")
        with st.spinner("⚡ Model AI sedang memindai daun "):
            start_time = time.time()
            results = model.predict(
                np.array(img),
                conf=confidence)
            end_time = time.time()
            
        if results and len(results) > 0:
            result_img = results[0].plot()[:, :, ::-1]
            with col2:
                st.image(
                    result_img,
                    caption="Hasil Deteksi AI",
                    use_container_width=True)
            
            st.markdown("## 📋 Hasil Analisis & Rekomendasi")
            boxes = results[0].boxes
            if boxes is not None and len(boxes) > 0:
                detected_count = len(boxes)
                for box in boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    conf_score = float(box.conf[0]) * 100
                    advice = get_advice(label)
                    
                    with st.container(border=True):
                        st.subheader(f"{advice['emoji']} {advice['title']}")
                        st.write(advice['desc'])
                        st.progress(min(conf_score / 100, 1.0))
                        st.caption(f"Confidence: {conf_score:.2f}% | Tindakan: {advice['status']}")
                        
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Objek Terdeteksi", detected_count)
                with m2:
                    st.metric("Inference Time", f"{(end_time-start_time):.2f}s")
                with m3:
                    st.metric("Status", "Terdeteksi")
            else:
                st.success("✅ Tidak ditemukan penyakit. Daun sehat.")

elif menu == "📹 Deteksi Langsung":
    st.markdown("## 📹 Deteksi Langsung")
    st.info("Gunakan browser Chrome dan izinkan akses kamera.")
    
    @st.cache_data
    def get_ice_servers():
        try:
            account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
            auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
            client = Client(account_sid, auth_token)
            token = client.tokens.create()
            return token.ice_servers
        except Exception as e:
            st.warning("⚠️ Twilio tidak terkonfigurasi. Menggunakan server publik sebagai cadangan.")
            return [{"urls": ["stun:stun.l.google.com:19302"]}]
    
    class VideoProcessor:
        def recv(self, frame):
            img = frame.to_ndarray(format="bgr24")
            results = model.predict(img, conf=confidence)
            annotated = results[0].plot()
            return av.VideoFrame.from_ndarray(annotated, format="bgr24")
            
    webrtc_streamer(
        key="sawitGuard-ai",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration(
            {"iceServers": get_ice_servers()}
        ),
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True)

# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div class='footer'>
© 2026 Sawit Detection • RT-DETR Detection System By Ishbir
</div>
""", unsafe_allow_html=True)
