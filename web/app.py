#!/usr/bin/python3
# -*- encoding: utf-8 -*-

import glob
import hashlib
import json
import os
import re
import time
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

# ✅ เชื่อมต่อ MongoDB (ใช้ os.getenv เพื่อป้องกันแอปเด้ง)
mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/flaskdb')
app.config["MONGO_URI"] = mongo_uri
try:
    mongo = PyMongo(app)
    db = mongo.db
    print("[✅] Connected to MongoDB successfully!")
except Exception as e:
    print(f"[❌] MongoDB Connection Error: {str(e)}")

# ✅ กำหนดขนาดไฟล์สูงสุด
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# ✅ รองรับหลายภาษา
app.config['LANGUAGES'] = {
    'en': 'English',
    'fr': 'Français'
}

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {"jpeg", "png", "bmp", "gif", "tiff", "jpg", "jfif", "jpe", "tif"}

# ✅ ตรวจสอบว่าโฟลเดอร์ `static/uploads` มีอยู่หรือไม่ ถ้าไม่มีให้สร้าง
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print("[✅] Created directory: static/uploads")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    """ จัดการการอัปโหลดไฟล์ภาพ """
    
    # ✅ ตรวจสอบว่ามีไฟล์ถูกอัปโหลดหรือไม่
    if "file" not in request.files:
        return jsonify({"Error": "No file uploaded"}), 400

    file = request.files["file"]
    ext = file.filename.rsplit(".", 1)[-1].lower()

    # ✅ ตรวจสอบนามสกุลไฟล์
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"Error": f"Invalid extension: {ext}"}), 400

    # ✅ คำนวณค่า Hash ของไฟล์
    file.seek(0)
    hash_file = hashlib.md5(file.read()).hexdigest()
    file.seek(0)

    # ✅ ตรวจสอบและสร้างโฟลเดอร์ของไฟล์
    folder = os.path.join(UPLOAD_FOLDER, hash_file)
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"[✅] Created directory: {folder}")

    file_path = os.path.join(folder, f"image.{ext}")
    file.save(file_path)
    print(f"[✅] File saved: {file_path}")

    # ✅ บันทึกข้อมูลลง MongoDB
    try:
        file.seek(0, os.SEEK_END)  # ไปที่ท้ายไฟล์
        file_size = file.tell()  # ดึงขนาดไฟล์
        file.seek(0)  # รีเซ็ต pointer

        json_config = {
            "original_name": file.filename,
            "submit_date": time.time(),
            "md5_image": hash_file,
            "image": f"image.{ext}",
            "size": file_size
        }
        db.uploads.insert_one(json_config)
        print("[✅] File metadata saved to MongoDB")
    except Exception as e:
        print(f"[❌] MongoDB Insert Error: {str(e)}")
        return jsonify({"Error": "Failed to save file metadata"}), 500

    return jsonify({"Success": "File uploaded", "File": hash_file}), 200

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
