from langgraph.graph import StateGraph, MessagesState
from langgraph.constants import START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

    
from dotenv import load_dotenv
import os

# ---------------- Load env ----------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

checkpoint = InMemorySaver()
store = InMemoryStore()

# ---------------- Models ----------------
gemini_model = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash", api_key=GEMINI_API_KEY
)
ollama_model = ChatOllama(model="gemma3n", disable_streaming=False)

# fallback: if Gemini fails, use Ollama
model = gemini_model.with_fallbacks([ollama_model])

def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    state["messages"].append(response)
    return state

def create_state_graph():
    """
    Creates and returns a state graph with predefined nodes, edges, and memory checkpointing.

    Returns:
        StateGraph: A compiled state graph with nodes and edges set up.
    """

    workflow = (
        StateGraph(MessagesState)
        .add_node("call_model", call_model)
        .add_edge(START, "call_model")
        .add_edge("call_model", END)
        .compile(checkpointer=checkpoint, store=store)
    )

    return workflow

# Create the state graph
resume_agent = create_state_graph()