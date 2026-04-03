#import tensorflow as tf
#def load_and_prep_bt(filepath):
"""
    img = tf.io.read_file(filepath)
    img = tf.io.decode_image(img)
    img = tf.image.resize(img, (224, 224))
    return img
class_names = ['glioma_tumor', 'meningioma_tumor', 'no_tumor', 'pituitary_tumor']
def pred_model_bt(filepath):
    img = load_and_prep_bt(filepath)
    model = tf.keras.models.load_model("Brain_tumor")
    with tf.device('/cpu:0'):
        pred_prob = model.predict(tf.expand_dims(img, axis=0))
        pred_class = class_names[pred_prob.argmax()]

    return pred_class, pred_prob.max()
"""
# filepath = "testing_input/brain_tumor/no_tumor.jpg"
# print(pred_model_bt(filepath))
import tensorflow as tf
import numpy as np
import cv2

# ================================
# CLASS LABELS (MULTI-CLASS)
# ================================
classes = ['Glioma', 'Meningioma', 'No Tumor', 'Pituitary']

# ================================
# LOAD MODEL (ONLY ONCE)
# ================================
model = tf.keras.models.load_model("Brain_tumor")


# ================================
# IMAGE PREPROCESSING
# ================================
IMAGE_SIZE = (224, 224)

def load_and_prep_image(img_path):
    image = cv2.imread(img_path)

    if image is None:
        raise ValueError("Image not found or path incorrect")

    image = cv2.resize(image, IMAGE_SIZE)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   # ✅ important
    image = image / 255.0

    return image


# ================================
# MAIN PREDICTION FUNCTION
# ================================
def pred_model_bt(img_path, return_model=False):

    image = load_and_prep_image(img_path)

    image_exp = np.expand_dims(image, axis=0)

    prediction = model.predict(image_exp)

    class_idx = np.argmax(prediction)
    prob = np.max(prediction)

    result = classes[class_idx]

    # ✅ return for AI analysis
    if return_model:
        return result, prob, model, image_exp, classes
    else:
        return result, prob