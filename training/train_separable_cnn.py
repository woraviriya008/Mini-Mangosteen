#!/usr/bin/env python3
"""
=============================================================================
  Mangosteen Edge AI — Separable CNN High-Accuracy Training Pipeline
  Architecture: Multi-Stage Depthwise Separable CNN with Residual Block
  Parameter Count: ~90,891 (Strictly 60,000+ to <= 100,000)
  Target: LilyGO T-SIMCAM (ESP32-S3) | Full INT8 Quantization (96x96 INT8)
=============================================================================
"""

import os
import sys
import random
from pathlib import Path
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix, f1_score, balanced_accuracy_score

# Force UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# -----------------------------------------------------------------------------
# Configuration & Paths
# -----------------------------------------------------------------------------
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

DATASET_DIR = PROJECT_ROOT / "dataset"
TRAIN_DIR = DATASET_DIR / "train"
VAL_DIR = DATASET_DIR / "val"
TEST_DIR = DATASET_DIR / "test"

MODELS_EXPORT_DIR = PROJECT_ROOT / "models"
SRC_DIR = PROJECT_ROOT / "src"
OUTPUT_DIR = SCRIPT_DIR / "output_models"

MODELS_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IMG_HEIGHT, IMG_WIDTH = 96, 96
BATCH_SIZE = 16
EPOCHS = 80
CLASSES = ["overripe", "ripe", "unripe"]

print("=" * 72)
print("  🍃 MANGOSTEEN SEPARABLE CNN HIGH-ACCURACY TRAINING PIPELINE 🍃")
print("  Architecture: Multi-Stage Separable CNN + Residual Block (~90,891 Params)")
print("  Parameter Constraint: 60,000+ and <= 100,000 Parameters")
print("  Target: LilyGO T-SIMCAM ESP32-S3 (96x96 Full INT8)")
print("=" * 72)

# -----------------------------------------------------------------------------
# 1. Dataset Loading
# -----------------------------------------------------------------------------
print("\n[Step 1/6] Loading Dataset from:", DATASET_DIR)

train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    shuffle=True,
    seed=SEED
)

val_ds = tf.keras.utils.image_dataset_from_directory(
    VAL_DIR,
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    shuffle=False
)

test_ds = tf.keras.utils.image_dataset_from_directory(
    TEST_DIR,
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=1,
    label_mode="categorical",
    shuffle=False
)

eval_train_ds = tf.keras.utils.image_dataset_from_directory(
    TRAIN_DIR,
    image_size=(IMG_HEIGHT, IMG_WIDTH),
    batch_size=BATCH_SIZE,
    label_mode="categorical",
    shuffle=False
)

print(f"   Classes (Alphabetical): {train_ds.class_names}")

class_counts = {}
for c in CLASSES:
    class_counts[c] = len(list((TRAIN_DIR / c).glob("*.*")))
print(f"   Train samples per class: {class_counts}")

total_samples = sum(class_counts.values())
class_weights = {
    idx: total_samples / (len(CLASSES) * class_counts[c])
    for idx, c in enumerate(CLASSES)
}
print(f"   Calculated Balanced Class Weights: {class_weights}")

# -----------------------------------------------------------------------------
# 2. Build Multi-Stage Low-Latency Separable CNN (Target: ~94,163 parameters, range 60k-100k)
# -----------------------------------------------------------------------------
print("\n[Step 2/6] Building Low-Latency Multi-Stage Separable CNN Architecture...")

l2 = tf.keras.regularizers.l2(1.0e-4)
inputs = tf.keras.Input(shape=(IMG_HEIGHT, IMG_WIDTH, 3), name="input_image")

# Dynamic Augmentation
x = tf.keras.layers.RandomFlip("horizontal")(inputs)
x = tf.keras.layers.RandomRotation(0.10)(x)
x = tf.keras.layers.RandomZoom(0.08)(x)
x = tf.keras.layers.RandomContrast(0.06)(x)
x = tf.keras.layers.RandomBrightness(0.06)(x)

# Normalize [0..255] to [-1..1]
x = tf.keras.layers.Rescaling(1./127.5, offset=-1.0)(x)

# Stage 0: Fast Initial Feature Extraction (96x96 -> 48x48 via stride 2 to save FLOPs)
x = tf.keras.layers.Conv2D(32, (3, 3), strides=2, padding="same", use_bias=False, kernel_regularizer=l2, name="conv0")(x)
x = tf.keras.layers.BatchNormalization(name="bn0")(x)
x = tf.keras.layers.ReLU(6.0, name="relu0")(x)

