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
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}
/* BACKGROUND */
.stApp{
    background:
    linear-gradient(
        135deg,
        #07120b 0%,
        #0d1f11 50%,
        #1b5e20 100%
    );
    color:white;
}
/* HEADER */
.main-header{
    background:
    linear-gradient(
        135deg,
        #1b5e20,
        #2e7d32
    );
    padding:45px;
    border-radius:28px;
    text-align:center;
    margin-bottom:30px;

    box-shadow:
    0 15px 40px rgba(0,0,0,0.35);

    border:1px solid rgba(255,255,255,0.1);
}
.main-header h1{
    color:white;
    font-size:3.2rem;
    font-weight:800;
    margin-bottom:10px;
}
.main-header p{
    color:#dcedc8;
    font-size:1.1rem;
}
/* SIDEBAR */
section[data-testid="stSidebar"]{
    background:rgba(5,15,8,0.95);
}
/* TABS */
.stTabs [data-baseweb="tab-list"]{
    gap:12px;
}
.stTabs [data-baseweb="tab"]{
    height:55px;
    border-radius:15px;
    background:rgba(255,255,255,0.06);
    color:white;
    padding:10px 25px;
    font-weight:600;
}
.stTabs [aria-selected="true"]{
    background:#43a047 !important;
    color:white !important;
}
/* METRIC */
[data-testid="metric-container"]{
    background:rgba(255,255,255,0.06);
    border-radius:18px;
    padding:18px;
    border:1px solid rgba(255,255,255,0.08);
}
/* FOOTER */
.footer{
    text-align:center;
    margin-top:40px;
    color:#c8e6c9;
    opacity:0.8;
    padding-bottom:20px;
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
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## ⚙️ Pengaturan")
    confidence = st.slider(
        "Confidence Threshold",
        min_value=0.1,
        max_value=1.0,
        value=0.4,
        step=0.05)
    st.markdown("---")
    st.markdown("## 📊 Informasi Model")
    st.success("✅ Model RT-DETR Aktif")
    st.markdown("""
### Dataset
- Culvularia
- Heminthosprium
- Pestalotiopsis
- Daun Sehat

### Training
- Epoch : 150
- Framework : Ultralytics
- GPU : CUDA
""")
# =========================================================
# REKOMENDASI
# =========================================================
def get_advice(label):
    label = label.lower()
    if "culvularia" in label:
        return {
            "emoji": "🟠",
            "title": "Bercak Culvularia",
            "desc": "Gunakan fungisida dan hindari kelembapan berlebih.",
            "status": "Penyakit Terdeteksi"}
    elif "heminthosprium" in label:
        return {
            "emoji": "🔴",
            "title": "Bercak Heminthosprium",
            "desc": "Lakukan sanitasi daun dan gunakan fungisida berbahan tembaga.",
            "status": "Penyakit Terdeteksi"}
    elif "pestalotiopsis" in label:
        return {
            "emoji": "🟣",
            "title": "Bercak Pestalotiopsis",
            "desc": "Pangkas area terinfeksi dan gunakan fungisida sistemik.",
            "status": "Penyakit Terdeteksi"}
    return {
        "emoji": "🟢",
        "title": "Daun Sehat",
        "desc": "Tanaman dalam kondisi sehat dan normal.",
        "status": "Sehat"}
# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3 = st.tabs([
    "📸 Scan Gambar",
    "📹 Live Detection",
    "📈 Statistik"])
# =========================================================
# TAB 1 - IMAGE DETECTION
# =========================================================
with tab1:
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
            st.markdown("## 📋 Hasil Analisis")
            boxes = results[0].boxes
            if boxes is not None and len(boxes) > 0:
                detected_count = len(boxes)
                for box in boxes:
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]
                    conf_score = float(box.conf[0]) * 100
                    advice = get_advice(label)
                    # ==============================
                    # CARD HASIL DETEKSI
                    # ==============================
                    with st.container(border=True):
                        st.subheader(
                            f"{advice['emoji']} {advice['title']}")
                        st.write(advice['desc'])
                        st.progress(
                            min(conf_score / 100, 1.0))
                        st.caption(
                            f"Confidence: {conf_score:.2f}%")
                # ==============================
                # METRIC
                # ==============================
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric(
                        "Objek Terdeteksi",
                        detected_count)
                with m2:
                    st.metric(
                        "Inference Time",
                        f"{(end_time-start_time):.2f}s")
                with m3:
                    st.metric(
                        "Status",
                        "Terdeteksi")
            else:
                st.success(
                    "✅ Tidak ditemukan penyakit. Daun sehat.")
# =========================================================
# TAB 2 - LIVE DETECTION
# =========================================================
with tab2:
    st.markdown("## 📹 Live Camera Detection")
    st.info(
        "Gunakan browser Chrome dan izinkan akses kamera.")
    class VideoProcessor:
        def recv(self, frame):
            img = frame.to_ndarray(format="bgr24")
            results = model.predict(
                img,
                conf=confidence)
            annotated = results[0].plot()
            return av.VideoFrame.from_ndarray(
                annotated,
                format="bgr24")
    webrtc_streamer(
        key="sawitguard-ai",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration({
            "iceServers": [
                {
                    "urls": [
                        "stun:stun.l.google.com:19302"
                    ]
                }
            ]
        }),
        video_processor_factory=VideoProcessor,
        media_stream_constraints={
            "video": True,
            "audio": False},

        async_processing=True)
# =========================================================
# TAB 3 - STATISTICS
# =========================================================
with tab3:
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
    st.info("""
Model RT-DETR dilatih menggunakan dataset daun sawit
dengan 4 kelas utama:

• Bercak Culvularia  
• Bercak Heminthosprium  
• Bercak Pestalotiopsis  
• Daun Sehat
""")
# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div class='footer'>
© 2026 Sawit Detection • RT-DETR Detection System
</div>
""", unsafe_allow_html=True)