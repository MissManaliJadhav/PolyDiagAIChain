import tensorflow as tf
import numpy as np
import cv2

# ================================
# CLASS LABELS
# ================================
classes = ['Normal', 'Tuberculosis']

# ================================
# IMAGE SIZE (keep your original)
# ================================
IMAGE_SHAPE = (96, 96)

# ================================
# LOAD MODEL (ONCE ONLY)
# ================================
model = tf.keras.models.load_model("TB")


# ================================
# IMAGE PREPROCESSING
# ================================
def load_and_prep_tb(img_path):

    image = cv2.imread(img_path)

    if image is None:
        raise ValueError("Image not found")

    image = cv2.resize(image, IMAGE_SHAPE)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image = image / 255.0   # ✅ VERY IMPORTANT

    return image


# ================================
# PREDICTION FUNCTION (FINAL)
# ================================
def pred_model_tb(img_path, return_model=False):

    image = load_and_prep_tb(img_path)

    image_exp = np.expand_dims(image, axis=0)

    prediction = model.predict(image_exp)

    class_idx = np.argmax(prediction)
    prob = np.max(prediction)

    result = classes[class_idx]

    # ✅ Required for AI Analysis
    if return_model:
        return result, prob, model, image_exp, classes
    else:
        return result, prob