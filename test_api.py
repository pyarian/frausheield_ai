import requests

url = "http://127.0.0.1:5000/classify"

tests = [
    "Your Aadhaar is linked to money laundering. Do not disconnect this call.",
    "Your EMI of Rs 4500 has been debited successfully.",
    "Transfer all money to government verification account immediately or face arrest."
]

for text in tests:
    response = requests.post(url, json={"text": text})
    result = response.json()
    print(f"\nText: {text[:60]}...")
    print(f"Prediction: {result['prediction']} | Confidence: {result['confidence']}% | Risk: {result['risk_level']}")
    print("Explanation:")
    print(result["explanation"])
    print("-" * 60)