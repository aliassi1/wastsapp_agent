from tools.conversational_agent import conversational_agent  # your LLM-based router
from tools.Utils.utils import ALLOWED_INTENTS
from tools.book_checkup.check_if_first_visit import get_checkingin_first_step_BOOK_CHECKUP
from tools.book_checkup.preBooking_validation import PreBooking_validation
from langchain_core.messages import AIMessage


import asyncio
async def router(state: dict):
    """
    Router node: look at conversation output, decide intent.
    If not sure, return {"route": "router"} to loop again.
    """
    session_id = state.get("session_id")
    result = await conversational_agent(session_id, state["input"])  # your LLM call
    intent = result.get("response") if isinstance(result, dict) else result  # must return one of the ALLOWED_INTENTS or None
    print(intent)
    if intent in ALLOWED_INTENTS:
        return {
            "route": intent,
            "intent": intent,
            "input": state["input"],
            "session_id": session_id,
            "messages": [AIMessage(content=intent)],
            'output':intent
        }
    else:
        return {
            "route": "wait_for_input",
            "input": state["input"],
            "session_id": session_id,
            "messages": [AIMessage(content=intent)]
        }




async def wait_for_input(state: dict):
    # In a real app, you would collect new input from the user here.
    # For demo, just print and return the same state.
    print("Waiting for new user input. Please provide new input:")
    session_id = state.get("session_id")
    new_input = await asyncio.to_thread(input)
    return {"input": new_input, "route": "router", "session_id": session_id}




async def confirm_intent(state: dict):
    intent = state["intent"]
    print(f"Detected intent: {intent}. Is this what you want? (yes/no)")
    answer = await asyncio.to_thread(input).strip().lower()
    session_id = state.get("session_id")
    if answer == "yes":
        return {"route": intent, "input":state["input"], "session_id": session_id}
    else:
        return {"route": "wait_for_input", "input": state["input"], "session_id": session_id}













def is_form_complete(intake_form) -> bool:
    """
    Returns True if all required fields in intake_form are not None.
    intake_form can be a dict or a Pydantic model with attributes.
    """
    required_fields = ["new_patient"]

    for field in required_fields:
        value = getattr(intake_form, field, None) if hasattr(intake_form, field) else intake_form.get(field, None)
        if value is None :
            return True
        
    return False


async def PaitentProfile_missing(state: dict):
    # In a real app, you would collect new input from the user here.
    # For demo, just print and return the same state.
    print("Now in PaitentProfilemissing")
    session_id = state.get("session_id")
    new_input = await asyncio.to_thread(input)
    return {"input": new_input, "route": "book_checkup_agent", "session_id": session_id}







async def EligibilityandPatientProfile(state: dict):
    session_id = state.get("session_id")
    result = await get_checkingin_first_step_BOOK_CHECKUP(session_id, state["input"])
    loop = is_form_complete(result)
    if not loop:
        return {"route": "prebooking_validation", "input": state["input"], "session_id": session_id}
    else:
        return {"route": "PaitentProfile_missing", "input": state["input"], "session_id": session_id}

















def is_form_complete_PreBooking(intake_form) -> bool:
    """
    Returns True if all required fields in intake_form are not None.
    intake_form can be a dict or a Pydantic model with attributes.
    """
    required_fields = ["dentist_gender", "preferred_dentist", "type"]

    for field in required_fields:
        value = getattr(intake_form, field, None) if hasattr(intake_form, field) else intake_form.get(field, None)
        if value is None :
            return True
        
    return False




async def PaitentProfile_missing_preBooking(state: dict):
    # In a real app, you would collect new input from the user here.
    # For demo, just print and return the same state.
    print("Now in PaitentProfile_missing_preBooking")
    session_id = state.get("session_id")
    new_input = await asyncio.to_thread(input)
    return {"input": new_input, "route": "prebooking_validation", "session_id": session_id}







async def EligibilityandPatientProfile_preBooking(state: dict):
    session_id = state.get("session_id")
    result = await PreBooking_validation(session_id, state["input"])
    loop = is_form_complete_PreBooking(result)
    if not loop:
        return {"route": "booking_calender", "input": state["input"], "session_id": session_id}
    else:
        return {"route": "PaitentProfile_missing_preBooking", "input": state["input"], "session_id": session_id}



