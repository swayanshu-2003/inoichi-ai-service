def search_diseases(input_symptoms, collection, model, top_k=2000):
    input_text = ", ".join(input_symptoms)
    query_embedding = model.encode(input_text).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k * 2,  # Fetch more for better ranking
        include=["metadatas"]
    )

    matched_diseases = {}  # Disease → Symptoms mapping
    match_counts = {}  # Count of matched symptoms per disease
    matches = {}  # Disease → {symptom: match (1 or 0)}

    if not results or "metadatas" not in results or not results["metadatas"][0]:
        return [], {}

    for metadata in results["metadatas"][0]:
        disease = metadata.get("disease", "Unknown Disease").strip()
        symptoms_str = metadata.get("symptoms", "")

        # Convert stored symptoms back to list
        disease_symptoms = [s.strip().lower() for s in symptoms_str.split(",") if s.strip()]

        # Count how many input symptoms match stored symptoms
        match_count = sum(1 for symptom in input_symptoms if symptom.lower() in disease_symptoms)

        if match_count > 0:  # Only consider diseases with at least one match
            matched_diseases[disease] = disease_symptoms
            match_counts[disease] = match_count

            matches[disease] = {
                symptom: 1 if symptom.lower() in disease_symptoms else 0
                for symptom in input_symptoms
            }

    # Sort diseases based on maximum matches (descending order)
    sorted_diseases = sorted(match_counts.keys(), key=lambda d: match_counts[d], reverse=True)

    # Limit to top_k results
    sorted_diseases = sorted_diseases[:top_k]

    # Return sorted diseases and their match details
    return sorted_diseases, {disease: matches[disease] for disease in sorted_diseases}

