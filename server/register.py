import json
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config["key"] = "t_h_d"
USERS_FILE = "users.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}
    return users

def save_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file, indent=4)

users = load_users()

@app.route("/")
def home():
    return "Connected to the server"

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if username in users:
        return {"status": "error", "message": "Username already exists"}

    user_id = str(uuid.uuid4())  # Generate a random UUID for the user
    users[user_id] = {"name": username, "password": password}
    save_users(users)

    return {"status": "success", "message": "User created", "user_id": user_id}

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if username in users:
        if users[username]["password"] == password:
            return {"status": "success", "message": "Login successful", "user_id": users[username]["id"]}
        else:
            return {"status": "error", "message": "Incorrect password"}
    else:
        return {"status": "error", "message": "Username does not exist"}

if __name__ == "__main__":
    app.run(debug=True)
