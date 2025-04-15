import os
import platform
import tempfile
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from PIL import Image, ImageOps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from .models import Prediction, UserPredictModel

# Determine model paths based on platform
if platform.system() == 'Windows':
    text_model_path = r"C:\Users\moham\OneDrive\Documents\Raafiya\Project\CyberBulling\CODEING\Deploy\Project\App\LSTM.h5"
    dataset_path = r"C:\Users\moham\OneDrive\Documents\Raafiya\Project\CyberBulling\CODEING\Deploy\Project\App\CYBER.csv"
    image_model_path = r"C:\Users\moham\OneDrive\Documents\Raafiya\Project\CyberBulling\CODEING\Deploy\Project\App\keras_model.h5"
    images_path = r"C:\Users\moham\OneDrive\Documents\Raafiya\Project\CyberBulling\CODEING\Deploy\Project"
else:
    # Linux/Mac paths
    text_model_path = "/mnt/c/Users/moham/OneDrive/Documents/Raafiya/Project/CyberBulling/CODEING/Deploy/Project/App/LSTM.h5"
    dataset_path = "/mnt/c/Users/moham/OneDrive/Documents/Raafiya/Project/CyberBulling/CODEING/Deploy/Project/App/CYBER.csv"
    image_model_path = "/mnt/c/Users/moham/OneDrive/Documents/Raafiya/Project/CyberBulling/CODEING/Deploy/Project/App/keras_model.h5"
    images_path = "/mnt/c/Users/moham/OneDrive/Documents/Raafiya/Project/CyberBulling/CODEING/Deploy/Project"

# Load models (lazy loading to avoid loading on import)
text_model = None
image_model = None
tokenizer = None
label_encoder = None

def ready_model():
    """Warms up both text and image models on server startup"""
    # Warm up text model
    if not load_text_model():
        print("Failed to load text model during warmup")
        return
    
    try:
        # Text model warmup
        dummy_text = "warmup text for model initialization"
        input_sequence = tokenizer.texts_to_sequences([dummy_text])
        input_padded = pad_sequences(input_sequence, maxlen=100)
        text_model.predict(input_padded)
        
        # Image model warmup
        if load_image_model():
            dummy_image = np.zeros((1, 224, 224, 3), dtype=np.float32)
            image_model.predict(dummy_image)
        
        print("Models warmed up successfully")
    except Exception as e:
        print(f"Model warmup failed: {str(e)}")

