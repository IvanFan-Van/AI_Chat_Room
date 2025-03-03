from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    # 'messages66' will store the chatbot conversation history.
    # The 'add_messages' function ensures new messages are appended to the list.
    print('什么时候执行呢')
    messages66: Annotated[list, add_messages]

from langchain_openai import ChatOpenAI


# Set the model as ChatOpenAI
llm = ChatOpenAI(temperature=0, api_key="sk-34442cc84ebb4894b2eb884b3a6cd7f1")

def chatbot(state: State):
    # Use the LLM to generate a response based on the current conversation history.
    print('执行顺序1--- state值为：',state)
    response = llm.invoke(state["messages66"])

    # Return the updated state with the new message appended
    return {"messages66": [response]}

graph_builder = StateGraph(State)

# Add the 'chatbot' node to the graph,
graph_builder.add_node("chatbot", chatbot)

# For this basic chatbot, the 'chatbot' node is both the entry and finish point
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break

    # Process user input through the LangGraph
    for event in graph.stream({"messages66": [("user", user_input)]}):
        for value in event.values():
            print('执行顺序2---',value,'/n')
            print(value['messages66'],'/n')
            print("Assistant:", value["messages66"][-1].content,'/n')
