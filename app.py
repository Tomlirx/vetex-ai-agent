from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Allow all origins by default

# Load API key from environment variable
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("⚠️  OPENROUTER_API_KEY is not set. Please configure it in your environment!")

def ask_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
    "model": "deepseek/deepseek-r1-0528:free",
    #"model": "google/gemini-2.0-flash-exp:free",

        
    "temperature": 0.9,  # Add this line to boost variation
    "messages": [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": prompt}
    ]
}

    try:
        print(f"Sending prompt to OpenRouter: {prompt}")
        response = requests.post(url, headers=headers, json=payload)
        print(f"OpenRouter API status code: {response.status_code}")
        print(f"OpenRouter API raw response: {response.text}")

        response.raise_for_status()
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            answer = data["choices"][0]["message"]["content"]
            print(f"Received reply: {answer}")
            return answer
        else:
            print("No choices found in OpenRouter response.")
            return "Sorry, no response from OpenRouter."

    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

    return "Sorry, I couldn't process your request."


@app.route("/webhook", methods=["POST", "OPTIONS"])
def webhook():
    if request.method == "OPTIONS":
        return '', 200  # Handle CORS preflight

    data = request.get_json(force=True)
    prompt = data.get("message", "")
    print(f"Received prompt via webhook: {prompt}")
    reply = ask_openrouter(prompt)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
