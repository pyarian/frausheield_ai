from flask import Flask, request, jsonify
import pickle
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
import os
import numpy as np

load_dotenv()
client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

# Load classifier
with open('model/scam_classifier_v2.pkl', 'rb') as f:
    classifier = pickle.load(f)

# Load embedding model name and initialize
with open('model/embedding_model_name.pkl', 'rb') as f:
    model_name = pickle.load(f)

embedder = SentenceTransformer(model_name)  


def get_llm_explanation(text, prediction, confidence, risk_level):
    prompt = f"""
## ROLE
You are FraudShield AI, an expert citizen safety assistant deployed by the Ministry of Home Affairs, India. You help ordinary citizens — including elderly people with limited tech knowledge — understand whether they are being scammed, and what to do immediately.

## CONTEXT
India registered over 1.14 million cybercrime complaints in 2023. "Digital arrest" scams — where fraudsters impersonate CBI, ED, TRAI, or Customs officers and trap victims in fake video call interrogations — stole over Rs 1,776 crore in just 9 months of 2024. Your job is to protect citizens at the moment of contact, before any money is lost.

A citizen has just reported the following suspicious message or call to FraudShield AI:
"{text}"

Our detection system has analysed this and returned:
- Classification: {prediction}
- Confidence Score: {confidence}%
- Risk Level: {risk_level}

## EXAMPLES OF GOOD RESPONSES

Example 1 — SCAM detected:
"This is a classic digital arrest scam. Real CBI or ED officers never contact citizens over WhatsApp video calls, demand money transfers, or ask you to stay on camera — these are illegal tactics used by fraudsters to create panic. Hang up immediately, do not transfer any money, and report this call to the National Cyber Crime Helpline by calling 1930 or visiting cybercrime.gov.in."

Example 2 — LEGITIMATE detected:
"This message appears to be a routine bank notification with no signs of fraud. Legitimate bank alerts inform you of transactions but never ask for your OTP, PIN, or to transfer money for verification. No action is needed, but always stay cautious and never share your OTP with anyone."

## YOUR TASK
Based on the classification above, write a response with exactly these 3 parts:

1. WHAT IS HAPPENING — In 1-2 sentences, explain what type of scam this is (or why it looks legitimate). Be specific — name the tactic if it's a scam (digital arrest, fake warrant, isolation tactic, money transfer demand, etc.)

2. WHY THIS IS A RED FLAG (only if SCAM) — In 1 sentence, state one clear reason real government agencies never behave this way.

3. WHAT TO DO NOW — Give 2-3 specific action steps. If it's a scam always include: do not transfer money, hang up, and call 1930 or visit cybercrime.gov.in.

## STRICT RULES
- Write in simple, calm English that a 60-year-old can understand
- Never use words like "ML model", "classifier", "confidence score", or "algorithm"
- Never be alarmist or use ALL CAPS
- Keep total response under 120 words
- If risk level is HIGH, start with: "Warning: This is almost certainly a scam."
- If risk level is MEDIUM, start with: "Caution: This shows signs of a scam."
- If prediction is LEGITIMATE, start with: "This appears to be a legitimate message."
"""
    try:
        response = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Groq Error:", e)
        return "AI explanation is temporarily unavailable."

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400

    text = data['text']
    embedding = embedder.encode([text])
    
    prediction = classifier.predict(embedding)[0]
    label = 'SCAM' if prediction == 1 else 'LEGITIMATE'
    
    score = classifier.decision_function(embedding)[0]
    confidence = round(min(abs(score) * 40, 99), 2)
    
    risk_level = ('HIGH' if confidence > 85 and label == 'SCAM'
                  else 'MEDIUM' if label == 'SCAM'
                  else 'LOW')

    explanation = get_llm_explanation(text, label, confidence, risk_level)

    return jsonify({
        'text': text,
        'prediction': label,
        'confidence': confidence,
        'risk_level': risk_level,
        'explanation': explanation
    })

@app.route('/classify_file', methods=['POST'])
def classify_file():
    data = request.get_json()
    if not data or 'file_path' not in data:
        return jsonify({'error': 'No file path provided'}), 400

    file_path = data['file_path']
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read().strip()

    if not text:
        return jsonify({'error': 'File is empty'}), 400

    # same logic as /classify from here
    embedding = embedder.encode([text])
    prediction = classifier.predict(embedding)[0]
    label = 'SCAM' if prediction == 1 else 'LEGITIMATE'
    score = classifier.decision_function(embedding)[0]
    confidence = round(min(abs(score) * 40, 99), 2)
    risk_level = ('HIGH' if confidence > 85 and label == 'SCAM'
                  else 'MEDIUM' if label == 'SCAM'
                  else 'LOW')
    explanation = get_llm_explanation(text, label, confidence, risk_level)

    return jsonify({
        'prediction': label,
        'confidence': confidence,
        'risk_level': risk_level,
        'explanation': explanation
    })


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'running'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)