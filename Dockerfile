# ใช้ Python เป็น Base Image
FROM python:3.10.11-slim-bullseye

# ตั้งค่าที่ทำงานใน Container
WORKDIR /app

# ติดตั้ง dependencies พื้นฐานที่ต้องใช้
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# คัดลอก requirements.txt มาก่อนเพื่อลดเวลา Build
COPY requirements.txt /app/requirements.txt

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# คัดลอกไฟล์ทั้งหมดเข้าไปใน Container
COPY . .

# เปิดพอร์ต 5000
EXPOSE 5000

# รันแอป Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
