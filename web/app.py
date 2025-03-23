#!/usr/bin/python3
# -*- encoding: utf-8 -*-

"""
Aperi'Solve - Flask application.
Aperi'Solve is a web steganography platform.
"""
__author__ = "@Zeecka"
__copyright__ = "WTFPL"

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
from dotenv import load_dotenv
from flask_cors import CORS  # 🟢 เพิ่ม CORS เพื่อให้ API รองรับทุก Request

load_dotenv()  # โหลดค่าจาก .env ถ้ามี

# ตั้งค่า Path ของโฟลเดอร์ `language/`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LANG_DIR = os.path.join(BASE_DIR, "language")

if os.path.exists(LANG_DIR):
    print(f"✅ language directory exists: {LANG_DIR}")
    print(f"📂 Files in language/: {os.listdir(LANG_DIR)}")
else:
    print("❌ language directory NOT FOUND!")

app = Flask(__name__)
CORS(app)  # 🟢 เปิดใช้งาน CORS เพื่อให้เว็บเรียก API ได้ปกติ

app.config["MONGO_URI"] = 'mongodb://' + os.environ.get('MONGODB_USERNAME', 'flaskuser')
app.config["MONGO_URI"] += ':' + os.environ.get('MONGODB_PASSWORD', 'your_mongodb_password')
app.config["MONGO_URI"] += '@' + os.environ.get('MONGODB_HOSTNAME', 'mongodb') + ':27017/'
app.config["MONGO_URI"] += os.environ.get('MONGODB_DATABASE', 'flaskdb')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 Mb max
app.config['LANGUAGES'] = {
    'en': 'English',
    'fr': 'Français'
}

mongo = PyMongo(app)
db = mongo.db

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {"jpeg", "png", "bmp", "gif", "tiff", "jpg", "jfif", "jpe", "tif"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    """
    API สำหรับอัปโหลดไฟล์รูปภาพ
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"Invalid file extension: {file.filename}"}), 400

    # สร้าง Hash ของไฟล์เพื่อลดการอัปโหลดซ้ำ
    file.seek(0)
    file_hash = hashlib.md5(file.read()).hexdigest()
    file.seek(0)
    
    save_path = os.path.join(UPLOAD_FOLDER, file_hash)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    file_path = os.path.join(save_path, file.filename)
    file.save(file_path)

    # บันทึกข้อมูลไฟล์ลง MongoDB
    file_data = {
        "filename": file.filename,
        "hash": file_hash,
        "upload_time": time.time()
    }
    db.uploads.insert_one(file_data)

    return jsonify({
        "message": "File uploaded successfully",
        "hash": file_hash,
        "file_path": file_path
    }), 200

@app.route('/')
def home():
    return render_template('index.html', **load_i18n(request))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
