import requests
import re



def generate_disease_explanations(matched_diseases,GEMINI_API_URL):
    if not matched_diseases:
        return []

    # Construct the markdown-enhanced doctor-style prompt
    prompt = (
        "You are a highly experienced doctor explaining diseases to a patient in a clear, informative, and engaging way. "
        "Follow the exact format below for every disease:\n\n"
        "```\n"
        "[Condition Name]\n"
        "[Brief description of the condition, including key diagnostic criteria if applicable.]\n\n"
        "Key Symptoms:\n"
        "- [Symptom 1]\n"
        "- [Symptom 2]\n"
        "- [Symptom 3]\n"
        "- ...\n\n"
        "Causes or Risk Factors:\n"
        "- [Factor 1]: [Brief explanation]\n"
        "- [Factor 2]: [Brief explanation]\n"
        "- ...\n\n"
        "Treatment Options:\n"
        "- **Lifestyle Modifications**: [Brief description of lifestyle changes]\n"
        "- **Medications**: [Types of medications used, with brief descriptions]\n"
        "- **Regular Monitoring**: [Importance of follow-ups and monitoring]\n"
        "```\n\n"
        "Ensure the response strictly follows this format for easy rendering. "
        "For each disease, the Key Symptoms section must exactly match the symptoms provided below. Do not include any additional symptoms.\n\n"
        "Now, explain the following diseases:\n\n"
    )

    for disease, symptoms in matched_diseases.items():
        symptom_list = "\n".join([f"- **{symptom}**" for symptom, matched in symptoms.items() if matched == 1])
        prompt += f"### {disease}\nA brief introduction to {disease}.\n\nKey Symptoms:\n{symptom_list}\n\nCauses or Risk Factors:\n[Expected causes/risk factors here]\n\nTreatment Options:\n[Expected treatment options here]\n\n\n"

    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        if "candidates" in data and data["candidates"]:
            extracted_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            disease_blocks = re.split(r'\n### ', extracted_text)
            result = []

            for block in disease_blocks:
                if not block.strip():
                    continue
                lines = block.split('\n')
                title = lines[0].strip()
                description_lines = []
                key_symptoms = []
                causes = {}
                treatment = {}
                current_section = None

                for line in lines[1:]:
                    line = line.strip()
                    if not line:
                        continue
                    if line == "Key Symptoms:":
                        current_section = "key_symptoms"
                    elif line == "Causes or Risk Factors:":
                        current_section = "causes"
                    elif line == "Treatment Options:":
                        current_section = "treatment"
                    else:
                        if current_section is None:
                            description_lines.append(line)
                        elif current_section == "key_symptoms":
                            if line.startswith("- "):
                                symptom = line[2:].strip()
                                key_symptoms.append(symptom)
                        elif current_section == "causes":
                            if line.startswith("- "):
                                parts = line[2:].split(": ", 1)
                                if len(parts) == 2:
                                    factor, explanation = parts
                                    causes[factor.strip()] = explanation.strip()
                        elif current_section == "treatment":
                            if line.startswith("- **"):
                                line_content = line[4:].strip()
                                subcat_end = line_content.find("**: ")
                                if subcat_end != -1:
                                    subcat = line_content[:subcat_end].strip()
                                    desc = line_content[subcat_end+3:].strip()
                                    key = subcat.lower().replace(" ", "_")
                                    treatment[key] = desc

                description = " ".join(description_lines)
                treatment_options = {
                    "lifestyle_modifications": treatment.get("lifestyle_modifications", ""),
                    "medications": treatment.get("medications", ""),
                    "regular_monitoring": treatment.get("regular_monitoring", "")
                }

                result.append({
                    "title": title,
                    "description": description,
                    "key_symptoms": key_symptoms,
                    "causes_or_risk_factors": causes,
                    "treatment_options": treatment_options
                })

            return result
        else:
            return []
    except Exception as e:
        print(f"Error generating explanations: {e}")
        return []