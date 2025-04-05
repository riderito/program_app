import requests

response = requests.delete('http://localhost:5001/number/')
print("DELETE Response:")
print(response.json())