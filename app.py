#!/usr/bin/python3
# -*- encoding: utf-8 -*-

"""
Aperi'Solve - Flask application.
Aperi'Solve is a web steganography platform.
"""

import os
import glob
import hashlib
import json
import re
import time
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, make_response, Response
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv  # โหลดค่าจาก .env

# โหลดตัวแปรจาก .env ถ้ามี
load_dotenv()

# กำหนดค่า MongoDB จาก Environment Variables
MONGO_USERNAME = os.getenv('MONGODB_USERNAME', 'default_user')
MONGO_PASSWORD = os.getenv('MONGODB_PASSWORD', 'default_password')
MONGO_HOSTNAME = os.getenv('MONGODB_HOSTNAME', 'localhost')
MONGO_DATABASE = os.getenv('MONGODB_DATABASE', 'aperisolve')

app = Flask(__name__)

# ตั้งค่า MongoDB URI
app.config["MONGO_URI"] = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOSTNAME}:27017/{MONGO_DATABASE}"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size
app.config['LANGUAGES'] = {
    'en': 'English',
    'fr': 'Français'
}

mongo = PyMongo(app)
db = mongo.db

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = ["jpeg", "png", "bmp", "gif", "tiff", "jpg", "jfif", "jpe", "tif"]


def load_i18n(request):
    """Load languages from language folder and session."""
    languages = {}
    language_list = glob.glob("language/*.json")
    for lang in language_list:
        lang_code = os.path.basename(lang).split('.')[0]
        with open(lang) as file:
            languages[lang_code] = json.load(file)
    
    cookie_lang = request.cookies.get('lang')
    lang_keys = app.config['LANGUAGES'].keys()
    
    if cookie_lang in lang_keys:
        return languages[cookie_lang]
    
    header_lang = request.accept_languages.best_match(lang_keys)
    if header_lang in lang_keys:
        return languages[header_lang]
    
    return languages["en"]


def mencoder(o):
    """Encode BSON ObjectId to string."""
    if isinstance(o, ObjectId):
        return str(o)
    return str(o)


@app.route('/')
def home():
    return render_template('index.html', **load_i18n(request))


@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image uploads."""
    if "file" not in request.files:
        return jsonify({"Error": "File not found."})

    file = request.files["file"]
    ext = os.path.splitext(file.filename)[1].lower().lstrip(".")

    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"Error": f"Invalid extension: {ext}"})

    hash_file = hashlib.md5(file.read()).hexdigest()
    hash_full = hash_file
    original_name = file.filename
    file.seek(0)
    
    size = len(file.read())
    file.seek(0)
    
    t = time.time()
    json_config = {
        "original_name": original_name,
        "submit_date": t,
        "last_submit_date": t,
        "source_ip": request.remote_addr,
        "status": {},
        "image": f"image.{ext}",
        "size": size,
        "md5_image": hash_file,
        "md5_full": hash_full
    }

    # Create folder if not exists
    folder = os.path.join(UPLOAD_FOLDER, hash_full)
    if not os.path.isdir(folder):
        os.mkdir(folder)
        file.save(os.path.join(folder, f"image.{ext}"))

    # Insert in DB
    db.uploads.insert_one(json_config)

    return jsonify({"File": hash_full})


@app.route('/show')
def show():
    """Show uploaded images."""
    folder = UPLOAD_FOLDER
    dirs = os.listdir(folder) if os.path.exists(folder) else []
    return render_template('show.html', dirs=dirs, **load_i18n(request))


@app.route('/info/<file>')
@app.route('/info')
def info(file=None):
    """Retrieve file info."""
    if file:
        data = list(db.uploads.find({"md5_image": file}))
    else:
        data = list(db.uploads.find())

    for d in data:
        d["source_ip"] = "**redacted**"

    return Response(response=json.dumps(data, default=mencoder), status=200, mimetype="application/json")


@app.route('/static/<path:path>')
def send_js(path):
    """Serve static files."""
    return send_from_directory('static', path)


@app.route('/lang/<lang>')
def change_lang(lang=None):
    """Change language settings."""
    if lang in app.config['LANGUAGES']:
        response = make_response(redirect(request.referrer))
        response.set_cookie('lang', lang)
        return response
    return redirect(url_for('home'))


if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))  # ใช้พอร์ตที่ Railway กำหนด
    app.run(host="0.0.0.0", port=port)
