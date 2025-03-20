# ใช้ Python เวอร์ชันที่รองรับ
FROM python:3.10-slim

WORKDIR /app
COPY . .

# ติดตั้ง dependencies ของระบบที่จำเป็น
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    exiftool \
    binwalk \
    && rm -rf /var/lib/apt/lists/*

# ตรวจสอบว่าไฟล์ requirements.txt ถูก COPY มาใน Docker หรือไม่
RUN ls -la

# อัปเกรด pip และติดตั้ง dependencies
COPY requirements.txt .  # ✅ ต้องมีพารามิเตอร์ที่ 2 (ตำแหน่งปลายทาง)
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# ตั้งค่า environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "
