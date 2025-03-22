#!/usr/bin/python3
# -*- encoding: utf-8 -*-

import glob
import hashlib
import json
import os
import re
import time
from flask import Flask, render_template, request, jsonify, \
    send_from_directory, redirect, url_for, make_response, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

# เชื่อมต่อ MongoDB
try:
    app.config["MONGO_URI"] = os.environ['MONGO_URI']
    mongo = PyMongo(app)
    db = mongo.db
    print("[✅] Connected to MongoDB successfully!")
except Exception as e:
    print(f"[❌] MongoDB Connection Error: {str(e)}")

# กำหนดขนาดไฟล์สูงสุด
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# รองรับหลายภาษา
app.config['LANGUAGES'] = {
    'en': 'English',
    'fr': 'Français'
}

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = ["jpeg", "png", "bmp", "gif", "tiff", "jpg", "jfif", "jpe", "tif"]

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

    file = request.files["file"]  # รับไฟล์ที่อัปโหลด
    ext = str(os.path.splitext(file.filename)[1].lower().lstrip("."))

    # ✅ ตรวจสอบนามสกุลไฟล์
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"Error": f"Invalid extension: {ext}"}), 400

    # ✅ คำนวณค่า Hash ของไฟล์
    file.seek(0)
    hash_file = hashlib.md5(file.read()).hexdigest()
    file.seek(0)

    folder = os.path.join(UPLOAD_FOLDER, hash_file)
    if not os.path.exists(folder):
        os.makedirs(folder)  # ✅ ใช้ `os.makedirs()` แทน `os.mkdir()`
        print(f"[✅] Created directory: {folder}")

    file_path = os.path.join(folder, f"image.{ext}")
    file.save(file_path)
    print(f"[✅] File saved: {file_path}")

    # ✅ บันทึกข้อมูลลง MongoDB
    try:
        json_config = {
            "original_name": file.filename,
            "submit_date": time.time(),
            "md5_image": hash_file,
            "image": f"image.{ext}",
            "size": len(file.read())
        }
        db.uploads.insert_one(json_config)
        print("[✅] File metadata saved to MongoDB")
    except Exception as e:
        print(f"[❌] MongoDB Insert Error: {str(e)}")
        return jsonify({"Error": "Failed to save file metadata"}), 500

    return jsonify({"Success": "File uploaded", "File": hash_file}), 200


@app.route('/')
def home():
    index_data = {
        "what": "What is this?",
        "description": "Aperi'Solve is an online platform which performs layer analysis on images.",
        "selectfile": "Select a file to analyze",
        "selectimage": "Select Image",
        "submit": "Submit",
        "zsteg": {
            "extract": "Extract zsteg files (--extract)?",
            "options": "Test all options of zsteg (--all)?"
        },
        "enable": "Enable",
        "disable": "Disable",
        "gotpass": "I've got a password!",
        "password": "Password"
    }
    return render_template('index.html', index=index_data)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
