import streamlit as st
from ultralytics import RTDETR
from PIL import Image
import numpy as np
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import av
import time

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="SawitGuard AI",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded")

# =========================================================
# CUSTOM CSS (Dengan Perbaikan Responsif untuk HP)
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* BACKGROUND HIJAU TUA MODERN */
.stApp {
    background-color: #0b1c13;
    background-image: radial-gradient(circle at 50% 0%, #153b23 0%, #0b1c13 60%);
    color: #e0e0e0;
}

/* HEADER UTAMA */
.main-header {
    background: linear-gradient(135deg, #16562b, #24813f);
    padding: 40px;
    border-radius: 24px;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.main-header h1 {
    color: #ffffff;
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 8px;
    line-height: 1.2;
}
.main-header p {
    color: #c8e6c9;
    font-size: 1.1rem;
    margin-bottom: 0;
}

/* RESPONSIVE UNTUK HANDPHONE (< 768px) */
@media (max-width: 768px) {
    .main-header {
        padding: 25px 15px;
        border-radius: 18px;
        margin-bottom: 20px;
    }
    .main-header h1 {
        font-size: 2rem; /* Ukuran font dikecilkan untuk HP */
    }
    .main-header p {
        font-size: 0.95rem;
    }
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(8, 20, 12, 0.98);
}

/* METRIC CARDS */
[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 15px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

/* FOOTER */
.footer {
    text-align: center;
    margin-top: 50px;
    color: #81c784;
    opacity: 0.7;
    padding-bottom: 20px;
    font-size: 0.9rem;
}

/* RADIO BUTTON STYLING */
div.row-widget.stRadio > div {
    flex-direction: column;
    gap: 12px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class='main-header'>
    <h1>🌿 SAWIT DETECTION</h1>
    <p>Sistem Deteksi Penyakit Daun Sawit Berbasis RT-DETR</p>
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
# REKOMENDASI (Disesuaikan dengan Aturan Anda)
# =========================================================
def get_advice(label):
    label = label.lower()
    
    # Deteksi berdasarkan jenis bercak
    if "culvularia" in label or "brown spot" in label:
        return {
            "emoji": "🟠",
            "title": "Bercak Coklat (Culvularia)",
            "desc": "Penyakit terdeteksi. Segera aplikasikan rekomendasi pupuk yang sesuai untuk memperkuat ketahanan tanaman.",
            "status": "Butuh Pupuk"}
    elif "pestalotiopsis" in label or "white spot" in label:
        return {
            "emoji": "⚪",
            "title": "Bercak Putih (Pestalotiopsis)",
            "desc": "Penyakit terdeteksi. Segera aplikasikan pestisida yang direkomendasikan untuk mengendalikan penyebaran.",
            "status": "Butuh Pestisida"}
    elif "heminthosprium" in label:
        return {
            "emoji": "🔴",
            "title": "Bercak Heminthosprium",
            "desc": "Lakukan sanitasi daun dan gunakan fungisida berbahan tembaga.",
            "status": "Penyakit Terdeteksi"}
    
    return {
        "emoji": "🟢",
        "title": "Daun Sehat",
        "desc": "Tanaman dalam kondisi sehat dan normal.",
        "status": "Sehat"}

# =========================================================
# SIDEBAR & NAVIGASI
# =========================================================
with st.sidebar:
    st.markdown("## 🧭 Menu Navigasi")
    
    # Menambahkan opsi "Beranda" di urutan pertama
    menu = st.radio(
        "Pilih Halaman:",
        ["🏠 Beranda", "📸 Scan Gambar", "📹 Live Detection", "📈 Statistik"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    if menu in ["📸 Scan Gambar", "📹 Live Detection"]:
        st.markdown("## ⚙️ Pengaturan AI")
        confidence = st.slider(
            "Confidence Threshold",
            min_value=0.1,
            max_value=1.0,
            value=0.4,
            step=0.05)
        st.markdown("---")
        
    st.markdown("## 📊 Info Model")
    st.success("✅ Model Aktif")

# =========================================================
# KONTEN UTAMA
# =========================================================

if menu == "🏠 Beranda":
    st.markdown("## 👋 Selamat Datang di SawitGuard AI")
    st.write("Aplikasi ini menggunakan kecerdasan buatan (AI) untuk mendeteksi berbagai jenis penyakit pada daun kelapa sawit secara otomatis. Dengan deteksi dini, Anda dapat mengambil langkah pencegahan yang tepat untuk menjaga produktivitas panen.")
    
    st.info("👈 **Cara Penggunaan:** Buka menu navigasi di sebelah kiri (klik ikon **☰** di pojok kiri atas jika menggunakan HP), lalu pilih mode **Scan Gambar** atau **Live Detection** untuk mulai mendeteksi.")
    
    st.markdown("---")
    st.markdown("### 🔍 Kenali Penyakit Daun Sawit")
    
    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("#### 🟠 Bercak Coklat")
            st.write("Menyebabkan bercak berwarna kecoklatan pada daun. Memerlukan penyesuaian nutrisi dan pemberian **pupuk** untuk memulihkan kondisi tanaman.")
        with st.container(border=True):
            st.markdown("#### ⚪ Bercak Putih")
            st.write("Ditandai dengan lesi berwarna pucat atau putih. Infeksi ini membutuhkan penanganan cepat menggunakan **pestisida** untuk menghentikan penyebaran jamur.")
    with col_b:
        with st.container(border=True):
            st.markdown("#### 🔴 Bercak Heminthosprium")
            st.write("Penyakit jamur yang mengganggu fotosintesis daun. Umumnya diatasi dengan sanitasi ketat pada area kebun dan fungisida khusus.")
        with st.container(border=True):
            st.markdown("#### 🟢 Daun Sehat")
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
        with st.spinner("🔍 AI sedang menganalisis gambar..."):
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

elif menu == "📹 Live Detection":
    st.markdown("## 📹 Live Camera Detection")
    st.info("Gunakan browser Chrome dan izinkan akses kamera.")
    
    class VideoProcessor:
        def recv(self, frame):
            img = frame.to_ndarray(format="bgr24")
            results = model.predict(img, conf=confidence)
            annotated = results[0].plot()
            return av.VideoFrame.from_ndarray(annotated, format="bgr24")
            
    webrtc_streamer(
        key="sawitguard-ai",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration({
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        }),
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True)

elif menu == "📈 Statistik":
    st.markdown("## 📈 Statistik Model")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Epoch", "150")
    with c2:
        st.metric("mAP50", "46.5%")
    with c3:
        st.metric("Precision", "65.3%")
    with c4:
        st.metric("Recall", "46.8%")

# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div class='footer'>
© 2026 Sawit Detection • RT-DETR Detection System
</div>
""", unsafe_allow_html=True)
