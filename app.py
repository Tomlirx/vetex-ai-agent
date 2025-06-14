from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 Hello from Flask + Railway!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    # Just echo back for now
    return jsonify({"received": data})
