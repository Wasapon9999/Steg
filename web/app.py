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
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, make_response, Response
from flask_pymongo import PyMongo
from flask_cors import CORS  # ✅ เพิ่ม CORS ให้ API ใช้งานได้ทุกที่
from bson.objectid import ObjectId
from dotenv import load_dotenv

# ✅ โหลดค่า ENV จากไฟล์ .env
load_dotenv()

# ✅ ตั้งค่า Path ของโฟลเดอร์ `language/`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LANG_DIR = os.path.join(BASE_DIR, "language")

# ✅ ตรวจสอบว่าโฟลเดอร์ภาษาอยู่หรือไม่
if os.path.exists(LANG_DIR):
    print(f"✅ language directory exists: {LANG_DIR}")
    print(f"📂 Files in language/: {os.listdir(LANG_DIR)}")
else:
    print("❌ language directory NOT FOUND!")

# ✅ ตั้งค่า Flask
app = Flask(__name__)
CORS(app)  # ✅ อนุญาตให้ API ถูกเรียกจากทุกที่

# ✅ ตรวจสอบค่าจาก `.env` และตั้งค่า MongoDB
MONGO_USERNAME = os.getenv("MONGODB_USERNAME", "flaskuser")
MONGO_PASSWORD = os.getenv("MONGODB_PASSWORD", "your_mongodb_password")
MONGO_HOSTNAME = os.getenv("MONGODB_HOSTNAME", "mongodb")
MONGO_DATABASE = os.getenv("MONGODB_DATABASE", "flaskdb")

app.config["MONGO_URI"] = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOSTNAME}:27017/{MONGO_DATABASE}"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # ✅ 16 Mb max file size
app.config['LANGUAGES'] = {
    'en': 'English',
    'fr': 'Français'
}

# ✅ ตรวจสอบการเชื่อมต่อ MongoDB
try:
    mongo = PyMongo(app)
    db = mongo.db
    print("✅ MongoDB Connected!")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {"jpeg", "png", "bmp", "gif", "tiff", "jpg", "jfif", "jpe", "tif"}


# ✅ โหลดไฟล์ภาษา
def load_i18n(request):
    """Load languages from language folder and session."""
    languages = {}

    if not os.path.exists(LANG_DIR):
        print("❌ language directory NOT FOUND!")
        return {}

    print(f"✅ Loading languages from: {LANG_DIR}")

    language_list = glob.glob(os.path.join(LANG_DIR, "*.json"))

    for lang in language_list:
        lang_code = os.path.basename(lang).split('.')[0]
        try:
            with open(lang, encoding="utf-8") as file:
                languages[lang_code] = json.load(file)
        except Exception as e:
            print(f"❌ Error loading {lang_code}: {e}")

    cookie_lang = request.cookies.get('lang')
    lang_keys = app.config['LANGUAGES'].keys()

    if cookie_lang in lang_keys:
        return languages.get(cookie_lang, languages.get("en", {}))

    header_lang = request.accept_languages.best_match(lang_keys)
    if header_lang in lang_keys:
        return languages.get(header_lang, languages.get("en", {}))

    return languages.get("en", {})


# ✅ หน้าแรก
@app.route('/')
def home():
    return render_template('index.html', **load_i18n(request))


# ✅ API อัปโหลดไฟล์
@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400  # ❌ ไม่มี key `file` ใน request
        
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400  # ❌ ไฟล์ไม่ได้ถูกเลือก
        
        # ตรวจสอบว่านามสกุลไฟล์ถูกต้อง
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({"error": f"Invalid file type: {ext}"}), 400
        
        # บันทึกไฟล์
        upload_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(upload_path)
        
        return jsonify({"message": "File uploaded successfully!", "filename": file.filename}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # ❌ แสดงข้อความ Error ที่เกิดขึ้น


# ✅ เช็คว่าภาษาในระบบมีอะไรบ้าง
@app.route('/languages')
def get_languages():
    try:
        available_languages = list(app.config['LANGUAGES'].keys())
        return jsonify({"languages": available_languages}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ ส่งไฟล์ Static
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


# ✅ รันแอปใน Production Mode (ใช้ Gunicorn)
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
