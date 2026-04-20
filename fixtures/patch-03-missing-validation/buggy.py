from flask import Flask, request, jsonify

app = Flask(__name__)

users = {}


@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    # No validation: missing fields will raise KeyError, no type checks
    username = data["username"]
    email = data["email"]
    age = data["age"]

    user_id = len(users) + 1
    users[user_id] = {"username": username, "email": email, "age": age}
    return jsonify({"id": user_id}), 201


@app.route("/users/<int:user_id>")
def get_user(user_id):
    # No 404 handling — will raise KeyError if user doesn't exist
    user = users[user_id]
    return jsonify(user)
