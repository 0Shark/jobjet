import json
import uuid
from flask import Flask, request, jsonify
from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os

"""
curl to create someone (change student name)
curl -X POST -H "Content-Type: application/json" -d "{\"username\": \"john_doe\", \"password\": \"password123\", \"role\": \"student\"}" http://localhost:5000/register
"""


app = Flask(__name__)
app.config["key"] = "t_h_d"
USERS_FILE = os.getcwd() + "/speech-assistant/server/users.json"

#e ndryshova pak kyt se krijote file ne vedi.
LISTINGS_FILE = os.getcwd() + "/listings.json"

# Helper functions
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

def save_listings(listings):
    try:
        with open(LISTINGS_FILE, 'r') as file:
            old_listings = json.load(file)
    except FileNotFoundError:
        old_listings = {}

    # Update old_listings with the new listings
    for listing_id, listing_info in listings.items():
        if listing_id not in old_listings:
            old_listings[listing_id] = listing_info

    # Save the updated listings back to the file
    with open(LISTINGS_FILE, 'w') as file:
        json.dump(old_listings, file, indent=4)



def load_listings():
    try:
        with open(LISTINGS_FILE, "r") as file:
            try:
                listings = json.load(file)
            except Exception as e:
                listings = {}
    except FileNotFoundError:
        listings = {}
    return listings

listings = load_listings()


# Routes

# Login and register routes
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    roles = data.get("role")

    print(f"Received role: {roles}")  # Add this line for debugging

    if roles not in ["student", "job poster", "recruiter", "admin"]:
        return {"status": "error", "message": "Invalid role, please choose between student, job poster, or recruiter, or admin"}


    if username in users:
        return {"status": "error", "message": "Username already exists"}

    user_id = str(uuid.uuid4())  # Generate a random UUID for the user
    users[user_id] = {"name": username, "password": password, "roles": roles}
    save_users(users)

    return {"status": "success", "message": "User created", "user_id": user_id, "roles": roles}

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    roles=data.get("roles")

    if username in users:
        if users[user_id]["password"] == password:
            return {"status": "success", "message": "Login successful", "user_id": users[user_id]["id"], "roles": users[user_id]["roles"]}
        else:
            return {"status": "error", "message": "Incorrect password"}
    else:
        return {"status": "error", "message": "Username does not exist"}


# Job routes

# Add new jobs from LinkedIn
@app.route('/add_jobs/<keyword>/<location>')
def add_jobs(keyword, location):
    url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=' + keyword + '&location=' + location
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, 'html.parser')  
    jobs = soup.find_all('div', class_='job-search-card')

    result = {}
    for job in jobs:
        title = job.find('h3').text.strip() 
        company = job.find('h4').text.strip()
        location = job.find('span', class_='job-search-card__location').text.strip()
        date_posted = job.find('time')['datetime']
        link = job.find('a', class_='base-card__full-link')['href']
    
        result[str(uuid.uuid4())] = {
            'title': title, 
            'company': company, 
            'location': location, 
            'date_posted': date_posted,
            'link': link
            }

    save_listings(result)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
