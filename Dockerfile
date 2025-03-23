# ใช้ Python เป็น Base Image
FROM python:3.10.11-slim-bullseye

# ตั้งค่าที่ทำงานใน Container
WORKDIR /app

# คัดลอกไฟล์ requirements.txt มาก่อนเพื่อลดเวลา Build
COPY requirements.txt /app/

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกไฟล์โค้ดทั้งหมดเข้า Container
COPY . /app

# คัดลอกโฟลเดอร์ `language/` เข้า Container
COPY web/language /app/web/language

# กำหนด Environment Variables ให้ Flask รู้จักแอป
ENV FLASK_APP=web.app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# เปิดพอร์ต 5000
EXPOSE 5000

# รันแอป Flask ด้วย Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web.app:app"]
