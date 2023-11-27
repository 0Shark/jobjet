# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

class ActionRegisterLogin(Action):
    def name(self) -> Text:
        return "action_register_login"
    
    def run(self, dispatcher:CollectingDispatcher, tracker:Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        username=tracker.get_slot("username")
        password=tracker.get_slot("password")
        roles=tracker.get_slot("roles")

        register_url="http://localhost:5000/register"
        login_url="http://localhost:5000/login"
        register_data={"username":username, "password":password, "roles":roles}
        register_response= requests.post(register_url, json=register_data).json()


        if register_response.status_code==201:
            dispatcher.utter_message(text="User created")
        else:
            dispatcher.utter_message(text="Registration failed")

        login_url="http://localhost:5000/login"
        login_data={"username":username, "password":password, "roles":roles}
        login_response= requests.post(login_url, json=login_data).json()

        if login_response.status_code==200:
            dispatcher.utter_message(text="Login successful")
        else:
            dispatcher.utter_message(text="Login failed")
        
        return []