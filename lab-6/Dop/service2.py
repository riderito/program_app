from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/data")
def get_data():
    return jsonify({"service_2": "Я люблю"})

if __name__ == "__main__":
    app.run(port=5002)
