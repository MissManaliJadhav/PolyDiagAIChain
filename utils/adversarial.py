import numpy as np
import cv2
import tensorflow as tf

# =============================
# 1. Gaussian Noise
# =============================
def add_gaussian_noise(image):
    noise = np.random.normal(0, 25, image.shape).astype(np.uint8)
    return cv2.add(image, noise)


# =============================
# 2. Image Perturbation
# =============================
def perturb_image(image):
    blurred = cv2.GaussianBlur(image, (5,5), 0)
    rows, cols = image.shape[:2]
    M = cv2.getRotationMatrix2D((cols/2, rows/2), 10, 1)
    return cv2.warpAffine(blurred, M, (cols, rows))


# =============================
# 3. FGSM ATTACK (REAL)
# =============================
def fgsm_attack(model, image, epsilon=0.01):
    image = tf.convert_to_tensor(image, dtype=tf.float32)
    image = tf.expand_dims(image, axis=0)

    with tf.GradientTape() as tape:
        tape.watch(image)
        prediction = model(image)
        label = tf.argmax(prediction, axis=1)
        loss = tf.keras.losses.sparse_categorical_crossentropy(label, prediction)

    gradient = tape.gradient(loss, image)
    signed_grad = tf.sign(gradient)

    adversarial = image + epsilon * signed_grad
    adversarial = tf.clip_by_value(adversarial, 0, 255)

    return adversarial.numpy()[0]