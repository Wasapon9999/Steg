FROM python:3.10-slim

WORKDIR /app
COPY . .

# ติดตั้ง dependencies
RUN pip install -r requirements.txt

# ตั้งค่า Environment Variables สำหรับ Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
