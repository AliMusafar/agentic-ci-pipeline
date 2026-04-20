from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/calculate", methods=["POST"])
def calculate():
    # Dangerous: executes user-supplied string as Python code
    expression = request.json.get("expr", "")
    result = eval(expression)
    return jsonify({"result": result})


@app.route("/health")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(debug=True)
