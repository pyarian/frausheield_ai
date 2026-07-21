import requests

response = requests.post("http://127.0.0.1:5000/analyse-call", json={
    "phone": "9627020081",
    "transcript": """Hello sir good morning this is Priya calling from HDFC Bank customer care. Sir I am calling to inform you that your credit card payment of 8500 rupees
is due on 25th July. Sir please ensure you make the payment on time to avoid
any late payment charges. You can pay through the HDFC mobile banking app
net banking or by visiting your nearest HDFC Bank branch. Sir I would also
like to inform you that we have a new zero interest EMI offer available on
your credit card for purchases above 5000 rupees at select merchants. Would
you like to know more about this offer sir? Sir please note that HDFC Bank
will never ask for your OTP PIN or CVV number over the phone. If anyone
calls you asking for these details please do not share them and report
immediately to our fraud helpline. Is there anything else I can help you
with today sir? Thank you for banking with HDFC Bank sir have a good day."""
})
print(response.json())