import requests
import os

NVIDIA_API_KEY = "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"

invoke_url = "https://integrate.api.nvidia.com/v1/models"
headers = {
    "Authorization": f"Bearer {NVIDIA_API_KEY}",
    "Accept": "application/json",
}

response = requests.get(invoke_url, headers=headers)
print("Status Code:", response.status_code)
if response.status_code == 200:
    data = response.json()
    models = data.get("data", [])
    for m in models:
        if "vision" in m["id"].lower() or "phi-3" in m["id"].lower() or "llama-3.2" in m["id"].lower():
            print(m["id"])
else:
    print(response.text)
