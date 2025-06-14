import os
import json
from flask import Flask, request, jsonify
from google.cloud import aiplatform
from google.oauth2 import service_account
from vertexai.language_models import ChatModel

app = Flask(__name__)

# Load credentials from environment variable
creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not creds_json:
    raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable")

creds_dict = json.loads(creds_json)
credentials = service_account.Credentials.from_service_account_info(creds_dict)

# Init Vertex AI
PROJECT_ID = creds_dict["project_id"]
REGION = "us-central1"

aiplatform.init(project=PROJECT_ID, location=REGION, credentials=credentials)
chat_model = ChatModel.from_pretrained("chat-bison@001")  # You can change to Gemini when available

@app.route("/")
def home():
    return "Vertex AI Agent is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Missing 'message' in request"}), 400

    # Generate reply from Vertex AI
    chat = chat_model.start_chat()
    response = chat.send_message(user_message)

    return jsonify({"response": response.text})

if __name__ == "__main__":
    app.run(debug=True)
