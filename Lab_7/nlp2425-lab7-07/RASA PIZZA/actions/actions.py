from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import random

MENU = {
    "Margherita": {
        "prices": {"small": 12, "medium": 14, "large": 18},
        "discount": 2
    },
    "Marinara": {
        "prices": {"small": 12, "medium": 14, "large": 18},
        "discount": 0
    },
    "Hawaiian": {
        "prices": {"small": 12, "medium": 14, "large": 18},
        "discount": 0
    }
}

class ActionCalculatePrice(Action):
    def name(self) -> Text:
        return "action_calculate_price"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        # 2) get pizza type and size
        p_type = (tracker.get_slot("pizza_type") or "").title()
        p_size = (tracker.get_slot("pizza_size") or "").lower()

        # 3) find pizza price in menu and calculate total price
        if p_type in MENU and p_size in MENU[p_type]["prices"]:
            base_price = MENU[p_type]["prices"][p_size]
            discount = MENU[p_type]["discount"]
            total = base_price - discount

            dispatcher.utter_message(text=f"The total price is {total:.2f} euros.")
            return [SlotSet("price", total)]
        else:
            dispatcher.utter_message(
                text="Sorry, I couldn't find that pizza or size. "
                     "Please choose Margherita, Marinara, or Hawaiian in Small, Medium, or Large."
            )
            return []

class ActionGenerateOrderId(Action):
    def name(self) -> Text:
        return "action_generate_order_id"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        order_id = random.randint(1000, 9999)
        dispatcher.utter_message(
            text=f"Great! Your order ID is {order_id}. "
                 "Please pick it up at the shop. Enjoy!"
        )
        return []
