import numpy as np
import cv2
import tensorflow as tf
# Import attacks
from utils.adversarial import add_gaussian_noise, perturb_image, fgsm_attack
# -----------------------------------
# UNIVERSAL IMAGE ANALYSIS
# -----------------------------------
def print_ai_analysis(model_function, img_path):

    print("\n========== AI ROBUSTNESS ANALYSIS ==========")

    # Get prediction + model + processed image
    class_result, prob, model, image , classes = model_function(img_path, return_model=True)

    print("\n[ ORIGINAL IMAGE ]")
    print(f"Prediction : {class_result}")
    print(f"Confidence : {round(prob*100,2)}%")

    # =============================
    # 1. Gaussian Noise
    # =============================
    noisy_img = add_gaussian_noise(image[0])
    noisy_pred = model.predict(np.expand_dims(noisy_img, axis=0))

    noisy_class = np.argmax(noisy_pred)
    noisy_prob = np.max(noisy_pred)

    print("\n[ GAUSSIAN NOISE ]")
    print(f"Prediction : {classes[noisy_class]}")
    print(f"Confidence : {round(noisy_prob*100,2)}%")

    # =============================
    # 2. Perturbation
    # =============================
    pert_img = perturb_image(image[0])
    pert_pred = model.predict(np.expand_dims(pert_img, axis=0))

    pert_class = np.argmax(pert_pred)
    pert_prob = np.max(pert_pred)

    print("\n[ IMAGE PERTURBATION ]")
    print(f"Prediction : {classes[pert_class]}")
    print(f"Confidence : {round(pert_prob*100,2)}%")

    # =============================
    # 3. FGSM Attack (REAL)
    # =============================
    adv_img = fgsm_attack(model, image[0])
    adv_pred = model.predict(np.expand_dims(adv_img, axis=0))

    adv_class = np.argmax(adv_pred)
    adv_prob = np.max(adv_pred)

    print("\n[ FGSM ATTACK ]")
    print(f"Prediction : {classes[adv_class]}")
    print(f"Confidence : {round(adv_prob*100,2)}%")

    # =============================
    # Robustness Logic
    # =============================
    original_pred = model.predict(image)
    original_class = np.argmax(original_pred)
    if original_class == noisy_class == pert_class == adv_class:
        robustness = "Stable"
    else:
        robustness = "Sensitive"

    # =============================
    # Trust Score (IMPROVED)
    # =============================
    trust_score = round(
        (prob * 0.6) +
        (1.0 if robustness == "Stable" else 0.5) * 0.4,
        2
    )

    print("\n[ FINAL ANALYSIS ]")
    print(f"Robustness : {robustness}")
    print(f"Trust Score : {trust_score}")

    print("\n========== END ANALYSIS ==========")