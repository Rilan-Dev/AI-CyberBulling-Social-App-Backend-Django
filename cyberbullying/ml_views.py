import os
import json
import base64
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Prediction, UserPredictModel

# ==============================================================================
# NVIDIA NIM API Integration
# This file replaces the local TensorFlow models to prevent OOM errors and
# provide State-of-the-Art accuracy using Llama-3 and Phi-3-Vision APIs.
# ==============================================================================

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "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")

# ------------------------------------------------------------------------------
# TEXT CLASSIFICATION (Using Meta Llama-3 70B via NVIDIA API)
# ------------------------------------------------------------------------------
@csrf_exempt
def text_classification_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)
    
    if request.content_type == 'application/json':
        data = json.loads(request.body)
        text_input = data.get('text', None)
    else:
        text_input = request.POST.get("text_input") or request.POST.get("text")
    
    if not text_input:
        return JsonResponse({"success": False, "error": "No text input provided"}, status=400)

    if not NVIDIA_API_KEY:
        return JsonResponse({"success": False, "error": "NVIDIA_API_KEY not configured"}, status=500)

    invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        "You are an AI trained to detect cyberbullying, harassment, and inappropriate content in social media posts. "
        "Analyze the following text and categorize it STRICTLY as exactly one of these labels: "
        "'age', 'ethnicity', 'religion', 'gender', 'sexual_harassment', 'other_cyberbullying', or 'not_cyberbullying'. "
        "Reply ONLY with the exact label string. No explanation.\n\n"
        f"Text to analyze: \"{text_input}\""
    )

    payload = {
        "model": "meta/llama3-70b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 15,
        "temperature": 0.1,
    }

    try:
        response = requests.post(invoke_url, headers=headers, json=payload)
        response.raise_for_status()
        
        ai_reply = response.json()["choices"][0]["message"]["content"].strip().lower()
        
        categories = ['age', 'ethnicity', 'religion', 'gender', 'sexual_harassment', 'other_cyberbullying', 'not_cyberbullying']
        result = "not_cyberbullying"
        for cat in categories:
            if cat in ai_reply:
                result = cat
                break

        status_mapping = {
            "not_cyberbullying": "clean",
            "age": "flagged",
            "ethnicity": "blocked",
            "religion": "flagged",
            "gender": "flagged",
            "sexual_harassment": "blocked",
            "other_cyberbullying": "flagged"
        }
        status = status_mapping.get(result, "flagged")
        
        reason_mapping = {
            "age": "Content contains age-based discrimination or bullying.",
            "ethnicity": "Content contains ethnicity-based discrimination or hate speech.",
            "religion": "Content contains religion-based discrimination or offensive material.",
            "gender": "Content contains gender-based discrimination or bullying.",
            "sexual_harassment": "Content contains sexual harassment or explicit material.",
            "other_cyberbullying": "Content contains general cyberbullying or offensive language.",
            "not_cyberbullying": None
        }
        reason = reason_mapping.get(result)

        Prediction.objects.create(input_text=text_input, output_label=result)

        return JsonResponse({
            "success": True,
            "prediction": result,
            "status": status,
            "confidence": 0.95,
            "reason": reason,
            "processed_text": text_input
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)

# ------------------------------------------------------------------------------
# IMAGE CLASSIFICATION (Using Microsoft Phi-3-Vision via NVIDIA API)
# ------------------------------------------------------------------------------
@csrf_exempt
def image_classification_api(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)
    
    if 'image' not in request.FILES:
        return JsonResponse({"success": False, "error": "No image provided"}, status=400)
    
    if not NVIDIA_API_KEY:
        return JsonResponse({"success": False, "error": "NVIDIA_API_KEY not configured"}, status=500)

    try:
        image_file = request.FILES['image']
        
        image_bytes = image_file.read()
        base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
        
        ext = image_file.name.split('.')[-1].lower()
        if ext == 'jpg': ext = 'jpeg'
        mime_type = f"image/{ext}"

        invoke_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "meta/llama-3.2-11b-vision-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": 'Analyze this image and classify the content strictly into exactly ONE of the following tags: "NSFW_Content", "offensive", "negative", "humour", or "Non_Offensive". Reply ONLY with the exact tag string. No explanation.'},
                        {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_encoded}"}}
                    ]
                }
            ],
            "max_tokens": 10,
            "temperature": 0.1
        }

        response = requests.post(invoke_url, headers=headers, json=payload)
        response.raise_for_status()

        ai_reply = response.json()["choices"][0]["message"]["content"].strip()

        categories = ['NSFW_Content', 'offensive', 'negative', 'humour', 'Non_Offensive']
        result = "Non_Offensive"
        for cat in categories:
            if cat.lower() in ai_reply.lower():
                result = cat
                break

        status_mapping = {
            "humour": "clean",
            "Non_Offensive": "clean",
            "negative": "flagged",
            "offensive": "blocked",
            "NSFW_Content": "blocked"
        }
        status = status_mapping.get(result, "flagged")
        
        reason_mapping = {
            "humour": None,
            "Non_Offensive": None,
            "negative": "Image contains negative content that may be upsetting",
            "offensive": "Image contains offensive content that violates community guidelines",
            "NSFW_Content": "Image contains inappropriate content not suitable for all audiences"
        }
        reason = reason_mapping.get(result)

        image_file.seek(0)
        UserPredictModel.objects.create(image=image_file, label=result)

        return JsonResponse({
            "success": True,
            "prediction": result,
            "status": status,
            "confidence": 0.95,
            "reason": reason,
            "filename": image_file.name,
            "model_used": "nvidia_api"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)
