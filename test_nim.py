import requests

NVIDIA_API_KEY = "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"
invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {NVIDIA_API_KEY}",
    "Content-Type": "application/json"
}

def test_text(text_input):
    prompt = (
        "You are an AI trained to detect cyberbullying in social media posts. "
        "Analyze the following text and categorize it STRICTLY as exactly one of these labels: "
        "'age', 'ethnicity', 'religion', or 'not_cyberbullying'. "
        "Reply ONLY with the exact label string. No explanation.\n\n"
        f"Text to analyze: \"{text_input}\""
    )

    payload = {
        "model": "meta/llama3-70b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 10,
        "temperature": 0.1,
    }

    try:
        response = requests.post(invoke_url, headers=headers, json=payload)
        response.raise_for_status()
        ai_reply = response.json()["choices"][0]["message"]["content"].strip()
        print(f"[{text_input}] -> AI OUTPUT: '{ai_reply}'")
    except Exception as e:
        print(f"Error for [{text_input}]: {e}")
        try:
            print("Response:", response.text)
        except:
            pass

print("Testing Text Classification API...")
test_text("You are just a stupid little kid, go back to kindergarten!")
test_text("I hate your religion, it is pure evil and all of you should be banned.")
test_text("Wow, the weather is beautiful today, looking forward to the hike!")
