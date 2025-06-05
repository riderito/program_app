from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/data")
def get_data():
    return jsonify({"service_3": "РПП❤️"})

if __name__ == "__main__":
    app.run(port=5003)
