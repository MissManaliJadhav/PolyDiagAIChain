import numpy as np
import cv2
import tensorflow as tf

# =============================
# 1. Gaussian Noise
# =============================
def add_gaussian_noise(image):
    noise = np.random.normal(0, 0.05, image.shape)
    noisy = image + noise
    noisy = np.clip(noisy, 0, 1)
    return noisy


# =============================
# 2. Image Perturbation
# =============================
def perturb_image(image):
    image_uint8 = (image * 255).astype(np.uint8)

    blurred = cv2.GaussianBlur(image_uint8, (5, 5), 0)
    rows, cols = image_uint8.shape[:2]

    M = cv2.getRotationMatrix2D((cols/2, rows/2), 10, 1)
    perturbed = cv2.warpAffine(blurred, M, (cols, rows))

    perturbed = perturbed / 255.0
    return perturbed


# =============================
# 3. FGSM ATTACK
# =============================
def fgsm_attack(model, image, epsilon=0.01):

    if len(image.shape) == 3:
        image = np.expand_dims(image, axis=0)

    image = tf.convert_to_tensor(image, dtype=tf.float32)

    with tf.GradientTape() as tape:
        tape.watch(image)
        prediction = model(image)

        label = tf.argmax(prediction, axis=1)
        loss = tf.keras.losses.sparse_categorical_crossentropy(label, prediction)

    gradient = tape.gradient(loss, image)
    signed_grad = tf.sign(gradient)

    adversarial = image + epsilon * signed_grad
    adversarial = tf.clip_by_value(adversarial, 0, 1)

    return adversarial.numpy()[0]