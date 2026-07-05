"""
Animal-10 Image Classifier — FastAPI Backend
Model: DenseNet121 fine-tuned on Animals-10 dataset
Classes: butterfly, horse, spider, squirrel, cow, chicken, dog, sheep, cat, elephant
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse , HTMLResponse
import numpy as np
import cv2
import base64
import io
import os
from PIL import Image

app = FastAPI(title="Animal Classifier API", version="1.0.0")

# Allow frontend dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Class config (Italian training order → English) ──────────────────────────
CLASS_NAMES_IT = [
    "cane", "cavallo", "elefante", "farfalla", "gallina",
    "gatto", "mucca", "pecora", "ragno", "scoiattolo"
]
CLASS_NAMES_EN = {
    "cane":      "Dog",
    "cavallo":   "Horse",
    "elefante":  "Elephant",
    "farfalla":  "Butterfly",
    "gallina":   "Chicken",
    "gatto":     "Cat",
    "mucca":     "Cow",
    "pecora":    "Sheep",
    "ragno":     "Spider",
    "scoiattolo":"Squirrel",
}
CLASS_EMOJIS = {
    "Dog": "🐕", "Horse": "🐴", "Elephant": "🐘", "Butterfly": "🦋",
    "Chicken": "🐔", "Cat": "🐱", "Cow": "🐄", "Sheep": "🐑",
    "Spider": "🕷️", "Squirrel": "🐿️",
}

IMG_SIZE = (128, 128)

# ── Lazy model loading ────────────────────────────────────────────────────────
model = None

def get_model():
    global model
    if model is not None:
        return model

    import tensorflow as tf

    # Try common save locations
    candidates = [
        "my_model.keras",
        "model_animal10.keras",
        "../my_model.keras",
        os.environ.get("MODEL_PATH", ""),
    ]
    for path in candidates:
        if path and os.path.exists(path):
            print(f"Loading model from: {path}")
            model = tf.keras.models.load_model(path, compile=False)
            return model

    raise FileNotFoundError(
        "Model file not found. Place 'my_model.keras' in the backend directory "
        "or set MODEL_PATH environment variable."
    )


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """Decode image bytes → normalised (1, 128, 128, 3) array."""
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image.")
    img = cv2.resize(img, IMG_SIZE)
    return img, np.expand_dims(img / 255.0, axis=0)


def make_gradcam(img_array: np.ndarray, mdl) -> np.ndarray:
    """Produce Grad-CAM heatmap overlay using DenseNet conv4_block24_concat."""
    import tensorflow as tf

    try:
        base_model = mdl.get_layer("densenet121")
        target_layer = base_model.get_layer("conv4_block24_concat")
        grad_model = tf.keras.Model(
            inputs=base_model.input,
            outputs=[target_layer.output, base_model.output],
        )

        with tf.GradientTape() as tape:
            conv_outputs, base_outputs = grad_model(img_array)
            x = base_outputs
            for layer in mdl.layers[1:]:
                x = layer(x)
            predictions = x
            pred_index = tf.argmax(predictions[0])
            class_channel = predictions[:, pred_index]

        grads = tape.gradient(class_channel, conv_outputs)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_outputs = conv_outputs[0]
        heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-8)
        return heatmap.numpy()
    except Exception as e:
        print(f"Grad-CAM failed: {e}")
        return None


def encode_image(img_bgr: np.ndarray) -> str:
    """BGR numpy array → base64 PNG string."""
    _, buffer = cv2.imencode(".png", img_bgr)
    return base64.b64encode(buffer).decode("utf-8")


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()



@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/classes")
def classes():
    return {
        "classes": [
            {"id": i, "italian": it, "english": CLASS_NAMES_EN[it], "emoji": CLASS_EMOJIS[CLASS_NAMES_EN[it]]}
            for i, it in enumerate(CLASS_NAMES_IT)
        ]
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    # ── Validate ──────────────────────────────────────────────────────────
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    image_bytes = await file.read()
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10 MB).")

    try:
        img_bgr, img_array = preprocess_image(image_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # ── Load model & predict ──────────────────────────────────────────────
    try:
        mdl = get_model()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    preds = mdl.predict(img_array, verbose=0)[0]
    pred_idx = int(np.argmax(preds))
    pred_it = CLASS_NAMES_IT[pred_idx]
    pred_en = CLASS_NAMES_EN[pred_it]
    confidence = float(preds[pred_idx])

    # All class probabilities
    all_probs = [
        {
            "class": CLASS_NAMES_EN[it],
            "emoji": CLASS_EMOJIS[CLASS_NAMES_EN[it]],
            "probability": float(preds[i]),
        }
        for i, it in enumerate(CLASS_NAMES_IT)
    ]
    all_probs.sort(key=lambda x: x["probability"], reverse=True)

    # ── Grad-CAM ──────────────────────────────────────────────────────────
    heatmap = make_gradcam(img_array, mdl)
    gradcam_b64 = None
    if heatmap is not None:
        heatmap_resized = cv2.resize(heatmap, IMG_SIZE)
        heatmap_uint8 = np.uint8(255 * heatmap_resized)
        heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        img_uint8 = np.uint8(img_bgr)
        overlay = cv2.addWeighted(img_uint8, 0.6, heatmap_color, 0.4, 0)
        gradcam_b64 = encode_image(overlay)

    # Original image b64
    original_b64 = encode_image(img_bgr)

    return JSONResponse({
        "prediction": pred_en,
        "emoji": CLASS_EMOJIS[pred_en],
        "confidence": confidence,
        "confidence_pct": f"{confidence * 100:.1f}%",
        "all_probabilities": all_probs,
        "original_image": original_b64,
        "gradcam_image": gradcam_b64,
    })
