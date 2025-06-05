from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route("/aggregate")
def aggregate_data():
    service_2_data = requests.get("http://localhost:5002/data").json()
    service_3_data = requests.get("http://localhost:5003/data").json()

    result = {
            "Результат агрегации": {
                **service_2_data,
                **service_3_data
            }
        }
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5001)
