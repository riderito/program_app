import requests

response = requests.post(
    'http://localhost:5001/number/',
    json={'jsonParam': 5},
    headers={'Content-Type': 'application/json'}
)
print("POST Response:")
print(response.json())