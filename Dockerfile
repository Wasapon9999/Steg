# ใช้ Python เวอร์ชันที่รองรับ
FROM python:3.10-slim

WORKDIR /app
COPY . .

# ติดตั้ง dependencies ของระบบก่อน
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    exiftool \
    binwalk \
    && rm -rf /var/lib/apt/lists/*

# อัปเกรด pip ก่อนติดตั้งแพ็กเกจ
RUN python -m pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ตั้งค่า environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
