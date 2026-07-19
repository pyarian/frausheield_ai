import requests

response = requests.post("http://127.0.0.1:5000/classify_file", 
                        json={"file_path": "C:\\Users\\riyab\\OneDrive\\Desktop\\projects\\fraudshield-ai\\test_call.txt"})
result = response.json()
print(result)  # add this line
print(f"Prediction: {result['prediction']} | Confidence: {result['confidence']}% | Risk: {result['risk_level']}")
