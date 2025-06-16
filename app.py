from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Your valid OpenRouter API key (keep this secret in real usage)
OPENROUTER_API_KEY = "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"

def ask_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
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

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    prompt = data.get("message", "")
    print(f"Received prompt via webhook: {prompt}")
    reply = ask_openrouter(prompt)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
