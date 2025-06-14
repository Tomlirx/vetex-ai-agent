from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # Set this in Railway environment settings

def ask_openrouter(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful AI agent."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # 打印调试用，看看返回了啥
        print("OpenRouter response:", result)

        # 确认是否有 'choices' 字段再返回
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
