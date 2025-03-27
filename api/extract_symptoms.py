import requests

def extract_symptoms(user_input,GEMINI_API_URL):
    prompt = f"You are a medical expert listening to a patient's description of their condition. Extract only the precise medical symptom terms from the following text, ensuring they are written in standardized clinical terminology. Provide the symptoms as a comma-separated list, without any explanations or extra words.\n\nPatient: '{user_input}'"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            extracted_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            symptoms = [s.strip().lower() for s in extracted_text.split(",") if s]
            print(symptoms)
            return symptoms
        else:
            return []
    except Exception as e:
        return []
