"""
Google Colab Image Model Training Script for Cyberbullying Detection
--------------------------------------------------------------------
Instructions for Google Colab:
1. Zip your DATASET folder and upload it to Colab, OR mount your Google Drive.
2. Unzip it (e.g., !unzip DATASET.zip).
3. Ensure the folder has this structure: 
   DATASET/
     TRAIN/
       NSFW_Content/
       Non_Offensive/
       humour/
       negative/
       offensive/
4. Paste this code into a Colab cell and run it with a T4 GPU.

This script uses MobileNetV3Small, a state-of-the-art lightweight CNN from Google.
It achieves high accuracy but produces a model file less than 15MB, completely 
solving the Out-Of-Memory issues on your server while providing "latest" tech.
"""

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV3Small
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

print(f"TensorFlow Version: {tf.__version__}")
print(f"Num GPUs Available: {len(tf.config.list_physical_devices('GPU'))}")

# 1. Configuration
# Path to your unzipped dataset in Colab
TRAIN_DIR = 'DATASET/TRAIN'
VALIDATION_SPLIT = 0.2
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# 2. Data Augmentation (Crucial for preventing overfitting)
print("Preparing Data Generators...")
datagen = ImageDataGenerator(
    rescale=1./255,          # Normalize pixels
    rotation_range=20,       # Randomly rotate
    width_shift_range=0.2,   # Shift left/right
    height_shift_range=0.2,  # Shift up/down
    horizontal_flip=True,    # Flip horizontally
    validation_split=VALIDATION_SPLIT
)

train_generator = datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training'
)

val_generator = datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation'
)

# See which indices map to which classes
classes_dict = train_generator.class_indices
print("Class Mapping:", classes_dict)

# 3. Build Model (Transfer Learning with MobileNetV3)
# By setting include_top=False, we remove the 1000-class ImageNet output
base_model = MobileNetV3Small(
    input_shape=(224, 224, 3), 
    include_top=False, 
    weights='imagenet'
)

# Freeze base model first
base_model.trainable = False

# Add our custom classification head
model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dropout(0.2), # Dropout to prevent overfitting
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dense(len(classes_dict), activation='softmax')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# 4. Train specific head (Phase 1)
callbacks = [
    EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True),
    ModelCheckpoint('best_image_model.h5', monitor='val_val_accuracy', save_best_only=True)
]

print("Starting Phase 1 Training (Feature Extraction)...")
history_1 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=10,
    callbacks=callbacks
)

# 5. Fine-tuning (Phase 2) - Unfreeze top layers of MobileNet
print("Starting Phase 2 Training (Fine Tuning)...")
base_model.trainable = True

# Freeze bottom 100 layers, train the rest
for layer in base_model.layers[:100]:
    layer.trainable = False

# Recompile with a MUCH LOWER learning rate
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

callbacks_2 = [
    EarlyStopping(monitor='val_loss', patience=4, restore_best_weights=True),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=1e-7)
]

history_2 = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=15,
    callbacks=callbacks_2
)

# 6. Save final model
print("Training Complete. Saving Final Model...")
model.save("Image-Analysis_v2.h5")
print("Done! Download `Image-Analysis_v2.h5` from Colab.")
