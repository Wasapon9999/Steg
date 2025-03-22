from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "AperiSolve is running on Railway!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)  # หรือเปลี่ยนเป็น 5000 ถ้า Railway ใช้ port นี้
