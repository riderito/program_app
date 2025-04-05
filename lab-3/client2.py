import requests

response = requests.get('http://localhost:5001/number/?param=5')
print("GET Response:")
print(response.json())