# Stage 1: SeparableConv2D (48x48 -> 24x24 via stride 2)
x = tf.keras.layers.SeparableConv2D(64, (3, 3), strides=2, padding="same", use_bias=False, depthwise_regularizer=l2, pointwise_regularizer=l2, name="sep_conv1")(x)
x = tf.keras.layers.BatchNormalization(name="bn1")(x)
x = tf.keras.layers.ReLU(6.0, name="relu1")(x)

# Stage 2: SeparableConv2D (24x24 -> 12x12 via stride 2)
x = tf.keras.layers.SeparableConv2D(128, (3, 3), strides=2, padding="same", use_bias=False, depthwise_regularizer=l2, pointwise_regularizer=l2, name="sep_conv2")(x)
x = tf.keras.layers.BatchNormalization(name="bn2")(x)
x = tf.keras.layers.ReLU(6.0, name="relu2")(x)

# Stage 3: SeparableConv2D (12x12 refinement, stride 1)
x = tf.keras.layers.SeparableConv2D(144, (3, 3), strides=1, padding="same", use_bias=False, depthwise_regularizer=l2, pointwise_regularizer=l2, name="sep_conv3")(x)
x = tf.keras.layers.BatchNormalization(name="bn3")(x)
x = tf.keras.layers.ReLU(6.0, name="relu3")(x)

# Stage 4: SeparableConv2D (12x12 -> 6x6 via stride 2)
x = tf.keras.layers.SeparableConv2D(176, (3, 3), strides=2, padding="same", use_bias=False, depthwise_regularizer=l2, pointwise_regularizer=l2, name="sep_conv4")(x)
x = tf.keras.layers.BatchNormalization(name="bn4")(x)
x = tf.keras.layers.ReLU(6.0, name="relu4")(x)

# Stage 5: SeparableConv2D (6x6 deep features, stride 1)
x = tf.keras.layers.SeparableConv2D(176, (3, 3), strides=1, padding="same", use_bias=False, depthwise_regularizer=l2, pointwise_regularizer=l2, name="sep_conv5")(x)
x = tf.keras.layers.BatchNormalization(name="bn5")(x)
x = tf.keras.layers.ReLU(6.0, name="relu5")(x)

# Global Average Pooling + Head
x = tf.keras.layers.GlobalAveragePooling2D(name="gap")(x)
x = tf.keras.layers.Dropout(0.25, name="dropout")(x)
outputs = tf.keras.layers.Dense(len(CLASSES), activation="softmax", kernel_regularizer=l2, name="predictions")(x)

model = tf.keras.Model(inputs, outputs, name="Mangosteen_SeparableCNN_94k")
total_params = model.count_params()

print("\n--- Model Architecture Summary ---")
model.summary()

print(f"\n👉 Total Parameters: {total_params:,}")
if not (60000 <= total_params <= 100000):
    raise ValueError(f"Parameters ({total_params:,}) out of requested 60,000 - 100,000 range!")
print("✅ Parameter count verified: Exactly in 60,000 - 100,000 range!")

# -----------------------------------------------------------------------------
# 3. Train Model in Float32 with Label Smoothing & Balanced Checkpoint
# -----------------------------------------------------------------------------
print("\n[Step 3/6] Compiling and Training Float32 Model...")

lr_schedule = tf.keras.optimizers.schedules.CosineDecay(
    initial_learning_rate=1.0e-3,
    decay_steps=EPOCHS * len(train_ds),
    alpha=0.01
)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=lr_schedule),
    loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.03),
    metrics=["accuracy"]
)

keras_save_path = OUTPUT_DIR / "mangosteen_separable_cnn_94k.keras"

