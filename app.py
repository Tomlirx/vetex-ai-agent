from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route("/test", methods=["GET"])
def test_openrouter():
    test_prompt = "Tell me a joke"
    print(f"Calling OpenRouter with prompt: {test_prompt}")
    reply = ask_openrouter(test_prompt)
    return jsonify({"reply": reply})


#OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Set this in Railway environment settings
OPENROUTER_API_KEY = "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"

def ask_openrouter(prompt):
    print(f"Using API key: {OPENROUTER_API_KEY[:8]}...")  # Debug log of partial key
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
            {"role": "system", "content": "You are a helpful AI agent."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        print("OpenRouter response:", result)  # Debug log for full response

        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return "Sorry, no response from OpenRouter."

    except Exception as e:
        print(f"Error in ask_openrouter: {e}")
        return "Sorry, I couldn’t process your request."


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    user_message = data.get("message", "")
    reply = ask_openrouter(user_message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
