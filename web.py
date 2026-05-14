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
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* BACKGROUND */
.stApp {
    background-color: #0b1c13;
    background-image: radial-gradient(circle at 50% 0%, #153b23 0%, #0b1c13 60%);
    color: #e0e0e0;
}

/* HEADER */
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
    color: white;
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 8px;
}

.main-header p {
    color: #c8e6c9;
    font-size: 1.1rem;
}

@media (max-width: 768px) {
    .main-header {
        padding: 25px 15px;
        border-radius: 18px;
    }

    .main-header h1 {
        font-size: 2rem;
    }

    .main-header p {
        font-size: 0.95rem;
    }
}

/* SIDEBAR */
section[data-testid="stSidebar"] {
    background: rgba(8, 20, 12, 0.98);
}

/* METRIC */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 15px;
    border: 1px solid rgba(255,255,255,0.08);
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
# MODEL PATH
# =========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")

if not os.path.exists(MODEL_PATH):
    st.error("❌ File model best.pt tidak ditemukan!")
    st.stop()

# =========================================================
# LOAD MODEL
# =========================================================
@st.cache_resource
def load_model():
    return RTDETR(MODEL_PATH)

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

    if "culvularia" in label:
        return {
            "emoji": "🟠",
            "title": "Bercak Culvularia",
            "desc": "Penyakit terdeteksi. Gunakan fungisida dan tingkatkan sanitasi kebun.",
            "status": "Butuh Penanganan"
        }

    elif "pestalotiopsis" in label:
        return {
            "emoji": "⚪",
            "title": "Bercak Pestalotiopsis",
            "desc": "Gunakan pestisida yang direkomendasikan untuk menghentikan penyebaran jamur.",
            "status": "Butuh Pestisida"
        }

    elif "helminthosprium" in label:
        return {
            "emoji": "🔴",
            "title": "Bercak Helminthosprium",
            "desc": "Lakukan sanitasi daun dan gunakan fungisida berbahan tembaga.",
            "status": "Penyakit Terdeteksi"
        }

    return {
        "emoji": "🟢",
        "title": "Daun Sehat",
        "desc": "Tanaman dalam kondisi sehat dan normal.",
        "status": "Sehat"
    }

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.markdown("## 🧭 Menu")

    menu = st.radio(
        "Pilih Halaman",
        [
            "🏠 Beranda",
            "📸 Scan Gambar",
            "📹 Deteksi Langsung",
            "📈 Data"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    if menu in ["📸 Scan Gambar", "📹 Deteksi Langsung"]:

        st.markdown("## ⚙️ Pengaturan AI")

        confidence = st.slider(
            "Confidence",
            min_value=0.1,
            max_value=1.0,
            value=0.5,
            step=0.05
        )

    st.markdown("---")

    st.markdown("## 📊 Info Model")
    st.success("✅ RT-DETR Aktif")

# =========================================================
# BERANDA
# =========================================================
if menu == "🏠 Beranda":

    st.markdown("## 👋 Selamat Datang di Sawit Detection")

    st.write("""
    Sistem ini menggunakan kecerdasan buatan berbasis RT-DETR 
    untuk mendeteksi penyakit daun kelapa sawit secara otomatis.
    """)

    st.info("""
    👈 Gunakan menu di sebelah kiri untuk:
    
    • Upload gambar daun  
    • Mengambil foto langsung  
    • Deteksi realtime menggunakan kamera  
    • Melihat statistik model AI
    """)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:

        with st.container(border=True):
            st.markdown("### 🟠 Culvularia")
            st.write("""
            Penyakit jamur yang menyebabkan bercak coklat pada daun sawit.
            """)

        with st.container(border=True):
            st.markdown("### ⚪ Pestalotiopsis")
            st.write("""
            Penyakit jamur yang menyebabkan bercak putih pucat pada daun.
            """)

    with col2:

        with st.container(border=True):
            st.markdown("### 🔴 Helminthosprium")
            st.write("""
            Penyakit jamur yang menyebabkan bercak gelap pada daun sawit.
            """)

        with st.container(border=True):
            st.markdown("### 🟢 Daun Sehat")
            st.write("""
            Tidak ditemukan indikasi penyakit pada daun.
            """)

# =========================================================
# SCAN GAMBAR
# =========================================================
elif menu == "📸 Scan Gambar":

    st.markdown("## 📸 Upload atau Ambil Foto")

    col1, col2 = st.columns(2)

    with col1:

        uploaded_file = st.file_uploader(
            "Upload Gambar",
            type=["jpg", "jpeg", "png"]
        )

        camera_image = st.camera_input("Ambil Foto")

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
                conf=confidence,
                imgsz=640,
                verbose=False
            )

            end_time = time.time()

        if results and len(results) > 0:

            result_img = results[0].plot()[:, :, ::-1]

            with col2:
                st.image(
                    result_img,
                    caption="Hasil Deteksi",
                    use_container_width=True
                )

            st.markdown("## 📋 Hasil Analisis")

            boxes = results[0].boxes

            if boxes is not None and len(boxes) > 0:

                detected_labels = set()

                detected_count = 0

                for box in boxes:

                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]

                    conf_score = float(box.conf[0]) * 100

                    if conf_score < 50:
                        continue

                    if label in detected_labels:
                        continue

                    detected_labels.add(label)

                    detected_count += 1

                    advice = get_advice(label)

                    with st.container(border=True):

                        st.subheader(
                            f"{advice['emoji']} {advice['title']}"
                        )

                        st.write(advice['desc'])

                        st.progress(min(conf_score / 100, 1.0))

                        st.caption(
                            f"Confidence: {conf_score:.2f}%"
                        )

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric("Objek", detected_count)

                with c2:
                    st.metric(
                        "Inference",
                        f"{(end_time-start_time):.2f}s"
                    )

                with c3:
                    st.metric("Status", "Terdeteksi")

            else:
                st.success("✅ Tidak ditemukan penyakit.")

