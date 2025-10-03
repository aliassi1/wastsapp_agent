from langgraph.graph import StateGraph, END
from tools.conversational_agent import conversational_agent  # your LLM-based router
from tools.Utils.utils import ALLOWED_INTENTS
from tools.Utils.llm_nodes import router,confirm_intent,wait_for_input,EligibilityandPatientProfile,PaitentProfile_missing,PaitentProfile_missing_preBooking,EligibilityandPatientProfile_preBooking
from tools.book_checkup.booking import open_booking_link


from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    session_id: str                 # your wa_id
    input: str                      # current user text (for convenience)
    route: str                      # set by router; used by conditional edges
    output: Optional[str]           # last output text (optional)
    messages: Annotated[List[AnyMessage], add_messages]  # <— MAGIC: appends across nodes


# --- Graph definition ---
graph = StateGraph(AgentState)


# Add router
graph.add_node("router", router)
graph.add_node("wait_for_input", wait_for_input)
graph.add_node("confirm_intent", confirm_intent)

graph.add_node('PaitentProfile_missing',PaitentProfile_missing)

graph.add_node('PaitentProfile_missing_preBooking',PaitentProfile_missing_preBooking)




def tooth_pain_agent(state): return {"output": "Handled by tooth_pain_agent"}
def whitening_agent(state): return {"output": "Handled by whitening_agent"}
def braces_agent(state): return {"output": "Handled by braces_agent"}
def emergency_agent(state): return {"output": "Handled by emergency_agent"}
def child_agent(state): return {"output": "Handled by child_agent"}


graph.add_node("book_checkup_agent", EligibilityandPatientProfile)
graph.add_node('prebooking_validation',EligibilityandPatientProfile_preBooking)


graph.add_node('booking_calender', open_booking_link)
graph.add_node('next_step', child_agent)

graph.add_node("faq_agent", tooth_pain_agent)
graph.add_node("whitening_agent", whitening_agent)
graph.add_node("reschedule_agent", braces_agent)
graph.add_node("cancel_agent", child_agent)


    
graph.set_entry_point("router")

# Conditional routing
graph.add_conditional_edges(
    "router",
    lambda state: state["route"],
    {**ALLOWED_INTENTS, "wait_for_input": "wait_for_input"}
)

graph.add_conditional_edges(
    "wait_for_input",
    lambda state: state["route"],
    {"router": "router"}
)


graph.add_conditional_edges(
    "book_checkup_agent",
    lambda state: state["route"],
    {"PaitentProfile_missing": "PaitentProfile_missing", "prebooking_validation": "prebooking_validation"}
)

graph.add_conditional_edges(
    "PaitentProfile_missing",
    lambda state: state["route"],
    {"book_checkup_agent": "book_checkup_agent"}
)


graph.add_conditional_edges(
    "prebooking_validation",
    lambda state: state["route"],
    {"PaitentProfile_missing_preBooking": "PaitentProfile_missing_preBooking", "booking_calender": "booking_calender"}
)

graph.add_conditional_edges(
    "PaitentProfile_missing_preBooking",
    lambda state: state["route"],
    {"prebooking_validation": "prebooking_validation"}
)
graph.add_edge('booking_calender',END)
# End all intent agents
# for node_name in ALLOWED_INTENTS.values():
#     if node_name !='book_checkup_agent':
#         graph.add_edge(node_name, END)

app = graph.compile()

import uuid

import asyncio

if __name__ == "__main__":
    # Generate a random session_id for each chat
    session_id = str(uuid.uuid4())
    print(f"Session ID: {session_id}")
    query = input()
    result = asyncio.run(app.ainvoke({"input": query, "session_id": session_id}))
