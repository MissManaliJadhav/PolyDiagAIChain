import tensorflow as tf
import numpy as np
import cv2
classes = ['Normal', 'Pneumonia']
IMAGE_SHAPE = (224, 224)
# ✅ Correct path
model = tf.keras.models.load_model("pneumonia")
def pred_model(img_path, return_model=False):
    image = cv2.imread(img_path)

    if image is None:
        raise ValueError("Image not found")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, IMAGE_SHAPE)

    image = image / 255.0
    image = np.reshape(image, (1, 224, 224, 3))

    prediction = model.predict(image)

    prob = float(np.max(prediction))
    class_idx = int(np.argmax(prediction))

    class_result = classes[class_idx]

    if return_model:
        return class_result, prob, model, image,classes

    return class_result, prob