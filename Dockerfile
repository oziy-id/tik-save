# Gunakan Python versi ringan
FROM python:3.9-slim

# Install ffmpeg (penting buat yt-dlp agar proses lancar)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Buat folder kerja di dalam server
WORKDIR /app

# Copy requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Buat folder downloads dan atur izin agar bisa ditulisi (Write Permission)
RUN mkdir -p /app/downloads && chmod 777 /app/downloads

# Copy semua file proyekmu ke server
COPY . .

# Atur izin untuk folder downloads lagi (untuk memastikan)
RUN chmod -R 777 /app/downloads

# Buka port 7860 (Port wajib Hugging Face)
EXPOSE 7860

# Jalankan aplikasi menggunakan Gunicorn (lebih kuat dari python app.py biasa)
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app", "--timeout", "120"]