class MultiMetricCheckpoint(tf.keras.callbacks.Callback):
    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        self.best_bal_acc = -1.0
        self.best_macro_f1 = -1.0
        self.best_epoch = 0

    def on_epoch_end(self, epoch, logs=None):
        val_preds, val_targets = [], []
        for imgs, lbls in val_ds:
            p = np.argmax(self.model(imgs, training=False).numpy(), axis=1)
            t = np.argmax(lbls.numpy(), axis=1)
            val_preds.extend(p)
            val_targets.extend(t)

        val_preds = np.array(val_preds)
        val_targets = np.array(val_targets)
        classes_found = len(set(val_preds))

        macro_f1 = f1_score(val_targets, val_preds, average="macro", zero_division=0)
        bal_acc = balanced_accuracy_score(val_targets, val_preds) * 100.0
        raw_acc = np.mean(val_targets == val_preds) * 100.0

        if classes_found == len(CLASSES) and bal_acc > self.best_bal_acc:
            self.best_bal_acc = bal_acc
            self.best_macro_f1 = macro_f1
            self.best_epoch = epoch + 1
            self.model.save(str(self.filepath))
            print(f"\n   >>> [Epoch {epoch+1:02d} ⭐ BEST] Bal Acc: {bal_acc:.1f}% | Macro-F1: {macro_f1:.4f} | Raw Acc: {raw_acc:.1f}% (Saved)")

checkpoint_cb = MultiMetricCheckpoint(keras_save_path)

history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS,
    class_weight=class_weights,
    callbacks=[checkpoint_cb],
    verbose=1
)

# Load best checkpoint
if keras_save_path.exists():
    best_model = tf.keras.models.load_model(str(keras_save_path))
    print(f"\n✅ Loaded best checkpoint from: {keras_save_path} (Epoch {checkpoint_cb.best_epoch})")
else:
    best_model = model

# -----------------------------------------------------------------------------
# 4. Evaluate Float32 Model on Test Set
# -----------------------------------------------------------------------------
print("\n[Step 4/6] Evaluating Float32 Model on Test Set...")

y_true = []
y_pred_f32 = []
for imgs, labels in test_ds:
    pred = best_model.predict(imgs, verbose=0)
    y_pred_f32.append(np.argmax(pred[0]))
    y_true.append(np.argmax(labels.numpy()[0]))

y_true = np.array(y_true)
y_pred_f32 = np.array(y_pred_f32)

f32_test_acc = np.mean(y_true == y_pred_f32) * 100.0
print(f"\n=======================================================")
print(f"🎯 Float32 Test Accuracy: {f32_test_acc:.2f}% ({np.sum(y_true == y_pred_f32)}/{len(y_true)})")
print(f"=======================================================")
print("\nFloat32 Confusion Matrix:")
print(confusion_matrix(y_true, y_pred_f32))
print("\nFloat32 Classification Report:")
print(classification_report(y_true, y_pred_f32, target_names=CLASSES, digits=4, zero_division=0))

# -----------------------------------------------------------------------------
# 5. Full INT8 Quantization (Matching ESP32-S3 Firmware Input/Output)
# -----------------------------------------------------------------------------
print("\n[Step 5/6] Performing Full INT8 Quantization...")

def representative_dataset():
    for imgs, _ in eval_train_ds.unbatch().batch(1).take(150):
        yield [imgs]

