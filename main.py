from flask import Flask, request, redirect, jsonify
import json
import os
import random
from datetime import datetime

app = Flask(__name__)

url_file = "urls.json"
log_file = "access_logs.json"
short_code_length = 16


def load_urls():
    if os.path.exists(url_file):
        with open(url_file, "r") as file:
            return json.load(file)
    return {}


def save_urls(urls):
    with open(url_file, "w") as file:
        json.dump(urls, file, indent=2)


def generate_short_code(url):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    short_code = "".join(random.choice(chars) for _ in range(short_code_length))
    return short_code


def log_access(code, req):
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    path = request.path
    query = request.query_string.decode()
    timestamp = datetime.now().isoformat()

    log_entry = {
        "code": code,
        "ip": ip,
        "user_agent": user_agent,
        "path": path,
        "query": query,
        "timestamp": timestamp,
    }

    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            logs = json.load(file)
    else:
        logs = []

    logs.append(log_entry)

    with open(log_file, "w") as file:
        json.dump(logs, file, indent=2)


@app.route("/new", methods=["POST"])
def create_short_url():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    urls = load_urls()
    code = generate_short_code(url)

    if code in urls:
        return jsonify({"shortUrl": f"http://localhost:5000/{code}"}), 200

    urls[code] = url
    save_urls(urls)

    return jsonify({"shortUrl": f"http://localhost:5000/{code}"}), 201


@app.route("/<code>", methods=["GET"])
def redirect_to_url(code):
    urls = load_urls()

    if code in urls:
        log_access(code, request)
        return redirect(urls[code], 302)

    return jsonify({"error": "Link not found"}), 404


@app.route("/links", methods=["GET"])
def list_url():
    data = load_urls()
    return jsonify(data), 200


@app.route("/logs", methods=["GET"])
def get_logs():
    if os.path.exists(log_file):
        with open(log_file, "r") as file:
            logs = json.load(file)
        return jsonify(logs), 200
    return jsonify([]), 200


if __name__ == "__main__":
    app.run(debug=True)
