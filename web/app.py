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
ALLOWED_EXTENSIONS = ["jpeg", "png", "bmp",
                      "gif", "tiff", "jpg", "jfif", "jpe", "tif"]


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


@app.route('/')
def home():
    return render_template('index.html', **load_i18n(request))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
