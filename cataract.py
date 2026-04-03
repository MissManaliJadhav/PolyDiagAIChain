import tensorflow as tf
import numpy as np
import cv2

# ================================
# CLASS LABELS
# ================================
classes = ['Normal', 'Cataract']

# ================================
# LOAD MODEL
# ================================
model = tf.keras.models.load_model("Cataract")

# ================================
# IMAGE PREPROCESSING
# ================================
IMAGE_SIZE = (224, 224)

def load_and_prep_image(img_path):
    image = cv2.imread(img_path)

    if image is None:
        raise ValueError("Image not found")

    image = cv2.resize(image, IMAGE_SIZE)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image / 255.0

    return image


# ================================
# PREDICTION FUNCTION
# ================================
def pred_model_ct(img_path, return_model=False):

    image = load_and_prep_image(img_path)
    image_exp = np.expand_dims(image, axis=0)

    prediction = model.predict(image_exp)

    class_idx = np.argmax(prediction)
    prob = np.max(prediction)

    result = classes[class_idx]

    if return_model:
        return result, prob, model, image_exp, classes
    else:
        return result, prob