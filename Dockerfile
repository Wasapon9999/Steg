# ใช้ Python เวอร์ชันที่รองรับ
FROM python:3.10-slim

WORKDIR /app
COPY . .

# ติดตั้ง dependencies ของระบบที่จำเป็น
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    exiftool \
    binwalk \
    && rm -rf /var/lib/apt/lists/*

# อัปเกรด pip และติดตั้ง dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# ตั้งค่า environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
