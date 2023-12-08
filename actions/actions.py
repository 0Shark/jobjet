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

        print(f"Received password: {password} Username: {username}")

        register_url="http://localhost:5000/register"
        register_data={"username":username, "password":password}
        register_response = requests.post(register_url, json=register_data).json()

        if "status" in register_response and register_response["status"] == "success":
            dispatcher.utter_message(text="User created! Your id is: " + register_response["user_id"])
        else:
            dispatcher.utter_message(text="Registration failed" + register_response["message"])


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
            dispatcher.utter_message(text="Login failed! Please try again." + login_response["message"])

        return []
    

class ActionLogin(Action):
    def name(self) -> Text:
        return "action_login"
    
    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        username=tracker.get_slot("username")
        password=tracker.get_slot("password")

        print(f"Password: {password} Username: {username}")

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
            dispatcher.utter_message(text="Login failed! Please try again.")
        
        return []
    

class ActionGetJobsForCategory(Action):
    def name(self) -> Text:
        return "action_find_jobs"
    
    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        job_category = tracker.get_slot("job_category")

        print(f"Job category: {job_category}")

        jobs_url = 'http://localhost:5000/get_jobs/'

        data = {"job_category": job_category}

        response = requests.post(jobs_url, json=data).json()

        if "status" in response and response["status"] == "success":
            dispatcher.utter_message(text="I found " + str(len(response["jobs"])) + " jobs for that category!")
            for job_id, job_info in response["jobs"].items():
                dispatcher.utter_message(text="Job title: " + job_info["title"] + " at " + job_info["company"] + " in " + job_info["location"] + ".")
                dispatcher.utter_message(text="Date posted: " + job_info["date_posted"] + ".")
                dispatcher.utter_message(text="Link: " + job_info["link"] + ".")
        else:
            dispatcher.utter_message(text="Oops! Something went wrong." + response["message"])

        return []

class ActionChangePreferences(Action):
    def name(self) -> Text:
        return "action_change_preferences"
    
    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        job_category = tracker.get_slot("job_category")

        print(f"Job category: {job_category}")

        preferences_url = 'http://localhost:5000/change_preferences/'

        data = {"job_category": job_category}

        response = requests.post(preferences_url, json=data).json()

        if "status" in response and response["status"] == "success":
            dispatcher.utter_message(text="Your preferences have been updated! Good luck with your job search!")
        else:
            print(response)
            dispatcher.utter_message(text="Oops! Something went wrong." + response["message"])

        return []