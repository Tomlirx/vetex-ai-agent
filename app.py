from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import os

# Google AI API SDK
from google.cloud import aiplatform
from google.oauth2 import service_account

app = Flask(__name__)

# 读取 Google 认证 JSON 路径或环境变量
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON_PATH")  # Railway Secret 里设置的文件路径
GOOGLE_CREDS_CONTENT = os.getenv("GOOGLE_CREDS_CONTENT") # 也可以用内容环境变量

if GOOGLE_CREDS_JSON:
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_CREDS_JSON)
elif GOOGLE_CREDS_CONTENT:
    import json, tempfile
    creds_dict = json.loads(GOOGLE_CREDS_CONTENT)
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        json.dump(creds_dict, tmp)
        tmp.flush()
        credentials = service_account.Credentials.from_service_account_file(tmp.name)
else:
    raise RuntimeError("请设置 GOOGLE_CREDS_JSON_PATH 或 GOOGLE_CREDS_CONTENT 环境变量")

# Google AI Vertex AI endpoint
ENDPOINT = os.getenv("GOOGLE_AI_ENDPOINT")  # 形如 projects/xxx/locations/xxx/endpoints/xxx

client = aiplatform.gapic.PredictionServiceClient(credentials=credentials)

def call_google_ai_api(prompt: str) -> str:
    instances = [{"content": prompt}]
    parameters = {}

    response = client.predict(endpoint=ENDPOINT, instances=instances, parameters=parameters)
    return response.predictions[0]

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        html = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")[:5000]  # 限制字符数避免超限

        prompt = f"请用中文总结以下内容的要点：\n\n{text}"
        summary = call_google_ai_api(prompt)

        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