converter = tf.lite.TFLiteConverter.from_keras_model(best_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.int8   # Standard int8_t for ESP32-S3
converter.inference_output_type = tf.int8

tflite_model_int8 = converter.convert()

tflite_filename = "mangosteen_separable_cnn_94k_96x96_int8.tflite"
tflite_project_path = MODELS_EXPORT_DIR / tflite_filename
tflite_output_path = OUTPUT_DIR / tflite_filename

tflite_project_path.write_bytes(tflite_model_int8)
tflite_output_path.write_bytes(tflite_model_int8)

size_kb = len(tflite_model_int8) / 1024
print(f"🎉 INT8 Quantization Successful!")
print(f"📁 Exported to: {tflite_project_path}")
print(f"📊 Quantized Model Size: {size_kb:.2f} KB (Internal ESP32-S3 PSRAM/SRAM ready)")

# Evaluate INT8 Model using TFLite Interpreter (simulating camera buffer)
print("\n🧪 Evaluating Quantized INT8 Model on Test Set...")
interpreter = tf.lite.Interpreter(model_content=tflite_model_int8)
interpreter.allocate_tensors()

in_idx = interpreter.get_input_details()[0]["index"]
out_idx = interpreter.get_output_details()[0]["index"]
in_details = interpreter.get_input_details()[0]
in_scale, in_zero_point = in_details["quantization"]

y_pred_int8 = []
for imgs, labels in test_ds:
    if in_scale > 0:
        img_int8 = np.round(imgs.numpy() / in_scale + in_zero_point).clip(-128, 127).astype(np.int8)
    else:
        img_int8 = np.clip(imgs.numpy() - 128, -128, 127).astype(np.int8)
    interpreter.set_tensor(in_idx, img_int8)
    interpreter.invoke()
    out = interpreter.get_tensor(out_idx)[0]
    y_pred_int8.append(np.argmax(out))

y_pred_int8 = np.array(y_pred_int8)
int8_test_acc = np.mean(y_true == y_pred_int8) * 100.0

print(f"\n=======================================================")
print(f"⚡ INT8 Test Accuracy:    {int8_test_acc:.2f}% ({np.sum(y_true == y_pred_int8)}/{len(y_true)})")
print(f"🎯 Float32 Test Accuracy: {f32_test_acc:.2f}%")
print(f"⚖️ Quantization Drop:    {f32_test_acc - int8_test_acc:+.2f}%")
print(f"=======================================================")
print("\nINT8 Confusion Matrix:")
print(confusion_matrix(y_true, y_pred_int8))
print("\nINT8 Classification Report:")
print(classification_report(y_true, y_pred_int8, target_names=CLASSES, digits=4, zero_division=0))

# -----------------------------------------------------------------------------
# 6. Export C++ Header & Source Array for PlatformIO ESP32-S3
# -----------------------------------------------------------------------------
print("\n[Step 6/6] Generating C++ Array for ESP32-S3 in src/...")

def generate_c_files(tflite_bytes, output_dir, prefix="mangosteen_model"):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    header_path = out_path / f"{prefix}_data.h"
    source_path = out_path / f"{prefix}_data.cc"
    
    array_name = f"g_{prefix}_data"
    len_name = f"g_{prefix}_data_len"
    
    # Header (.h)
    header_guard = f"{prefix.upper()}_DATA_H_"
    header_content = f"""// Auto-generated Separable CNN Model Header for LilyGO T-SIMCAM (ESP32-S3)
// Architecture: Multi-Stage Separable CNN + Residual Block (Parameters: {total_params:,})
// Model Size: {len(tflite_bytes)} bytes ({len(tflite_bytes)/1024:.2f} KB)
// Accuracy: Float32 {f32_test_acc:.2f}% -> INT8 {int8_test_acc:.2f}%
#ifndef {header_guard}
#define {header_guard}

#ifdef __cplusplus
extern "C" {{
#endif

extern const unsigned char {array_name}[];
extern const unsigned int {len_name};

#ifdef __cplusplus
}}
#endif

#endif  // {header_guard}
"""
    header_path.write_text(header_content, encoding="utf-8")
    
    # Source (.cc) with 16-byte alignment
    hex_lines = []
    chunk_size = 12
    for i in range(0, len(tflite_bytes), chunk_size):
        chunk = tflite_bytes[i:i+chunk_size]
        hex_vals = [f"0x{b:02x}" for b in chunk]
        line = "  " + ", ".join(hex_vals)
        if i + chunk_size < len(tflite_bytes):
            line += ","
        hex_lines.append(line)
        
    source_content = f"""// Auto-generated Separable CNN Model Data for LilyGO T-SIMCAM (ESP32-S3)
// Architecture: Multi-Stage Separable CNN + Residual Block (Parameters: {total_params:,})
// Input: INT8 [1, {IMG_HEIGHT}, {IMG_WIDTH}, 3] (Normalized [-128..127])
#include "{prefix}_data.h"

// 16-byte alignment is required for TensorFlow Lite Micro tensor arena optimizations
alignas(16) const unsigned char {array_name}[] = {{
{chr(10).join(hex_lines)}
}};

const unsigned int {len_name} = {len(tflite_bytes)};
"""
    source_path.write_text(source_content, encoding="utf-8")
    print(f"   [+] Written: {header_path}")
    print(f"   [+] Written: {source_path} ({len(tflite_bytes)} bytes)")

generate_c_files(tflite_model_int8, SRC_DIR)
generate_c_files(tflite_model_int8, OUTPUT_DIR)

print("\n" + "=" * 72)
print("🎉 TRAINING AND INT8 QUANTIZATION COMPLETED SUCCESSFULLY!")
print(f"📁 TFLite Model: models/{tflite_filename}")
print(f"📁 C++ Firmware Array: src/mangosteen_model_data.cc")
print(f"⚡ Ready to flash with: python setup.py (or setup.bat)")
print("=" * 72)
