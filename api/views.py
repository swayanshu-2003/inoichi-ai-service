

import os
import requests
import chromadb
from sentence_transformers import SentenceTransformer
from rest_framework.response import Response
from rest_framework.views import APIView
from .generate_description import generate_disease_explanations
from .search_diseases import search_diseases

# Set Gemini API Key
GENAI_API_KEY = "AIzaSyC6HMDAetPkZufKOXybz7O_Je18t3F3guA"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GENAI_API_KEY}"

# Load ChromaDB client
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_collection(name="disease_symptom_db")

# Load Sentence Transformer Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Function to Extract Symptoms from Input Text using Gemini Free API
def extract_symptoms(user_input):
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


# Django API View
class ExtractSymptomsView(APIView):
    def post(self, request):
        user_input = request.data.get("input", "")
        if not user_input:
            return Response({"error": "No input provided"}, status=400)

        # Extract Symptoms from Input
        symptoms = extract_symptoms(user_input,GEMINI_API_URL)
        if not symptoms:
            return Response({"error": "No symptoms detected"}, status=400)

        # Search Diseases in Vector DB
        diseases, matches = search_diseases(symptoms,collection,model)
        
        # generate disease descriptions
        descriptions = generate_disease_explanations(dict(list(matches.items())[:3]), GEMINI_API_URL)
        print(descriptions)
       
        output = {
            "input":user_input,
            "extracted_symptoms": symptoms,
            "matching_diseases": diseases,
            "matches": matches,
            "descriptions": descriptions
        }

        return Response(output)

