from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import StateGraph, START, END
from pizza_chatbot import State, pizza_bot


def build_pizza_graph() -> CompiledStateGraph:
    graph = StateGraph(State)
    graph.add_node("pizza_bot", pizza_bot)
    graph.add_edge(START, "pizza_bot")
    graph.add_edge("pizza_bot", END)
    return graph.compile()


def main_loop():
    sgraph = build_pizza_graph()
    print("=== Pizza Chatbot （Input quit/exit/q to Exit） ===")
    while True:
        try:
            text = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if text.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break
        for ev in sgraph.stream({"messages": [{"role": "user", "content": text}]}, {}):
            result = next(iter(ev.values()))
            latest_msg = result["messages"][-1]
            print("Assistant:", latest_msg.content)


if __name__ == "__main__":
    main_loop()
