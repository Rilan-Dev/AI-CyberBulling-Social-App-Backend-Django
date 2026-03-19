"""
Google Colab Text Model Training Script for Cyberbullying Detection
-------------------------------------------------------------------
Instructions for Google Colab:
1. Open https://colab.research.google.com/ and create a new notebook.
2. Go to 'Runtime' > 'Change runtime type' > Select 'T4 GPU'.
3. Upload your 'Text_Analysing_Dataset.csv' to the Colab files section.
4. Paste this entire code into a cell and run it.

This script uses a highly efficient, hybrid 1D-CNN + LSTM architecture 
which trains extremely fast on a GPU, provides excellent accuracy, 
and produces a very lightweight model (perfect for low-memory servers).
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import pickle

print(f"TensorFlow Version: {tf.__version__}")
print(f"Num GPUs Available: {len(tf.config.list_physical_devices('GPU'))}")

# 1. Load Dataset
print("Loading dataset...")
df = pd.read_csv('Text_Analysing_Dataset.csv', encoding='latin1')
df = df.dropna(subset=['tweet_text', 'cyberbullying_type'])

# Clean text (lowercasing, removing special chars)
import re
def clean_text(text):
    text = text.lower()
    text = re.sub(r'@[A-Za-z0-9_]+', '', text) # Remove mentions
    text = re.sub(r'#', '', text) # Remove hashtag symbol but keep text
    text = re.sub(r'http\S+', '', text) # Remove links
    text = re.sub(r'[^a-zA-Z\s]', '', text) # Remove punctuation
    return text.strip()

df['tweet_text'] = df['tweet_text'].apply(clean_text)

# 2. Encode Labels
le = LabelEncoder()
y = le.fit_transform(df['cyberbullying_type'])
num_classes = len(np.unique(y))
y = tf.keras.utils.to_categorical(y, num_classes=num_classes)

print("Classes mapped to:")
for i, name in enumerate(le.classes_):
    print(f"{i} -> {name}")

# 3. Tokenize Text
MAX_WORDS = 15000
MAX_LEN = 100

tokenizer = Tokenizer(num_words=MAX_WORDS, oov_token="<OOV>")
tokenizer.fit_on_texts(df['tweet_text'])

X = tokenizer.texts_to_sequences(df['tweet_text'])
X = pad_sequences(X, maxlen=MAX_LEN, padding='post', truncating='post')

# 4. Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Build Lightweight but Powerful Model (1D CNN + BiLSTM)
# This is much faster and lighter than Transformers, preventing memory crashes
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=MAX_WORDS, output_dim=128, input_length=MAX_LEN),
    tf.keras.layers.SpatialDropout1D(0.2), # Prevents overfitting
    
    # Extract local patterns (words that signify bullying)
    tf.keras.layers.Conv1D(64, 5, activation='relu'),
    tf.keras.layers.MaxPooling1D(pool_size=2),
    
    # Understand sequence context
    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(64, return_sequences=False)),
    
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(num_classes, activation='softmax')
])

model.compile(
    loss='categorical_crossentropy',
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    metrics=['accuracy']
)

model.summary()

# 6. Callbacks for dynamic learning and early stopping
callbacks = [
    EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=0.00001)
]

# 7. Train Model
print("Starting training...")
history = model.fit(
    X_train, y_train,
    epochs=15,
    batch_size=64,
    validation_split=0.1,
    callbacks=callbacks
)

# 8. Evaluate & Export
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy * 100:.2f}%")

model.save("Text-Analysis_v2.h5")

# Save Tokenizer (very important for loading the model on backend)
with open('tokenizer.pickle', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

print("Training complete! Please download 'Text-Analysis_v2.h5' and 'tokenizer.pickle' from Colab.")
