import json
import uuid
from flask import Flask, request, jsonify
from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os

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

    print(f"Received password: {password} Username: {username}")

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
            'title': keyword,
            'company': company, 
            'location': location, 
            'date_posted': date_posted,
            'link': link
            }

    save_listings(result)

    return jsonify(result)

# Get jobs for a specific category
@app.route('/get_jobs/', methods=["POST"])
def get_jobs():
    data = request.get_json()
    category = data.get("job_category")

    # "6d3eb207-17d5-4526-8426-07c69375217b": {
    #     "title": "Machine Learning Engineer",
    #     "company": "Skale",
    #     "location": "Munich, Bavaria, Germany",
    #     "date_posted": "2023-10-27",
    #     "link": "https://de.linkedin.com/jobs/view/machine-learning-engineer-at-skale-3744374619?refId=1GPkFn2rkECODQnK2WPeig%3D%3D&trackingId=a5AeTx%2Bfvmzv%2BJPtX9BeAw%3D%3D&position=10&pageNum=0&trk=public_jobs_jserp-result_search-card"
    # },
    # "64b70f00-5a76-4fe0-ba5c-d99afcae669f": {
    #     "title": "AI Engineer Academy - Germany",
    #     "company": "Avanade",
    #     "location": "Munich, Bavaria, Germany",
    #     "date_posted": "2023-11-19",
    #     "link": "https://de.linkedin.com/jobs/view/ai-engineer-academy-germany-at-avanade-3751250844?refId=1GPkFn2rkECODQnK2WPeig%3D%3D&trackingId=LAAGw85eBqcpI3uWE0FpRg%3D%3D&position=11&pageNum=0&trk=public_jobs_jserp-result_search-card"
    # },
    
    result = {}
    # Get all jobs that include the category in their title or company
    for listing_id, listing_info in listings.items():
        if category.lower() in listing_info["title"].lower() or category.lower() in listing_info["company"].lower():
            result[listing_id] = listing_info

    if len(result) > 0:
        return {"status": "success", "jobs": result}
    else:
        return {"status": "error", "message": "I could not find any jobs for that category. If you want to add jobs for that category, please login as a job poster."}

@app.route('/preferences', methods=["POST"])
def preferences():
    #preferences is an array of strings
    data=request.get_json()
    username=data.get("username")
    preferences=data.get("job_category")
    users[username]["preferences"].append(preferences)
    save_users(users)
    return {"status":"success", "message":"Preferences saved successfully!"}


if __name__ == "__main__":
    app.run(debug=True)