def load_text_model():
    global text_model, tokenizer, label_encoder
    if text_model is None:
        try:
            from keras.layers import LSTM
            from keras.saving import register_keras_serializable
            
            # Create a custom LSTM class that filters out unsupported arguments
            @register_keras_serializable()
            class CustomLSTM(LSTM):
                def __init__(self, *args, **kwargs):
                    # Remove unsupported arguments
                    kwargs.pop('time_major', None)
                    super().__init__(*args, **kwargs)
            
            # Load the model with the custom class
            text_model = tf.keras.models.load_model(
                text_model_path,
                compile=False,
                custom_objects={'LSTM': CustomLSTM}
            )
            
            # Compile the model
            optimizer = tf.keras.optimizers.Adam(learning_rate=0.001)
            text_model.compile(
                optimizer=optimizer,
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            # Prepare tokenizer and label encoder
            df = pd.read_csv(dataset_path, encoding='latin1')
            df['tweet_text'] = df['tweet_text'].apply(
                lambda x: x.lower() if pd.notna(x) else ""
            )
            
            label_encoder = LabelEncoder()
            df['cyberbullying_type'] = label_encoder.fit_transform(
                df['cyberbullying_type']
            )
            
            X = df['tweet_text']
            max_words = 10000
            tokenizer = Tokenizer(num_words=max_words)
            tokenizer.fit_on_texts(X)
            
            return True
        except Exception as e:
            print(f"Error loading text model: {e}")
            return False
    return True

def load_image_model():
    global image_model
    if image_model is None:
        try:
            from keras.layers import DepthwiseConv2D
            from keras.saving import register_keras_serializable
            
            # Create a custom DepthwiseConv2D class that filters out unsupported arguments
            @register_keras_serializable()
            class CustomDepthwiseConv2D(DepthwiseConv2D):
                def __init__(self, *args, **kwargs):
                    # Remove unsupported arguments
                    kwargs.pop('groups', None)
                    super().__init__(*args, **kwargs)
            
            # Load the model with the custom class
            image_model = tf.keras.models.load_model(
                image_model_path,
                compile=False,
                custom_objects={'DepthwiseConv2D': CustomDepthwiseConv2D}
            )
            return True
        except Exception as e:
            print(f"Error loading image model: {e}")
            return False
    return True


@csrf_exempt
def text_classification_api(request):
    """
    API endpoint for text classification.
    Accepts POST requests with 'text' parameter.
    Returns classification result as JSON.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)
    
    # Get text input from request
    if request.content_type == 'application/json':
        import json
        data = json.loads(request.body)
        text_input = data.get('text', None)
    else:
        text_input = request.POST.get("text_input", None) or request.POST.get("text", None)
    
    if not text_input:
        return JsonResponse({"success": False, "error": "No text input provided"}, status=400)
    
    print("Input received:", text_input)
    
    # Load model if not already loaded
    if not load_text_model():
        return JsonResponse({"success": False, "error": "Failed to load text classification model"}, status=500)
    
    try:
        # Preprocess text
        preprocessed_text = text_input.lower()
        
        # Tokenize and pad input
        max_sequence_length = 100
        input_sequence = tokenizer.texts_to_sequences([preprocessed_text])
        input_padded = pad_sequences(input_sequence, maxlen=max_sequence_length)
        
        # Make prediction
        predicted_probabilities = text_model.predict(input_padded)
        predicted_class = np.argmax(predicted_probabilities, axis=1)[0]
        
        # Map to labels
        class_mapping = {0: "age", 1: "ethnicity", 2: "not_cyberbullying", 3: "religion"}
        result = class_mapping.get(predicted_class, "unknown")
        
        # Map to our application's status
        status_mapping = {
            "not_cyberbullying": "clean",
            "age": "flagged",
            "ethnicity": "blocked",
            "religion": "flagged"
        }
        
        status = status_mapping.get(result, "flagged")
        confidence = float(predicted_probabilities[0][predicted_class])
        
        # Generate reason based on category
        reason_mapping = {
            "age": "Content contains age-based discrimination or bullying",
            "ethnicity": "Content contains ethnicity-based discrimination or hate speech",
            "religion": "Content contains religion-based discrimination or offensive material",
            "not_cyberbullying": None
        }
        
        reason = reason_mapping.get(result)
        
        # Save prediction to database
        try:
            Prediction.objects.create(input_text=preprocessed_text, output_label=result)
        except Exception as e:
            print(f"Error saving prediction: {e}")
        
        return JsonResponse({
            "success": True,
            "prediction": result,
            "status": status,
            "confidence": confidence,
            "reason": reason,
            "processed_text": preprocessed_text
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)

@csrf_exempt
def image_classification_api(request):
    """
    API endpoint for image classification.
    Accepts POST requests with 'image' file.
    Returns classification result as JSON.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)
    
    if 'image' not in request.FILES:
        return JsonResponse({"success": False, "error": "No image provided"}, status=400)
    
    # Load model if not already loaded
    if not load_image_model():
        return JsonResponse({"success": False, "error": "Failed to load image classification model"}, status=500)
    
    tmp_path = None
    try:
        # Save uploaded file temporarily
        image_file = request.FILES['image']
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            for chunk in image_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        
        # Process image for model
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        image = Image.open(tmp_path).convert("RGB")
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
        data[0] = normalized_image_array
        
        # Make prediction
        prediction = image_model.predict(data)
        classes = ['humour', 'negative', 'offensive', 'Non_Offensive', 'NSFW_Content']
        predicted_class = np.argmax(prediction)
        result = classes[predicted_class]
        confidence = float(prediction[0][predicted_class])
        
        # Map to our application's status
        status_mapping = {
            "humour": "clean",
            "Non_Offensive": "clean",
            "negative": "flagged",
            "offensive": "blocked",
            "NSFW_Content": "blocked"
        }
        
        status = status_mapping.get(result, "flagged")
        
        # Generate reason based on category
        reason_mapping = {
            "humour": None,
            "Non_Offensive": None,
            "negative": "Image contains negative content that may be upsetting",
            "offensive": "Image contains offensive content that violates community guidelines",
            "NSFW_Content": "Image contains inappropriate content not suitable for all audiences"
        }
        
        reason = reason_mapping.get(result)
        
        # Save to database if needed
        try:
            UserPredictModel.objects.create(image=image_file, label=result)
        except Exception as e:
            print(f"Error saving image prediction: {e}")
        
        return JsonResponse({
            "success": True,
            "prediction": result,
            "status": status,
            "confidence": confidence,
            "reason": reason,
            "filename": image_file.name
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
