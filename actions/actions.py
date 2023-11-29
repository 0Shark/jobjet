from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

class ActionRegisterLogin(Action):
    def name(self) -> Text:
        return "action_register_login"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        username = tracker.latest_message.get("text")
        password = tracker.latest_message.get("password")
        roles = tracker.latest_message.get("roles")

        register_url = "http://localhost:5000/register"
        login_url = "http://localhost:5000/login"

        # Register user
        register_data = {"username": username, "password": password, "roles": roles}
        register_response = requests.post(register_url, json=register_data).json()

        if register_response["status"] == "success":
            dispatcher.utter_message(text="User created")
        else:
            dispatcher.utter_message(text=f"Registration failed. Reason: {register_response.get('message', 'Unknown error')}")

        # Login user
        login_data = {"username": username, "password": password, "roles": roles}
        login_response = requests.post(login_url, json=login_data).json()

        if login_response["status"] == "success":
            dispatcher.utter_message(text="Login successful")
        else:
            dispatcher.utter_message(text=f"Login failed. Reason: {login_response.get('message', 'Unknown error')}")

        return []
