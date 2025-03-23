# ใช้ Python เป็น Base Image
FROM python:3.10.11-slim-bullseye

# ตั้งค่าที่ทำงานใน Container
WORKDIR /app

# ติดตั้งแพ็กเกจพื้นฐานที่จำเป็น
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# คัดลอกไฟล์ทั้งหมดเข้าไปใน Container
COPY . .

# ติดตั้ง dependencies จาก `requirements.txt` (ที่ Root)
RUN pip install --no-cache-dir -r requirements.txt

# เปิดพอร์ต 5000 (ให้ตรงกับ Railway)
EXPOSE 5000

# รันแอป Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
