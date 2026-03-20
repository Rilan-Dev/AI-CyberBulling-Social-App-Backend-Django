import requests
import base64

NVIDIA_API_KEY = "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"
invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {NVIDIA_API_KEY}",
    "Content-Type": "application/json"
}

# Create a tiny 1x1 black image via base64 for testing:
# iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=
b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

payload = {
    "model": "meta/llama-3.2-11b-vision-instruct",
    "messages": [
        {
            "role": "user",
            "content": f'Analyze this image. <img src="data:image/png;base64,{b64}" />'
        }
    ],
    "max_tokens": 10
}

response = requests.post(invoke_url, headers=headers, json=payload)
print(response.status_code)
print(response.text)

# Also try the OpenAI format just in case
payload2 = {
    "model": "meta/llama-3.2-11b-vision-instruct",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this image."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            ]
        }
    ],
    "max_tokens": 10
}
res2 = requests.post(invoke_url, headers=headers, json=payload2)
print("Format 2:", res2.status_code)
print(res2.text)

