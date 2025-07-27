
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import tools_condition, ToolNode
from pydantic import BaseModel, Field
from typing import Annotated, Literal
import json
from typing_extensions import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from basic import GEMINI_API_KEY, GEMINI_API_KEY1
import base64
import google.genai as genai
from dotenv import load_dotenv
from google.genai import types

'''
AIM : user authentication
No need to use LLM here.....
just basic workflow graph
'''

model = "gemini-2.5-pro"

client = genai.Client(api_key = GEMINI_API_KEY1)

llm = ChatGoogleGenerativeAI(
    model = model,
    google_api_key = GEMINI_API_KEY
)

#================STATE==================

class AuthState(TypedDict):

    username : str | None
    password : str | None
    is_authenticated : bool | None
    output : str | bool


def input_node(state : AuthState):

    if state.get("username", "") == "":
        state["username"] = input("Enter ur username : ")

    password = input("Enter ur password : ")

    return {"password" : password}

def validation_node(state : AuthState):

    user_name = state.get("username", "")
    password = state.get("password", "")

    if user_name == "test_user" and password == "test_user":
        is_auth = True
    else :
        is_auth = False

    return {"is_authenticated" : is_auth}

def router(state : AuthState):

    if state["is_authenticated"]:
        return "success_node"
    else:
        return "failure_node"

def success_node(state : AuthState):
    return {"output" : "User authenticated successfully"}

def failure_node(state : AuthState):
    return {"output" : "User Auth Failed"}


workflow = StateGraph(AuthState)

#Nodes
workflow.add_node("input_node", input_node)
workflow.add_node("validation_node", validation_node)
workflow.add_node("success_node", success_node)
workflow.add_node("failure_node", failure_node)

#EDGES
workflow.add_edge("input_node", "validation_node")
workflow.add_conditional_edges("validation_node", router, {"success_node" : "success_node", "failure_node" : "failure_node" })
#workflow.add_edge("sucess_node", END)  END node is added automatically
workflow.add_edge("failure_node", "input_node")

#Entry point
workflow.set_entry_point("input_node")

#compile
app = workflow.compile()

#invoke the graph
inputs = {"user_name" : "test_user"}
result = app.invoke(inputs)
print(result)


print(result["output"])


# auth_state_1: AuthState = {
#     "username": "alice123",
#     "password": "123",
#     "is_authenticated": True,
#     "output": "Login successful."
# }
#
# auth_state_2: AuthState = {
#     "username":"",
#     "password": "wrongpassword",
#     "is_authenticated": False,
#     "output": "Authentication failed. Please try again."
# }
#
# print(input_node(auth_state_2))
