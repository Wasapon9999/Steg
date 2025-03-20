
FROM python:3.10.11-slim-bullseye
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x start.sh
EXPOSE 5000
CMD ["sh", "start.sh"]
