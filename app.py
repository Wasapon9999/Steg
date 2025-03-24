import os
import glob
import hashlib
import json
import re
import time
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, make_response, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from waitress import serve

app = Flask(__name__)

# แก้ไขให้ใช้ os.environ.get() ป้องกัน KeyError
MONGO_USERNAME = os.environ.get("MONGODB_USERNAME", "default_user")
MONGO_PASSWORD = os.environ.get("MONGODB_PASSWORD", "default_password")
MONGO_HOSTNAME = os.environ.get("MONGODB_HOSTNAME", "localhost")
MONGO_DATABASE = os.environ.get("MONGODB_DATABASE", "testdb")

app.config["MONGO_URI"] = f'mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOSTNAME}:27017/{MONGO_DATABASE}'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 Mb max
app.config['LANGUAGES'] = {'en': 'English', 'fr': 'Français'}

mongo = PyMongo(app)
db = mongo.db

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = ["jpeg", "png", "bmp", "gif", "tiff", "jpg", "jfif", "jpe", "tif"]

# ตรวจสอบและสร้างโฟลเดอร์ uploads
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if "file" not in request.files:
        return jsonify({"Error": "File not found."})

    file = request.files["file"]
    ext = str(os.path.splitext(file.filename)[1].lower().lstrip("."))
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"Error": f"Invalid extension: {ext}"})

    hash_file = str(hashlib.md5(file.read()).hexdigest())
    hash_full = hash_file
    file.seek(0)

    folder = os.path.join(UPLOAD_FOLDER, hash_full)
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)  # แก้ไขให้สร้างโฟลเดอร์อัตโนมัติ
    
    file.save(f"{folder}/image.{ext}")
    db.uploads.insert_one({"md5_full": hash_full, "image": f"image.{ext}"})
    return jsonify({"File": hash_full})

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=5000)
