
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import tools_condition, ToolNode
from pydantic import BaseModel, Field
from typing import Annotated, Literal
import json
from typing_extensions import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain_core.tools import tool
from basic import GEMINI_API_KEY, GEMINI_API_KEY1
import base64
import google.genai as genai
from dotenv import load_dotenv
from google.genai import types

'''
reflection agent
'''

model = "gemini-2.5-pro"


llm = ChatGoogleGenerativeAI(
    model = model,
    google_api_key = GEMINI_API_KEY
)

class State(TypedDict):
    messages : Annotated[list, add_messages]
    loop_msg : str | None


def generation_node(state : State):

    # only takes feedback from the user only

    system_msg = SystemMessage(content = "You are a professional LinkedIn content assistant tasked with crafting engaging, insightful, and well-structured LinkedIn posts."
    " Generate the best LinkedIn post possible for the user's request."
    " If the user provides feedback or critique, respond with a refined version of your previous attempts, improving clarity, tone, or engagement as needed")

    all_msg = [system_msg] + state["messages"]

    response = llm.invoke(all_msg)
    print(response.content)

    return {"messages" : [AIMessage(content = response.content)]}

def reflection_node(state : State):
    return {"messages" : [HumanMessage(content = state["loop_msg"])]}

def check_user(state : State):

    # Human In Loop (LLM takes input from the User)
    satisfy = input("do you want to modify the response ? If Yes : give your modifications else type No")
    return {"loop_msg" : satisfy}


def should_continue(state : State):
    user_msg = state.get("loop_msg", "No")
    if state["loop_msg"] == "No":
        return "end"
    else :
        return "reflection_node"


workflow = StateGraph(State)

#nodes
workflow.add_node("generation_node", generation_node)
workflow.add_node("reflection_node", reflection_node)
workflow.add_node("check_user", check_user)

#edges
workflow.add_edge("generation_node", "check_user")
workflow.add_conditional_edges("check_user", should_continue, {"end" : END, "reflection_node" : "reflection_node"})
workflow.add_edge("reflection_node", "generation_node")

#entry
workflow.set_entry_point("generation_node")

#compile
app = workflow.compile()

#invoke the graph
response = app.invoke({"messages" : [HumanMessage(content = "Tell me about You in 50 words, include your family details as well")]})
print(response["messages"][-1].content)

