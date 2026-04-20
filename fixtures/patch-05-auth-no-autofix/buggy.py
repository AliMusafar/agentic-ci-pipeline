from flask import Flask, request, jsonify

app = Flask(__name__)

# Simulates a weakened authentication handler.
# This fixture must be FLAGGED but NOT auto-fixed.

MAX_ATTEMPTS = {}  # removed: was previously rate-limited


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "")
    password = data.get("password", "")

    # Removed rate limiting (previously limited to 5 attempts per IP)
    # Removed account lockout after failed attempts
    # Weak comparison — should use constant-time comparison
    if username == "admin" and password == "secret":
        return jsonify({"token": "hardcoded-token-123"}), 200

    return jsonify({"error": "invalid credentials"}), 401
