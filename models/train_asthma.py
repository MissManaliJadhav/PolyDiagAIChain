import pandas as pd
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset (FIXED PATH)
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, "asthma.csv")

    df = pd.read_csv(file_path)
    print("Using real dataset...")
except Exception as e:
    print("Dataset not found, using sample data...")
    print("Error:", e)

    data = {
        'cough': [1,0,1,0,1,1,0,0,1,0],
        'wheezing': [1,0,1,0,1,1,0,0,1,0],
        'shortness_of_breath': [1,0,1,0,1,1,0,0,1,0],
        'chest_tightness': [1,0,1,0,1,1,0,0,1,0],
        'age': [25,30,45,50,35,40,28,33,60,22],
        'asthma': [1,0,1,0,1,1,0,0,1,0]
    }
    df = pd.DataFrame(data)

# Clean data
df = df.dropna()

print("Columns:", df.columns)

# ===============================
# 🔥 HANDLE DATASET DIFFERENCE
# ===============================

if 'asthma' not in df.columns:
    print("⚠️ 'asthma' column not found. Creating from Severity...")

    if 'Severity_Mild' in df.columns:
        # Create target column
        df['asthma'] = df[['Severity_Mild', 'Severity_Moderate']].max(axis=1)

        # Drop unwanted columns
        df = df.drop(['Severity_Mild', 'Severity_Moderate', 'Severity_None'], axis=1)
    else:
        raise Exception("❌ No valid target column found in dataset!")

# ===============================
# FEATURES & TARGET
# ===============================
X = df.drop('asthma', axis=1)
y = df['asthma']

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

# Ensure models folder exists
os.makedirs('models', exist_ok=True)

# Save model
pickle.dump(model, open('models/asthma_model.sav', 'wb'))

# Save accuracy
with open('models/asthma_accuracy.txt', 'w') as f:
    f.write(str(round(accuracy * 100, 2)))

print(f"✅ Model trained successfully! Accuracy: {round(accuracy * 100, 2)}%")