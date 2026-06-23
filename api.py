from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import shutil
import os
from datetime import datetime

app = FastAPI(title="Penerima Gambar ESP32-CAM")

# Pastikan folder penyimpanan tersedia
UPLOAD_DIR = "iot_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Membuat nama file unik berdasarkan waktu
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = file.filename.split(".")[-1]
        filename = f"esp32_{timestamp}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Menyimpan gambar dari ESP32 ke folder
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return JSONResponse(status_code=200, content={"message": "Gambar berhasil diterima!", "filename": filename})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Gagal memproses gambar: {str(e)}"})
