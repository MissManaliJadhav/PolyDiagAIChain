import os
import csv
import pickle
import sklearn
import webbrowser
import numpy as np
import pandas as pd
from pneumonia import pred_model
from maps import current_location
from cataract import pred_model_ct
from brain_tumor import pred_model_bt
from tuberculosis import pred_model_tb
from insurance import insurance_predict
from blockchain.blockchain_service import (store_prediction,get_all_records,get_patient_records,get_blockchain_logs)
from flask import session, redirect, url_for, request, render_template, flash , Flask
import sqlite3
from utils.trust_score import calculate_trust
from utils.recommendations import get_recommendations
from utils.explain_ai import simple_explain
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps
import hashlib
from ai_analysis import print_ai_analysis
from utils.adversarial import add_gaussian_noise, perturb_image, fgsm_attack
import cv2
app = Flask(__name__)
app.secret_key = "multidisease_secret_key"
blockchain_logs=[]
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function
def role_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            user_role = session.get("role")
            if not user_role:
                return redirect(url_for("login"))
            if user_role.lower() not in [r.lower() for r in allowed_roles]:
                return "Access Denied"
            return f(*args, **kwargs)
        return wrapper
    return decorator
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS diagnosis(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    disease TEXT,
    result TEXT,
    trust_score TEXT,
    blockchain_hash TEXT
)
""")
    conn.commit()
    conn.close()
init_db()

# ===============================
# UNIVERSAL DIAGNOSIS SAVE FUNCTION
# ===============================
def save_diagnosis(disease, result, trust_score, blockchain_hash):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    patient_id = session.get("user_id")
    doctor_id = session.get("doctor_id")

    cursor.execute("""
        INSERT INTO diagnosis
        (patient_id, doctor_id, disease, result, trust_score, blockchain_hash)
        VALUES (?,?,?,?,?,?)
    """, (
        patient_id,
        doctor_id,
        disease,
        result,
        trust_score,
        blockchain_hash
    ))

    conn.commit()
    conn.close()

diabetes_model = pickle.load(open('models/diabetes_model.sav', 'rb'))
heart_disease_model = pickle.load(open('models/heart_disease_model.sav', 'rb'))
parkinsons_model = pickle.load(open('models/parkinsons_model.sav', 'rb'))
otherdiseases_model = pickle.load(open('models/otherdiseases.sav', 'rb'))
asthma_model = pickle.load(open('models/asthma_model.sav', 'rb'))
latitude, longitude = current_location()
# reading csv and converting the data to integer
def open_csv(filepath, filename):
    with open(filepath + filename, mode='r') as file:
        csvFile = csv.reader(file)

        for lines in csvFile:
            arr = lines

        data = list(map(float, arr))
        return data


latitude, longitude = current_location()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'csv'}

# Input from form and conversion of data into dataframe for training
@app.route('/db_form', methods=['GET', 'POST'])
def db_form():
    global predictions, file_name, predictions1, predictions2, predictions3, predictions4, predictions5, data
    error = ''
    latitude, longitude = current_location()
    if request.method == "POST":

        fullname = request.form.get("fullname")

        preg = request.form.get("preg")

        glucose = request.form.get("glucose")

        bp = request.form.get("bp")

        skin = request.form.get("skin")

        insulin = request.form.get("insulin")

        bmi = request.form.get("bmi")

        dpf = request.form.get("dpf")

        age = request.form.get("age")

        data = [preg, glucose, bp, skin, insulin, bmi, dpf, age]
        data_conv = np.array([data])
        data_csv = pd.DataFrame(data_conv,
                                columns=['Pregnancies', 'Glucose', 'Blood Pressure', 'SkinThickness', 'Insulin', 'BMI',
                                         'Diabetes Pedigree Function', 'Age'])

        print(data_csv)
        data = list(map(float, data))

        # compare_data = compare_input(data, DB_Models)
        if len(data) == 8:

            # changing the input_data_diabetes to numpy array
            input_data_diabetes_as_numpy_array = np.asarray(data)
            # reshape the array as we are predicting for one instance
            input_data_diabetes_reshaped = input_data_diabetes_as_numpy_array.reshape(1, -1)
            # prediction = diabetes_model.predict(input_data_diabetes_reshaped)
            print(input_data_diabetes_reshaped)
            prediction1 = diabetes_model.predict(input_data_diabetes_reshaped)

            # Accuracies
            model = diabetes_model.predict_proba(input_data_diabetes_reshaped)
            acc = model.max()
            if (prediction1[0] == 0):
                result = 'The Patient does not have Diabetes'
            else:
                result = 'The Patient has Diabetes'

            confidence = f"{round(acc * 100, 2)}%"
            trust_score = calculate_trust(acc)
            predictions = f"{result} | Confidence: {confidence} | Trust :{trust_score}"
            patient_hash = hashlib.sha256(fullname.encode()).hexdigest()
            blockchain_result= f"{result} | Trust Score :{trust_score}"

            txid=store_prediction(
                patient_name=patient_hash,
                disease="Diabetes",
                result=blockchain_result
                #confidence=confidence
                #timestamp=str(datetime.now())
)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            blockchain_logs.append({
                "hash": txid,
                "patient_hash": patient_hash,
                "disease": "Diabetes",
                "model": "ML Model",
                "time": timestamp
            })
            # ===== SAVE INTO DATABASE =====
            block_hash = patient_hash
            save_diagnosis("Diabetes", result, trust_score, txid)
            #trust_score = calculate_trust(acc)
            recommendation = get_recommendations("Diabetes", result)
            features = [
                "Pregnancies","Glucose","Blood Pressure",
                "SkinThickness","Insulin","BMI",
                "DPF","Age"
]
            explanation = simple_explain(features, [data], result)
            #explanation = simple_explain("Diabetes", data)

# Fake blockchain tx id display (optional)
            tx_hash = "Stored in Blockchain"

        if (len(error) == 0):
            return render_template('results.html',lat=latitude,lng=longitude,type="csv",disease="db",predictions=predictions,model="db",data=data_csv.to_html(classes='mystyle', index=False),
    # ⭐ NEW FEATURES
    trust_score=trust_score,
    recommendation=recommendation,
    explanation=explanation,
    tx_hash=tx_hash
)
        else:
            return render_template('index.html', error=error)

    return render_template("diabetes_form.html")


# Input from form and conversion of data into dataframe for training
@app.route('/hd_form', methods=['GET', 'POST'])
def hd_form():
    global predictions, file_name, predictions1, predictions2, predictions3, predictions4, predictions5, data
    error = ''
    latitude, longitude = current_location()
    if request.method == "POST":

        fullname = request.form.get("fullname")

        age = request.form.get("age")

        sex = request.form.get("sex")

        cp = request.form.get("cp")

        trestbps = request.form.get("trestbps")

        chol = request.form.get("chol")

        fbs = request.form.get("fbs")

        restecg = request.form.get("restecg")

        thalach = request.form.get("thalach")

        exang = request.form.get("exang")

        oldpeak = request.form.get("oldpeak")

        slope = request.form.get("slope")

        ca = request.form.get("ca")

        thal = request.form.get("thal")

        data = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
        data_conv = np.array([data])
        data_csv = pd.DataFrame(data_conv,
                                columns=["age","sex","cp","trestbps","chol","fbs","restecg","thalach",
         "exang","oldpeak","slope","ca","thal"])

        print(data_csv)
        data = list(map(float, data))

        if (len(data) == 13):

            input_data_heartd_as_numpy_array = np.asarray(data)
            # reshape the numpy array as we are predicting for only on instance
            input_data_heartd_reshaped = input_data_heartd_as_numpy_array.reshape(1, -1)

            prediction1 = heart_disease_model.predict(input_data_heartd_reshaped)

            # Accuracies
            model = heart_disease_model.predict_proba(input_data_heartd_reshaped)
            acc = model.max()
            if (prediction1[0] == 0):
                result = 'The Patient does not have Heart Disease'
            else:
                result = 'The Patient has Heart Disease'

            confidence = f"{round(acc * 100, 2)}%"
            trust_score = calculate_trust(acc)
            predictions = f"{result} | Confidence: {confidence} | Trust: {trust_score}"
            patient_hash = hashlib.sha256(fullname.encode()).hexdigest()
            blockchain_result= f"{result} | Trust Score :{trust_score}"

            txid=store_prediction(
                patient_name=patient_hash,
                disease="Heart Disease",
                result=blockchain_result,
                #confidence=confidence
                #timestamp=str(datetime.now())
)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            blockchain_logs.append({
                "hash": txid,
                "patient_hash": patient_hash,
                "disease": "Heart",
                "model": "ML Model",
                "time": timestamp
            })
            # ================= AI EXTRA FEATURES =================
            #trust_score = calculate_trust(acc)
            save_diagnosis("Heart Disease", result, trust_score, txid)
            recommendation = get_recommendations("Heart Disease", result)
            features = [
"age","sex","cp","trestbps","chol","fbs",
"restecg","thalach","exang","oldpeak",
"slope","ca","thal"
]

            explanation = simple_explain(features, [data], result)
            #explanation = simple_explain("Heart Disease", data)
            tx_hash = "Stored in Blockchain"
        if (len(error) == 0):
            return render_template('results.html',lat=latitude,lng=longitude,type="csv",disease="hd",predictions=predictions,model="hd",data=data_csv.to_html(classes='mystyle', index=False),trust_score=trust_score,recommendation=recommendation,explanation=explanation,tx_hash=tx_hash
)
        else:
            return render_template('index.html', error=error)

    return render_template("heart_disease_form.html")


# Input from form and conversion of data into dataframe for training
@app.route('/pk_form', methods=['GET', 'POST'])
def pk_form():
    global predictions, file_name, predictions1, predictions2, predictions3, predictions4, predictions5, data
    error = ''
    latitude, longitude = current_location()
    if request.method == "POST":

        fullname = request.form.get("fullname")

        a = request.form.get("1")

        b = request.form.get("2")

        c = request.form.get("3")

        d = request.form.get("4")

        e = request.form.get("5")

        f = request.form.get("6")

        g = request.form.get("7")

        h = request.form.get("8")

        i = request.form.get("9")

        j = request.form.get("10")

        k = request.form.get("11")

        l = request.form.get("12")

        m = request.form.get("13")

        n = request.form.get("14")

        o = request.form.get("15")

        p = request.form.get("16")

        q = request.form.get("17")

        r = request.form.get("18")

        s = request.form.get("19")

        t = request.form.get("20")

        u = request.form.get("21")

        v = request.form.get("22")

        data = [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v]
        data_conv = np.array([data])
        data_csv = pd.DataFrame(data_conv, columns=["MDVP:Fo(Hz)", "MDVP:Fhi(Hz)", "MDVP:Flo(Hz)", "MDVP:Jitter(%)",
                                                    "MDVP:Jitter(Abs)", "MDVP:RAP", "MDVP:PPQ", "Jitter:DDP",
                                                    "MDVP:Shimmer", "MDVP:Shimmer(dB)", "Shimmer:APQ3", "Shimmer:APQ5",
                                                    "MDVP:APQ", "Shimmer:DDA", "NHR", "HNR", "RPDE", "DFA", "spread1",
                                                    "spread2", "D2", "PPE"])

        print(data)
        data = list(map(float, data))

        if (len(data) == 22):
            input_data_parkinsons_as_numpy_array = np.round_(data, decimals=4)

            input_data_parkinsons_reshaped = input_data_parkinsons_as_numpy_array.reshape(1, -1)

            prediction1 = parkinsons_model.predict(input_data_parkinsons_reshaped)

            # Accuracies

            model = parkinsons_model.predict_proba(input_data_parkinsons_reshaped)
            acc = model.max()
            if (prediction1[0] == 0):
                result = 'The Patient does not have Parkinsons'
            else:
                result = 'The Patient has Parkinsons'

            confidence = f"{round(acc * 100, 2)}%"
            trust_score = calculate_trust(acc)
            predictions = f"{result} | Confidence: {confidence} | Trust: {trust_score}"
            patient_hash = hashlib.sha256(fullname.encode()).hexdigest()
            blockchain_result= f"{result} | Trust Score :{trust_score}"

            txid=store_prediction(
                patient_name=patient_hash,
                disease="Parkinsons",
                result=blockchain_result,
                #confidence=confidence
                #timestamp=str(datetime.now())
)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            blockchain_logs.append({
                "hash": txid,
                "patient_hash": patient_hash,
                "disease": "Parkinsons",
                "model": "ML Model",
                "time": timestamp
            })
            #trust_score = calculate_trust(acc)
            save_diagnosis("Parkinsons", result, trust_score, txid)
            recommendation = get_recommendations("Parkinsons", result)
            features = [f"Feature_{i}" for i in range(1,23)]
            explanation = simple_explain(features, [data], result)
            #explanation = simple_explain("Parkinsons", data)
            tx_hash = "Stored in Blockchain"
        if (len(error) == 0):
            return render_template('results.html',lat=latitude,lng=longitude,type="csv",disease="pk",predictions=predictions,model="pk",data=data_csv.to_html(classes='mystyle', index=False),trust_score=trust_score,recommendation=recommendation,explanation=explanation,tx_hash=tx_hash
)
        else:
            return render_template('index.html', error=error)

    return render_template("parkinsons_form.html")


# Input from form and convertion of data into dataframe for training
@app.route('/od_form', methods=['GET', 'POST'])
def od_form():
    global predictions, file_name, predictions1, predictions2, predictions3, predictions4, predictions5, data
    error = ''
    latitude, longitude = current_location()
    if request.method == "POST":

        fullname = request.form.get("fullname")

        a = request.form.get("1")

        b = request.form.get("2")

        c = request.form.get("3")

        d = request.form.get("4")

        e = request.form.get("5")

        f = request.form.get("6")

        g = request.form.get("7")

        h = request.form.get("8")

        i = request.form.get("9")

        j = request.form.get("10")

        k = request.form.get("11")

        l = request.form.get("12")

        m = request.form.get("13")

        n = request.form.get("14")

        o = request.form.get("15")

        p = request.form.get("16")

        q = request.form.get("17")

        r = request.form.get("18")

        s = request.form.get("19")

        t = request.form.get("20")

        u = request.form.get("21")

        v = request.form.get("22")

        w = request.form.get("23")

        x = request.form.get("24")

        y = request.form.get("25")

        z = request.form.get("26")

        aa = request.form.get("27")

        ab = request.form.get("28")

        ac = request.form.get("29")

        ad = request.form.get("30")

        ae = request.form.get("31")

        af = request.form.get("32")

        ag = request.form.get("33")

        data = [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, aa, ab, ac, ad, ae, af,
                ag]
        data_conv = np.array([data])
        data_csv = pd.DataFrame(data_conv,
                                columns=["itching", "skin_rash", "shivering", "chills", "vomiting", "fatigue",
                                         "high_fever", "headache", "yellowish_skin", "nausea", "loss_of_appetite",
                                         "pain_behind_the_eyes", "abdominial_pain", "diarrhoea", "mild_fever",
                                         "yellowing_of_eyes", "malaise", "runny_nose", "chest_pain",
                                         "pain_in_anal_region", "neck_pain", "dizziness", "swollen_extremeties",
                                         "slurred_speech", "loss_of_balance", "bladder_discomfort", "irritability",
                                         "increased_appetite", "stomach_bleeding", "painful_walking",
                                         "small_dents_in_nails", "blister", "prognosis"])

        print(data_csv)
        data = list(map(float, data))

        if (len(data) == 33):
            new_data = np.asarray(data)
            new_data2 = new_data.reshape(1, -1)
            # compute probabilities of assigning to each of the classes of prognosis
            probaDT = otherdiseases_model.predict_proba(new_data2)
            probaDT.round(4)  # round probabilities to four decimal places, if applicabl

            data = new_data2

            # Accuracies
            knn = otherdiseases_model.predict_proba(new_data2)
            acc = knn.max()

            #pred1 = otherdiseases_model.predict(new_data2)
            #predictions = f"{pred1[0]}" + f'{(round(acc, 3) * 100)}%'
            
            pred1 = otherdiseases_model.predict(new_data2)
            result = pred1[0]
            confidence = f"{round(acc * 100, 2)}%"
            trust_score = calculate_trust(acc)
            predictions = f"{result} | Confidence: {confidence} | Trust: {trust_score}"
            patient_hash = hashlib.sha256(fullname.encode()).hexdigest()
            blockchain_result= f"{result} | Trust Score :{trust_score}"
            txid=store_prediction(
                patient_name=patient_hash,
                disease="Other Disease",
                result=blockchain_result,
                
)
            save_diagnosis("Other Disease", result, trust_score, txid)
            recommendation = get_recommendations("Other Disease", result)
            features = list(data_csv.columns[:-1])
            explanation = simple_explain(features, data[0], result)
            tx_hash = "Stored in Blockchain"

        if (len(error) == 0):
            return render_template('results.html',lat=latitude,lng=longitude,type="csv",disease="od",
    predictions=predictions,model="od",data=data_csv.to_html(classes='mystyle', index=False),trust_score=trust_score,recommendation=recommendation,explanation=explanation,tx_hash=tx_hash
)
        else:
            return render_template('index.html', error=error)

    return render_template("other_diseases_form.html")


# Input form for insurance
@app.route('/insurance_form', methods=['GET', 'POST'])
def insurance_form():
    global predictions, file_name, predictions1, predictions2, predictions3, predictions4, predictions5, data
    error = ''
    latitude, longitude = current_location()
    if request.method == "POST":

        fullname = request.form.get("fullname")

        region = request.form.get("region")

        smoker = request.form.get("smoker")

        children = request.form.get("children")

        sex = request.form.get("sex")

        bmi = request.form.get("bmi")

        age = request.form.get("age")

        data = [age, sex, bmi, children, smoker, region]
        data_conv = np.array([data])
        data_csv = pd.DataFrame(data_conv,
                                columns=['age', 'sex', 'bmi', 'children', 'smoker', 'region'])

        print(data_csv)
        data = list(map(float, data))

        predictions = insurance_predict(data)

        if len(error) == 0:
            return render_template('insurance_results.html', type="csv",
                                   predictions=predictions,
                                   data=data_csv.to_html(classes='mystyle', index=False))
        else:
            return render_template('index.html', error=error)

    return render_template("insurance_form.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXT


# A common upload function for all pneumonia, HD, PK, DB and OD
@app.route('/success', methods=['GET', 'POST'])
def success():
    trust_score = None
    recommendation = None
    explanation = None
    tx_hash = None
    global predictions, file_name, data, data_csv, answer, latitude, longitude
    error = ''
    target_img = os.path.join(os.getcwd(), 'static/images/')
    latitude, longitude = current_location()
    if request.method == 'POST':

        if request.files:
            file = request.files['file']

            if file and allowed_file(file.filename):

                file.save(os.path.join(target_img, file.filename))
                img_path = os.path.join(target_img, file.filename)
                file_name = file.filename

                if ".csv" in file.filename:

                    data = open_csv('static/images/', file.filename)

                    f = f"static/images/{file.filename}"
                    data_csv = []
                    with open(f) as file:
                        csvfile = csv.reader(file)
                        for row in csvfile:
                            data_csv.append(row)
                    data_csv = pd.DataFrame(data_csv)

                    if (len(data) == 8 and "Glucose" in data_csv.columns[0]):

                        # changing the input_data_diabetes to numpy array
                        input_data_diabetes_as_numpy_array = np.asarray(data)
                        # reshape the array as we are predicting for one instance
                        input_data_diabetes_reshaped = input_data_diabetes_as_numpy_array.reshape(1, -1)
                        # prediction = diabetes_model.predict(input_data_diabetes_reshaped)
                        print(input_data_diabetes_reshaped)
                        prediction1 = diabetes_model.predict(input_data_diabetes_reshaped)

                        # Accuracies
                        model = diabetes_model.predict_proba(input_data_diabetes_reshaped)
                        acc = model.max()

                        if (prediction1[0] == 0):
                            result = 'The Patient does not have Diabetes'
                        else:
                            result = 'The Patient has Diabetes'
                        confidence = f"{round(acc * 100, 2)}%"
                        trust_score = calculate_trust(acc)

                        predictions = f"{result} | Confidence: {confidence} | Trust: {trust_score}"

                        recommendation = get_recommendations("Diabetes", result)

                        features = [
                        "Pregnancies","Glucose","Blood Pressure",
                        "SkinThickness","Insulin","BMI","DPF","Age"
                        ]

                        explanation = simple_explain(features, [data], result)

                        tx_hash = "Stored in Blockchain"
                        #  STORE IN BLOCKCHAIN
                        store_prediction(
                            patient_name="CSV_" + file.filename,
                            disease="Diabetes",
                            result=result,
                        )

                        if (len(error) == 0):
                            return render_template('results.html',lat=latitude,lng=longitude,type="csv",disease="db",predictions=predictions,data=data_csv.to_html(classes='mystyle', index=False),trust_score=trust_score,recommendation=recommendation,explanation=explanation,tx_hash=tx_hash)
                        else:
                            return render_template('index.html', error=error)
                        
                    elif len(data) == 8 and "age" in [col.lower() for col in data_csv.columns]:
                         input_data = pd.DataFrame([data], columns=[
                            "age","gender","smoking","sob","chest","wheezing","cough","family"
                        ])    
                         prediction = asthma_model.predict(input_data)
                         prob = asthma_model.predict_proba(input_data)
                         acc = prob.max()
                         if prediction[0] == 1:
                             result = "The Patient has Asthma"
                         else:
                             result = "The Patient does not have Asthma"
                         confidence = f"{round(acc * 100, 2)}%"
                         trust_score = calculate_trust(acc)
                         predictions = f"{result} | Confidence: {confidence} | Trust: {trust_score}"
                         recommendation = get_recommendations("Asthma", result)
                         features = ["age","gender","smoking","sob","chest","wheezing","cough","family"]
                         explanation = simple_explain(features, [data], result)
                         tx_hash = "Stored in Blockchain"
                         store_prediction(
                            patient_name="CSV_" + file.filename,
                            disease="Asthma",
                            result=result
                        )
                         return render_template(
                            'results.html',
                            lat=latitude,
                            lng=longitude,
                            type="csv",
                            disease="asthma",
                            model="asthma",
                            predictions=predictions,
                            data=data_csv.to_html(classes='mystyle', index=False),
                            trust_score=trust_score,
                            recommendation=recommendation,
                            explanation=explanation,
                            tx_hash=tx_hash
                        )
                    elif (len(data) == 13):

                        input_data_heartd_as_numpy_array = np.asarray(data)
                        # reshape the numpy array as we are predicting for only on instance
                        input_data_heartd_reshaped = input_data_heartd_as_numpy_array.reshape(1, -1)

                        prediction1 = heart_disease_model.predict(input_data_heartd_reshaped)

                        # Accuracies
                        model = heart_disease_model.predict_proba(input_data_heartd_reshaped)
                        acc = model.max()

                        if (prediction1[0] == 0):
                            result = 'The Patient does not have Heart Disease'
                        else:
                            result = 'The Patient has Heart Disease'
                        confidence = f"{round(acc * 100, 2)}%"
                        trust_score = calculate_trust(acc)
                        predictions = f"{result} | Confidence: {confidence} | Trust: {trust_score}"
                        recommendation = get_recommendations("Heart Disease", result)

                        features = [
                        "age","sex","cp","trestbps","chol","fbs",
                        "restecg","thalach","exang","oldpeak",
                        "slope","ca","thal"
                        ]

                        explanation = simple_explain(features, [data], result)

                        tx_hash = "Stored in Blockchain"
                        #  STORE IN BLOCKCHAIN
                        store_prediction(
                            patient_name="CSV_" + file.filename,
                            disease="Heart",
                            result=result,
                        )
                            
                        if len(error) == 0:
                            return render_template('results.html',lat=latitude,lng=longitude,type="csv",disease="hd",predictions=predictions,data=data_csv.to_html(classes='mystyle', index=False),trust_score=trust_score,recommendation=recommendation,explanation=explanation,tx_hash=tx_hash)
                        else:
                            return render_template('index.html', error=error)

                    elif len(data) == 22:
                        input_data_parkinsons_as_numpy_array = np.round_(data, decimals=4)
                        # reshape the numpy array
                        input_data_parkinsons_reshaped = input_data_parkinsons_as_numpy_array.reshape(1, -1)

                        prediction1 = parkinsons_model.predict(input_data_parkinsons_reshaped)

                        # Accuracies
                        model = parkinsons_model.predict_proba(input_data_parkinsons_reshaped)
                        acc = model.max()

                        if (prediction1[0] == 0):
                            result = 'The Patient does not have Parkinsons'
                        else:
                            result = 'The Patient has Parkinsons'
                        confidence = f"{round(acc * 100, 2)}%"
                        trust_score = calculate_trust(acc)
                        predictions = f"{result} | Confidence: {confidence} | Trust: {trust_score}"
                        recommendation = get_recommendations("Parkinsons", result)
                        features = [f"Feature_{i}" for i in range(1,23)]
                        explanation = simple_explain(features, [data], result)
                        tx_hash = "Stored in Blockchain"
                        store_prediction(
                            patient_name="CSV_" + file.filename,
                            disease="Parkinsons",
                            result=result
                 
)
                        if len(error) == 0:
                            return render_template('results.html',lat=latitude,lng=longitude,type="csv",disease="pk",predictions=predictions,model="pk",data=data_csv.to_html(classes='mystyle', index=False),trust_score=trust_score,recommendation=recommendation,explanation=explanation,tx_hash=tx_hash)
                        else:
                            return render_template('index.html', error=error)

                    elif len(data) == 33:
                        new_data = np.asarray(data)
                        new_data2 = new_data.reshape(1, -1)
                        probaDT = otherdiseases_model.predict_proba(new_data2)
                        probaDT.round(4)  # round probabilities to four decimal places, if applicabl
                        data = new_data2

                        # Accuracies

                        model = otherdiseases_model.predict_proba(new_data2)
                        acc = model.max()

                        pred1 = otherdiseases_model.predict(new_data2)
                        #predictions = f"{pred1[0]}" + f'{(round(acc, 3) * 100)}%'
                        result = pred1[0]
                        confidence = f"{round(acc * 100, 2)}%"
                        trust_score = calculate_trust(acc)
                        predictions = f"{result} | Confidence: {confidence} | Trust: {trust_score}"
                        recommendation = get_recommendations("Other Disease", result)
                        #features = [f"Symptom_{i}" for i in range(1,34)]
                        features = list(data_csv.columns[:-1])
                        explanation = simple_explain(features, data[0], result)
                        tx_hash = "Stored in Blockchain"

                        #  STORE IN BLOCKCHAIN
                        store_prediction(
                            patient_name="CSV_" + file.filename,
                            disease="Other Disease",
                            result=result,
                            #confidence=confidence
                            #timestamp=str(datetime.now())
                        )
                        if len(error) == 0:

                            return render_template('results.html',lat=latitude,lng=longitude,type="csv",disease="od",predictions=predictions,model="od",data=data_csv.to_html(classes='mystyle', index=False),trust_score=trust_score,recommendation=recommendation,explanation=explanation,tx_hash=tx_hash)

                        else:
                            return render_template('index.html', error=error)


                #else:
                    #class_result, prob_result = pred_model(img_path)
                    #predictions = (class_result, int(prob_result * 100))
                    #answer = predictions[0]
                else:
                    class_result, prob_result = pred_model(img_path)
                    answer = class_result
                    acc = prob_result
                    # AI Robustness + Trust Analysis (Terminal)
                    print_ai_analysis(pred_model, img_path)
                    result = answer
                    confidence = f"{round(acc*100,2)}%"
                    predictions = f"{result} | Confidence: {confidence}"

                    # ===== STORE BLOCKCHAIN =====
                    store_prediction(
                        patient_name="Image_" + file.filename,
                        disease="Pneumonia",
                        result=result,
                        #timestamp=str(datetime.now())
    )
    # ===== AI FEATURES =====
                    trust_score = calculate_trust(acc)
                    save_diagnosis("Pneumonia", result, trust_score, "Image_" + file.filename)
                    recommendation = get_recommendations("Pneumonia", result)
                    features = ["Model Confidence"]
                    explanation = simple_explain(features, [[acc]], result)
                    #explanation = simple_explain("Pneumonia", [acc])
                    tx_hash = "Stored in Blockchain"  
                    
            else:
                error = "Please upload images of jpg , jpeg and png extension only"

            if len(error) == 0:
                if ".csv" in file_name:
                    return render_template('results.html', lat=latitude, lng=longitude, type="csv",
                                           predictions=predictions,
                                           data=data_csv.to_html(classes='mystyle', header=False, index=False))
                else:
                    return render_template('results.html',lat=latitude,lng=longitude,img=file_name,answer=answer,type="img",model="pneumonia",predictions=predictions,trust_score=trust_score,recommendation=recommendation,explanation=explanation,tx_hash=tx_hash
)
                    
            else:
                return render_template('index.html', error=error)
    else:
        return render_template('index.html')


# upload function for brain_tumor
@app.route('/success_bt', methods=['GET', 'POST'])
def success_bt():
    trust_score = None
    recommendation = None
    explanation = None
    tx_hash = None
    global predictions, file_name, data, data_csv, answer
    error = ''
    target_img = os.path.join(os.getcwd(), 'static/images/')
    latitude, longitude = current_location()
    if request.method == 'POST':

        if request.files:
            file = request.files['file']

            if file and allowed_file(file.filename):

                file.save(os.path.join(target_img, file.filename))
                img_path = os.path.join(target_img, file.filename)
                file_name = file.filename

                #class_result, prob_result = pred_model_bt(img_path)
                #predictions = (class_result, int(prob_result * 100))
                #answer = predictions[0]
                # ===== STORE TO BLOCKCHAIN =====
                
                #class_result, prob_result = pred_model_bt(img_path)
                #answer = class_result
                #acc = prob_result
                #result = answer
                class_result, prob_result = pred_model_bt(img_path)  
                acc = prob_result 
                result = class_result  
                answer = result
                print_ai_analysis(pred_model_bt, img_path) #rubstness and ai trust score evalution
                confidence = f"{round(acc*100,2)}%"
                predictions = f"{result} | Confidence: {confidence}"
                store_prediction(
                    patient_name="Image_" + file.filename,
                    disease="Brain Tumor",
                    result=result
)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                blockchain_logs.append({
                    "hash": "Image_" + file.filename,
                    "patient_hash": "Image_" + file.filename,
                    "disease": "Brain Tumor",
                    "model": "CNN",
                    "time": timestamp
                })
                trust_score = calculate_trust(acc)
                save_diagnosis("Brain Tumor", result, trust_score, "Image_" + file.filename)
                recommendation = get_recommendations("Brain Tumor", result)
                features = ["Model Confidence"]
                explanation = simple_explain(features, [[acc]], result)
                #explanation = simple_explain("Brain Tumor", [acc])
                tx_hash = "Stored in Blockchain"

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

        if len(error) == 0:
            return render_template('results.html',lat=latitude,lng=longitude,img=file_name,answer=answer,type="img",model="bt",predictions=predictions,trust_score=trust_score,recommendation=recommendation,explanation=explanation,tx_hash=tx_hash
)
        else:
            return render_template('index.html', error=error)


# upload function for cataract
@app.route('/success_ct', methods=['GET', 'POST'])
def success_ct():
    trust_score = None
    recommendation = None
    explanation = None
    tx_hash = None
    global predictions, file_name, data, data_csv, answer
    error = ''
    target_img = os.path.join(os.getcwd(), 'static/images/')
    latitude, longitude = current_location()
    if request.method == 'POST':

        if request.files:
            file = request.files['file']

            if file and allowed_file(file.filename):

                file.save(os.path.join(target_img, file.filename))
                img_path = os.path.join(target_img, file.filename)
                file_name = file.filename
                class_result, prob_result = pred_model_ct(img_path)
                answer = class_result
                acc = prob_result
                print_ai_analysis(pred_model_ct, img_path) #rubstness
                result = answer
                confidence = f"{round(acc*100,2)}%"
                predictions = f"{result} | Confidence: {confidence}"

                store_prediction(
                    patient_name="Image_" + file.filename,
                    disease="Cataract",
                    result=result
)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                blockchain_logs.append({
                    "hash": "Image_" + file.filename,
                    "patient_hash": "Image_" + file.filename,
                    "disease": "Cataract",
                    "model": "CNN",
                    "time": timestamp
                })
                trust_score = calculate_trust(acc)
                save_diagnosis("Cataract", result, trust_score, "Image_" + file.filename)
                recommendation = get_recommendations("Cataract", result)
                features = ["Model Confidence"]
                explanation = simple_explain(features, [[acc]], result)
                #explanation = simple_explain("Cataract", [acc])
                tx_hash = "Stored in Blockchain"

            else:
                error = "Please upload images of jpg , jpeg and png extension only"

        if len(error) == 0:
             return render_template('results.html',lat=latitude,lng=longitude,img=file_name,answer=answer,type="img",model="ct",predictions=predictions,trust_score=trust_score,recommendation=recommendation,explanation=explanation,tx_hash=tx_hash
)
        else:
            return render_template('index.html', error=error)


# upload function for tuberculosis
@app.route('/success_tb', methods=['GET', 'POST'])
def success_tb():
    trust_score = None
    recommendation = None
    explanation = None
    tx_hash = None
    global predictions, file_name, data, data_csv, answer
    error = ''
    target_img = os.path.join(os.getcwd(), 'static/images/')
    latitude, longitude = current_location()
    if request.method == 'POST':

        if request.files:
            file = request.files['file']

            if file and allowed_file(file.filename):

                file.save(os.path.join(target_img, file.filename))
                img_path = os.path.join(target_img, file.filename)
                file_name = file.filename
                class_result, prob_result = pred_model_tb(img_path)
                answer = class_result
                acc = prob_result
                print_ai_analysis(pred_model_tb, img_path) #rubstness
                result = answer
                confidence = f"{round(acc*100,2)}%"
                predictions = f"{result} | Confidence: {confidence}"
                store_prediction(
                    patient_name="Image_" + file.filename,
                    disease="Tuberculosis",
                    result=result
)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                blockchain_logs.append({
                    "hash": "Image_" + file.filename,
                    "patient_hash": "Image_" + file.filename,
                    "disease": "Tuberculosis",
                    "model": "CNN",
                    "time": timestamp
                })
                trust_score = calculate_trust(acc)
                save_diagnosis("Tuberculosis", result, trust_score, "Image_" + file.filename)
                recommendation = get_recommendations("Tuberculosis", result)
                features = ["Model Confidence"]
                explanation = simple_explain(features, [[acc]], result)
                #explanation = simple_explain("Tuberculosis", [acc])
                tx_hash = "Stored in Blockchain"       
            else:
                error = "Please upload images of jpg , jpeg and png extension only"
        if len(error) == 0:
             return render_template('results.html',lat=latitude,lng=longitude,img=file_name,answer=answer,type="img",model="tb",predictions=predictions,trust_score=trust_score,recommendation=recommendation,explanation=explanation,tx_hash=tx_hash
)
        else:
            return render_template('index.html', error=error)
@app.route('/asthma')
def asthma():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("asthma.html")

@app.route('/asthma_form', methods=['GET', 'POST'])
@login_required
def asthma_form():

    latitude, longitude = current_location()

    if request.method == "POST":
        try:
            fullname = request.form.get("fullname")
            age = float(request.form.get("age"))
            gender = float(request.form.get("gender"))
            smoking = float(request.form.get("smoking"))
            sob = float(request.form.get("sob"))
            chest = float(request.form.get("chest"))
            wheezing = float(request.form.get("wheezing"))
            cough = float(request.form.get("cough"))
            family = float(request.form.get("family"))

            data = [age, gender, smoking, sob, chest, wheezing, cough, family]
            data_csv = pd.DataFrame([data], columns=[
                    "Age","Gender","Smoking","Shortness of Breath",
                    "Chest Tightness","Wheezing","Cough","Family History"
])

            data_np = np.asarray(data).reshape(1, -1)

            prediction = asthma_model.predict(data_np)
            prob = asthma_model.predict_proba(data_np)
            acc = prob.max()
            #print_tabular_analysis(asthma_model, data, "Asthma")
            result = "The Patient has Asthma" if prediction[0] == 1 else "The Patient does not have Asthma"
            confidence = f"{round(acc * 100, 2)}%"
            trust_score = calculate_trust(acc)

            predictions = f"{result} | Confidence: {confidence} | Trust: {trust_score}"

            patient_hash = hashlib.sha256(fullname.encode()).hexdigest()

            txid = store_prediction(
                patient_name=patient_hash,
                disease="Asthma",
                result=result
            )
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            blockchain_logs.append({
                "hash": txid,
                "patient_hash": patient_hash,
                "disease": "Asthma",
                "model": "ML Model",
                "time": timestamp
            })
            save_diagnosis("Asthma", result, trust_score, txid)
            recommendation = get_recommendations("Asthma", result)
            features = [
                "Age","Gender","Smoking","Shortness of Breath",
                "Chest Tightness","Wheezing","Cough","Family History"
                ]
            explanation = simple_explain(features, [data], result)
            return render_template(
                'results.html',
                lat=latitude,
                lng=longitude,
                disease="asthma",
                model ="asthma",
                type = "csv",
                predictions=predictions,
                data=data_csv.to_html(classes='mystyle', index=False),
                trust_score=trust_score,
                recommendation=recommendation,
                explanation=explanation,
                tx_hash="Stored in Blockchain"
            )

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("asthma_form.html")

@app.route('/heart_disease')
def heart_disease():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("heart_disease.html")
@app.route('/diabetes')
def diabetes():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("diabetes.html")
@app.route('/parkinsons')
def parkinsons():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("parkinsons.html")
@app.route('/other_diseases')
def other_diseases():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("other_diseases.html")
@app.route('/pneumonia')
def pneumonia():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("pneumonia.html")
@app.route('/brain_tumor')
def brain_tumor():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("brain_tumor.html")
@app.route('/cataract')
def cataract():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("cataract.html")
@app.route('/tuberculosis')
def tuberculosis():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("tuberculosis.html")
@app.route('/blockchain_history')
@login_required
def blockchain_history():
    if "user" not in session:
        return redirect(url_for("login"))
    records = get_all_records()
    return render_template("blockchain_history.html", records=records)
@app.route("/history")
@login_required
@role_required("admin", "doctor", "patient")
def history():
    data = get_all_records()
    return render_template(
        "history.html",
        records=data[::-1]   # latest first
    )
@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = request.form["role"]
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
            (name, email, password, role)
        )
        conn.commit()
        conn.close()
        flash("Signup successful! Please login.")
        return redirect(url_for("login"))
    return render_template("signup.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            session["user"] = user[1]     # name
            session["role"] = user[4].lower()   # ✅ VERY IMPORTANT
            print("LOGIN SUCCESS:", session["user"], session["role"])
            if session["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            elif session["role"] == "doctor":
                session["doctor_id"] = user[0]
                return redirect(url_for("doctor_dashboard"))
            elif session["role"] == "patient":
                return redirect(url_for("patient_dashboard"))
        else:
            flash("Invalid Login!")
    return render_template("login.html")
#@app.route("/logout")
#def logout():
    #session.pop("user", None)
    #session.pop("role", None)
    #return redirect(url_for("login"))
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
@app.route("/")
def home():
    latitude, longitude = current_location()
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", lat=latitude, lng=longitude)

@app.route('/patient_dashboard')
@login_required
@role_required("patient")
def patient_dashboard():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    patient_id = session.get("user_id")
    cursor.execute("""
    SELECT disease,result,trust_score,blockchain_hash
    FROM diagnosis
    WHERE patient_id=?
    """,(patient_id,))

    rows = cursor.fetchall()
    conn.close()

    records=[]

    for r in rows:
        records.append({
            "disease": r[0],
            "result": r[1],
            "trust": r[2],
            "hash": r[3]
        })

    return render_template("patient_dashboard.html",records=records)
@app.route('/doctor_dashboard')
@login_required
@role_required("doctor")
def doctor_dashboard():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT users.name, diagnosis.disease, diagnosis.result,
    diagnosis.trust_score, diagnosis.blockchain_hash
    FROM diagnosis
    JOIN users ON users.id = diagnosis.patient_id
    """)

    rows = cursor.fetchall()
    conn.close()

    records = []

    for r in rows:
        records.append({
            "patient": r[0],
            "disease": r[1],
            "result": r[2],
            "trust": r[3],
            "hash": r[4]
        })

    return render_template("doctor_dashboard.html", records=records)
@app.route("/admin_dashboard")
@login_required
@role_required("admin")
def admin_dashboard():
    logs = blockchain_logs
    return render_template(
        "admin_dashboard.html",
        blockchain_logs=logs,
        role="admin"
    )
@app.route("/system_status")
def system_status():

    status = {
        "AI Models": "Active",
        "Blockchain": "Connected",
        "Database": "Running",
        "System": "PolyDiagAI-Chain"
    }
    print("\n========== SYSTEM STATUS ==========")
    for k,v in status.items():
        print(f"{k} : {v}")
    print("===================================\n")
    return status
import threading
import webbrowser
def open_browser():
    webbrowser.open_new("http://127.0.0.1:2000/")
if __name__ == "__main__":
    system_status()
    threading.Timer(2, open_browser).start()
    app.run(debug=True, port=2000)