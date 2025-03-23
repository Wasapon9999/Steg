# ใช้ Python เป็น Base Image
FROM python:3.10.11-slim-bullseye

# ตั้งค่าที่ทำงานใน Container
WORKDIR /app

# คัดลอกโค้ดทั้งหมดจากโปรเจ็กต์
COPY . .

# ตั้งค่า ENV ให้ Flask ใช้พอร์ตจาก Railway
ENV FLASK_APP=backend/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production
ENV PORT=5000

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt

# เปิดพอร์ต 5000 (ให้ตรงกับ Railway)
EXPOSE 5000

# รันแอป Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
