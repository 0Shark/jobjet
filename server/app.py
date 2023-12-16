import json
import uuid
from flask import Flask, request, jsonify
from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
from datetime import date

app = Flask(__name__)
app.config["key"] = "t_h_d"

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
LISTINGS_FILE = os.path.join(os.path.dirname(__file__), "listings.json")

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

    # Convert UUID keys to strings before updating
    for listing_id, listing_info in listings.items():
        str_listing_id = str(listing_id)
        if str_listing_id not in old_listings:
            old_listings[str_listing_id] = listing_info

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

    print(f"Received password: {password} Username: {username}")

    if username is None or password is None:
        return {"status": "error", "message": "Please provide a username and a password! Rasa may have missed your username or password. Please try again or use our 'guest' account with username 'guest' and password 'guest'."}

    if username in users:
        return {"status": "error", "message": "Username already exists"}

    users[username] = {
        "id": str(uuid.uuid4()),
        "password": password,
        "invitations": [],
        "preferences": []
    }
    save_users(users)

    return {"status": "success", "message": "User created", "user_id": users[username]["id"]}
            
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if username in users:
        if users[username]["password"] == password:
            return {
                "status": "success", 
                "message": "Login successful", 
                "user_id": users[username]["id"], 
                "username": username,
                "preferences": users[username]["preferences"],
                "invitations": users[username]["invitations"]
            } 
        else:
            return {"status": "error", "message": "Incorrect password"}
    else:
        return {"status": "error", "message": "Username does not exist"}


# Add new jobs from LinkedIn
@app.route('/add_jobs/<keyword>/<general_location>', methods=["POST"])
def add_jobs(keyword, general_location):
    # Set default values if no keyword
    if keyword is None:
        keyword = 'software engineer'

    url = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=' + keyword + '&location=' + general_location
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
            'title': keyword,
            'company': company, 
            'location': location, 
            'date_posted': date_posted,
            'link': link
            }

    save_listings(result)

    if len(result) > 0:
        return {"status": "success", "message": "Jobs added successfully! I found " + str(len(result)) + " jobs for " + keyword + " in " + general_location + "."}
    else:
        return {"status": "error", "message": "Sorry, I could not find any jobs for " + keyword + " in " + general_location + "."}

# Get jobs for a specific category
@app.route('/get_jobs/', methods=["POST"])
def get_jobs():
    data = request.get_json()
    category = data.get("job_category")
    
    print(f"Showing jobs for {category}")

    result = {}
    # Get all jobs that include the category in their title or company
    for listing_id, listing_info in listings.items():
        if category.lower() in listing_info["title"].lower() or category.lower() in listing_info["company"].lower():
            result[listing_id] = listing_info

    if len(result) > 0:
        return {"status": "success", "jobs": result}
    else:
        return {"status": "error", "message": "I could not find any jobs for that category. If you want to add jobs for that category, please login as a job poster."}

# Update user preferences
@app.route('/update_preferences/', methods=["POST"])
def preferences():
    data=request.get_json()
    username=data.get("username") 
    preferences=data.get("job_category")

    print(f"Changing preferences for {username} to {preferences}")

    if username not in users:
        result = {"status":"error", "message":"User does not exist!"}

        return jsonify(result)
    else:
        users[username]["preferences"].append(preferences)
        
    save_users(users)

    result = {"status":"success", "message":"Preferences saved successfully!"}

    return jsonify(result)

# Get candidates for a specific job category
@app.route('/get_candidates/', methods=["POST"])
def get_candidates():
    data=request.get_json()
    job_category=data.get("job_category")
    recruiter=data.get("recruiter")

    if recruiter not in users:
        return {"status":"error", "message":"Sorry, you are not a registered recruiter!"}
    else:
        candidates=[]
        for user in users:
            if job_category in users[user]["preferences"]:
                candidates.append(user)
        return {"status":"success", "candidates":candidates}

# Invite a candidate to apply for a job
@app.route('/invite_candidate/', methods=["POST"])
def invite():
    data=request.get_json()
    job_category=data.get("job_category")
    recruiter=data.get("recruiter")
    candidate_username=data.get("candidate")

    print(f"Sending invitation from {recruiter} to {candidate_username} for {job_category}")

    if candidate_username is None:
        return {"status":"error", "message":"Please provide a candidate username! Rasa may have missed your candidate name. Please try again."}

    if candidate_username not in users:
        return {"status":"error", "message": "Sorry, this user with username " + candidate_username + " does not exist!"}
    else:
        users[candidate_username]["invitations"].append({"recruiter":recruiter, "job_category":job_category})
        save_users(users)
        return {"status":"success", "message":"Invitation sent successfully to " + candidate_username + "!"}
    

if __name__ == "__main__":
    app.run(debug=True)
