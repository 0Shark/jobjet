# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

class ActionRegister(Action):
    def name(self) -> Text:
        return "action_register"
    
    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        username=tracker.get_slot("username")
        password=tracker.get_slot("password")

        print(f"REGISTER NEW USER: Username: {username} Password: {password}")

        register_url="http://localhost:5000/register"
        register_data={"username":username, "password":password}
        register_response = requests.post(register_url, json=register_data).json()

        if "status" in register_response and register_response["status"] == "success":
            dispatcher.utter_message(text="User created! Your id is: " + register_response["user_id"])
        else:
            dispatcher.utter_message(text="Registration failed! " + register_response["message"])


        login_url="http://localhost:5000/login"
        login_data={"username":username, "password":password}
        login_response = requests.post(login_url, json=login_data).json()

        if "status" in login_response and login_response["status"] == "success":
            dispatcher.utter_message(text="Login successful! Welcome to the job portal " + login_response["username"] + "!")
            if len(login_response["invitations"]) > 0:
                dispatcher.utter_message(text="You have " + str(len(login_response["invitations"])) + " new invitations!")
                for invitation in login_response["invitations"]:
                    dispatcher.utter_message(text="You have been invited from " + invitation["recruiter"] + " for the job " + invitation["job_category"] + ".")
        else:
            dispatcher.utter_message(text="Login failed! Please try again. " + login_response["message"])

        return []
    

class ActionLogin(Action):
    def name(self) -> Text:
        return "action_login"
    
    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        username=tracker.get_slot("username")
        password=tracker.get_slot("password")

        print(f"LOGIN USER: Username: {username} Password: {password}")

        login_url="http://localhost:5000/login"
        login_data={"username":username, "password":password}
        login_response = requests.post(login_url, json=login_data).json()

        if "status" in login_response and login_response["status"] == "success":
            dispatcher.utter_message(text="Login successful! Welcome to the job portal " + login_response["username"] + "!")
            if len(login_response["invitations"]) > 0:
                dispatcher.utter_message(text="You have " + str(len(login_response["invitations"])) + " new invitations!")
                for invitation in login_response["invitations"]:
                    dispatcher.utter_message(text="You have been invited from " + invitation["recruiter"] + " for the job " + invitation["job_category"] + ".")
        else:
            print(login_response)
            dispatcher.utter_message(text="Login failed! Please try again. " + login_response["message"])
        
        return []
    

class ActionGetJobsForCategory(Action):
    def name(self) -> Text:
        return "action_find_jobs"
    
    def run(self, dispatcher:CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        job_category = tracker.get_slot("job_category")

        jobs_url = 'http://localhost:5000/get_jobs/'

        data = {"job_category": job_category}

        print(f"SHOWING JOBS FOR {job_category}")

        response = requests.post(jobs_url, json=data).json()

        if "status" in response and response["status"] == "success":
            dispatcher.utter_message(text="I found " + str(len(response["jobs"])) + " jobs for that category!")
            for job_id, job_info in response["jobs"].items():
                if job_info["title"]:
                    dispatcher.utter_message(text="Job title: " + job_info["title"])
                if job_info["company"]:
                    dispatcher.utter_message(text="Company: " + job_info["company"])
                if job_info["location"]:
                    dispatcher.utter_message(text="Location: " + job_info["location"])
                if job_info["date_posted"]:
                    dispatcher.utter_message(text="Date posted: " + job_info["date_posted"])
                if job_info["link"]:
                    dispatcher.utter_message(text="Link: " + job_info["link"])
                
                dispatcher.utter_message(text="-" * 10)
                    
        else:
            dispatcher.utter_message(text="Oops! Something went wrong. " + response["message"])

        return []

class ActionChangePreferences(Action):
    def name(self) -> Text:
        return "action_change_preferences"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        job_category = tracker.get_slot("job_category")
        username = tracker.get_slot("username")

        print(f"CHANGING PREFERENCES FOR {username} TO {job_category}")

        preferences_url = 'http://localhost:5000/update_preferences/'
        data = {"username": username, "job_category": job_category}

        try:
            response = requests.post(preferences_url, json=data)

            response = response.json()

            if "status" in response and response["status"] == "success":
                dispatcher.utter_message(text="Your preferences have been updated! Good luck with your job search!")
            else:
                print(response)
                dispatcher.utter_message(text="Oops! Something went wrong. " + response["message"])

        except requests.exceptions.JSONDecodeError as e:
            print(f"Error decoding JSON response: {str(e)}")
            dispatcher.utter_message(text="Oops! Something went wrong. Please try again later.")

        return []


class ActionViewCandidates(Action):
    def name(self) -> Text:
        return "action_view_candidates"
    
    def run(self, dispatcher:CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        job_category = tracker.get_slot("job_category")
        recruiter = tracker.get_slot("username")

        jobs_url = 'http://localhost:5000/get_candidates/'

        data = {"job_category": job_category, "recruiter": recruiter}

        print(f"SHOWING CANDIDATES FOR {job_category} FOR {recruiter}")

        response = requests.post(jobs_url, json=data).json()

        if "status" in response and response["status"] == "success":
            dispatcher.utter_message(text="I found " + str(len(response["candidates"])) + " candidates interested in that category!")

            for candidate in response["candidates"]:
                dispatcher.utter_message(text="Candidate: " + candidate)
            dispatcher.utter_message(text="Which candidate would you like to invite? (Please refer to the candidate by their username)")
        else:
            dispatcher.utter_message(text="Oops! Something went wrong. " + response["message"])

        return []
    

class ActionInviteCandidate(Action):
    def name(self) -> Text:
        return "action_invite_candidate"
    
    def run(self, dispatcher:CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        candidate = tracker.get_slot("candidate_username")
        recruiter = tracker.get_slot("username")
        job_category = tracker.get_slot("job_category")

        jobs_url = 'http://localhost:5000/invite_candidate/'

        data = {"job_category": job_category, "recruiter": recruiter, "candidate": candidate}

        print(f"INVITING {candidate} FOR {job_category} BY {recruiter}")

        response = requests.post(jobs_url, json=data).json()

        if "status" in response and response["status"] == "success":
            dispatcher.utter_message(text="Great! " + response["message"])
        else:
            dispatcher.utter_message(text="Oops! Something went wrong. " + response["message"])

        return []
    

class ActionAddNewJobs(Action):
    def name(self) -> Text:
        return "action_add_new_jobs"
    
    def run(self, dispatcher:CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        job_category = tracker.get_slot("job_category")

        if job_category is None:
            dispatcher.utter_message(text="Oops! Something went wrong. I couldn't find the job category you were looking for. Maybe Rasa missed it. Please try again.")
            return []
        
        jobs_url = f'http://localhost:5000/add_jobs/{job_category}/Germany'

        data = {"job_category": job_category}

        print(f"ADDING NEW JOBS FOR {job_category}")

        response = requests.post(jobs_url).json()

        if "status" in response and response["status"] == "success":
            dispatcher.utter_message(text="Great! " + response["message"])
        else:
            dispatcher.utter_message(text="Oops! Something went wrong. " + response["message"])

        return []