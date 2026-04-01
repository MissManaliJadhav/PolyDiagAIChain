import pandas as pd
import random

data = []

for _ in range(1000):
    age = random.randint(5, 70)
    gender = random.randint(0, 1)  # 0 = Female, 1 = Male
    smoking = random.randint(0, 1)
    sob = random.randint(0, 1)       # Shortness of breath
    chest = random.randint(0, 1)
    wheezing = random.randint(0, 1)
    cough = random.randint(0, 1)
    family = random.randint(0, 1)

    # Smart logic for asthma (realistic pattern)
    score = sob + chest + wheezing + cough + smoking + family

    if score >= 4:
        asthma = 1
    else:
        asthma = 0

    data.append([
        age, gender, smoking, sob, chest,
        wheezing, cough, family, asthma
    ])

columns = [
    "age", "gender", "smoking", "sob", "chest",
    "wheezing", "cough", "family", "asthma"
]

df = pd.DataFrame(data, columns=columns)

df.to_csv("models/asthma.csv", index=False)

print("✅ asthma.csv with 1000 rows created successfully!")