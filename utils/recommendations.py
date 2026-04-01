def get_recommendations(disease, result):
    disease = disease.strip().title()
    result = str(result).lower()
    #if "No" in str(result) or "Negative" in str(result):
        #return ["No major risk detected", "Maintain healthy lifestyle"]
    if "does not have" in result or "negative" in result:
        return [
            "No major risk detected",
            "Maintain healthy lifestyle",
            "Regular health check-ups recommended"
        ]
    recommendations = {

        "Diabetes":[
            "Avoid sugar foods",
            "Exercise daily",
            "Monitor glucose weekly"
        ],

        "Heart Disease":[
            "Reduce oil intake",
            "Daily walking",
            "Regular BP check",
            "Reduce cholesterol intake",
            "Regular cardio exercise",
            "Monitor blood pressure"
        ],

        "Brain Tumor":[
            "Consult neurologist",
            "MRI follow-up needed",
            "Medical supervision required"
        ],

        "Cataract":[
            "Wear UV glasses",
            "Eye specialist consultation",
            "Avoid bright light",
            "Consider surgery if severe"
        ],

        "Tuberculosis":[
            "Complete medication course",
            "Avoid close contact",
            "Start TB medication",
            "Follow doctor prescription"
        ],
        "Parkinsons":[
            "Consult neurologist",
            "Regular physiotherapy",
            "Healthy lifestyle"
        ],
        "Pneumonia":[
            "Take antibiotics",
            "Drink fluids",
            "Rest properly"
        ],
          
        "Other Disease":[
            "Consult doctor",
            "Follow medication",
            "Regular monitoring"
        ],
        
        "Asthma":[
            "Avoid dust and allergens",
            "Use inhaler regularly",
            "Avoid smoking",
            "Monitor breathing condition"
        ],
        
    }
    return recommendations.get(disease, recommendations.get("Other Disease"))
    #return recommendations.get(disease, ["Consult doctor"])