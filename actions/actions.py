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
            dispatcher.utter_message(text="Login successful! Welcome to the job portal.")
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
            dispatcher.utter_message(text="Login successful! Welcome to the job portal.")
        else:
            dispatcher.utter_message(text="Login failed! Please try again.")

        
        return []