# =========================================================
# DETEKSI REALTIME
# =========================================================
elif menu == "📹 Deteksi Langsung":

    st.markdown("## 📹 Deteksi Langsung")

    st.info("""
    Gunakan browser Chrome dan izinkan akses kamera.
    """)

    @st.cache_data
    def get_ice_servers():

        try:

            account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
            auth_token = st.secrets["TWILIO_AUTH_TOKEN"]

            client = Client(account_sid, auth_token)

            token = client.tokens.create()

            return token.ice_servers

        except:
            return [{
                "urls": ["stun:stun.l.google.com:19302"]
            }]

    class VideoProcessor:

        def recv(self, frame):

            img = frame.to_ndarray(format="bgr24")

            results = model.predict(
                img,
                conf=confidence,
                imgsz=640,
                verbose=False
            )

            annotated = results[0].plot()

            return av.VideoFrame.from_ndarray(
                annotated,
                format="bgr24"
            )

    webrtc_streamer(
        key="sawit-ai",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTCConfiguration(
            {"iceServers": get_ice_servers()}
        ),
        video_processor_factory=VideoProcessor,
        media_stream_constraints={
            "video": True,
            "audio": False
        },
        async_processing=True
    )

# =========================================================
# DATA MODEL
# =========================================================
elif menu == "📈 Data":

    st.markdown("## 📈 Statistik Model RT-DETR")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Epoch", "100")

    with c2:
        st.metric("mAP50", "55.2%")

    with c3:
        st.metric("Precision", "65.1%")

    with c4:
        st.metric("Recall", "52.1%")

    st.markdown("---")

    st.markdown("### 📊 Performa Tiap Penyakit")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):

            st.markdown("#### 🟠 Culvularia")

            st.write("Precision : 65.4%")
            st.write("Recall : 46.3%")
            st.write("mAP50 : 47.5%")

    with col2:
        with st.container(border=True):

            st.markdown("#### 🔴 Helminthosprium")

            st.write("Precision : 77.5%")
            st.write("Recall : 75.0%")
            st.write("mAP50 : 82.8%")

    with col3:
        with st.container(border=True):

            st.markdown("#### ⚪ Pestalotiopsis")

            st.write("Precision : 52.4%")
            st.write("Recall : 35.0%")
            st.write("mAP50 : 35.4%")

    st.markdown("---")

    st.info("""
    📌 Model dilatih menggunakan RT-DETR selama 100 epoch 
    menggunakan dataset penyakit daun kelapa sawit.
    """)

# =========================================================
# FOOTER
# =========================================================
st.markdown("""
<div class='footer'>
© 2026 Sawit Detection • RT-DETR Detection System By Ishbir
</div>
""", unsafe_allow_html=True)
