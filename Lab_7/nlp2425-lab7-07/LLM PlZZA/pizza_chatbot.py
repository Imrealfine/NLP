from typing import Annotated

from langchain_core.exceptions import OutputParserException
from typing_extensions import TypedDict
from uuid import uuid4
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain.schema import AIMessage

llm = ChatGroq(
    temperature=0,
    groq_api_key="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",
    model_name="llama-3.3-70b-versatile"
)

class State(TypedDict):
    messages: Annotated[list, add_messages]

class PizzaOrder(BaseModel):
    size: str = Field(description="Pizza size: small, medium or large")
    flavor: str = Field(description="Pizza flavor: marguerita(with 2 euros discount), marinara or hawaiian")
    opening_hours: bool = Field(
        default=False,
        description="Whether the user asked for opening hours"
    )
    custom_toppings: list[str] = Field(
        default_factory=list,
        description="Optional list of custom toppings"
    )
    drinks: list[str] = Field(
        default_factory=list,
        description="Optional list of drinks"
    )

parser = PydanticOutputParser(pydantic_object=PizzaOrder)

# Core: Analize user intent, calculate price or return opening hours and reply.
def pizza_bot(state: State) -> dict:
    user_input = state["messages"][-1].content
    from langchain.prompts import PromptTemplate
    prompt = PromptTemplate(
        template=(
            "You are a pizzeria assistant. Parse the user's request into JSON matching "
            "the schema below:\n{format_instructions}\nUser: {query}"
        ),
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    prompt_and_model = prompt | llm
    output = prompt_and_model.invoke({"query": user_input})
    try:
        parsed: PizzaOrder = parser.invoke(output)
    except OutputParserException:
        reply = (
            "Hello, I´m a pizzeria assistant.\n"
            "You can tell me:\n"
            "– What size of pizza you want (small/medium/large)\n"
            "– Flavor (marguerita／marinara／hawaiian)\n"
            "– Additional toppings (e.g. pepperoni, mushrooms, olives, etc.)\n"
            "– Drinks (cola, sprite, juice, water)\n"
            "– Ask for Opening hours\n"
            "What can I help you with today?"
        )
        return {"messages": [AIMessage(content=reply)]}

    if parsed.opening_hours:
        reply = "We are open from 10am to 11pm every day."
        return {"messages": [AIMessage(content=reply)]}

    valid_sizes = {"small", "medium", "large"}
    if not parsed.size or parsed.size.lower() not in valid_sizes:
        reply = (
            "Sorry, I didn't understand the size of the pizza you want."
            "Please choose from small, medium, or large."
        )
        return {"messages": [AIMessage(content=reply)]}

    prices = {"small": 12, "medium": 14, "large": 18}
    base = prices[parsed.size.lower()]
    if parsed.flavor.lower() == "marguerita":
        base -= 2

    topping_price = 1.5
    num_toppings = len(parsed.custom_toppings)
    extra_toppings_cost = num_toppings * topping_price

    # drinks
    drink_prices = {
        "cola": 2.5,
        "sprite": 2.5,
        "juice": 3.0,
        "water": 1
    }
    drinks_cost = sum(drink_prices.get(drink.lower(), 0) for drink in parsed.drinks)
    total = base + extra_toppings_cost + drinks_cost
    order_id = uuid4().hex[:8]

    details = [
        f"{parsed.size} pizza {parsed.flavor}(price: {base}€)",
    ]
    if num_toppings:
        details.append(f"with extra toppings {parsed.custom_toppings}({extra_toppings_cost}€)")
    if parsed.drinks:
        details.append(f"Drinks: {parsed.drinks}({drinks_cost}€)")

    reply = (
            "Order confirmed：\n"
            + "\n".join(details)
            + f"\nTotal: {total}€，order number: {order_id}."
            + "\nThank you for your order! Bye bye!"
    )

    return {"messages": [AIMessage(content=reply)]}
