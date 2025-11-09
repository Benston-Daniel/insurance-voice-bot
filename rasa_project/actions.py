from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

class ActionCheckPolicyStatus(Action):
    def name(self) -> str:
        return "action_check_policy_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict):
        # This is a simple stub: in production, query your policy DB/API here.
        policy_status = "Active"
        dispatcher.utter_message(template="utter_policy_status", policy_status=policy_status)
        return []
