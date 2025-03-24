FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# สร้างโฟลเดอร์ uploads ป้องกัน FileNotFoundError
RUN mkdir -p /app/static/uploads

CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"]
