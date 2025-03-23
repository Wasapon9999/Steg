# ใช้ Python เป็น Base Image
FROM python:3.10.11-slim-bullseye

# ตั้งค่าที่ทำงานใน Container
WORKDIR /app
# คัดลอกไฟล์ทั้งหมด รวมถึงโฟลเดอร์ `web/language/`
COPY . /app


# กำหนด Environment Variables ให้ Flask รู้จักแอป
ENV FLASK_APP=web.app
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt

# เปิดพอร์ต 5000
EXPOSE 5000

# รันแอป Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
