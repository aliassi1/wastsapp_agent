from tools.conversational_agent import conversational_agent  # your LLM-based router
from tools.Utils.utils import ALLOWED_INTENTS
from tools.book_checkup.check_if_first_visit import get_checkingin_first_step_BOOK_CHECKUP
from tools.book_checkup.preBooking_validation import PreBooking_validation
from langchain_core.messages import AIMessage


def router(state: dict):
    """
    Router node: look at conversation output, decide intent.
    If not sure, return {"route": "router"} to loop again.
    """
    print('this is it', state)
    result = conversational_agent(state["input"])  # your LLM call
    intent = result.get("response")  # must return one of the ALLOWED_INTENTS or None
    
    if intent in ALLOWED_INTENTS:
        # Route to confirm_intent with the detected intent
        return {"route": intent, 
                "intent": intent, 
                "input": state["input"],
                "messages": [AIMessage(content=intent)]}
    else:
        # not confident, ask for more input
        return {"route": "wait_for_input", 
                "input": state["input"]
                ,"messages": [AIMessage(content=intent)]
}




# Node to wait for new user input
def wait_for_input(state: dict):
    # In a real app, you would collect new input from the user here.
    # For demo, just print and return the same state.
    print("Waiting for new user input. Please provide new input:")
    new_input = input()
    return {"input": new_input, "route": "router"}




# Node to confirm detected intent
def confirm_intent(state: dict):
    intent = state["intent"]
    print(f"Detected intent: {intent}. Is this what you want? (yes/no)")
    answer = input().strip().lower()
    if answer == "yes":
        return {"route": intent, "input":state["input"]}
    else:
        return {"route": "wait_for_input", "input": state["input"]}













def is_form_complete(intake_form) -> bool:
    """
    Returns True if all required fields in intake_form are not None.
    intake_form can be a dict or a Pydantic model with attributes.
    """
    required_fields = ["new_patient", "age", "special_needs",'full_name']

    for field in required_fields:
        value = getattr(intake_form, field, None) if hasattr(intake_form, field) else intake_form.get(field, None)
        if value is None :
            return True
        
    return False


# Node to confirm detected intent
def PaitentProfile_missing(state: dict):
    # In a real app, you would collect new input from the user here.
    # For demo, just print and return the same state.
    print("Now in PaitentProfilemissing")
    new_input = input()
    return {"input": new_input, "route": "book_checkup_agent"}







def EligibilityandPatientProfile(state: dict):
    """
    Router node: look at conversation output, decide intent.
    If not sure, return {"route": "router"} to loop again.
    """

    result = get_checkingin_first_step_BOOK_CHECKUP(state["input"])  # your LLM call
    loop=is_form_complete(result)

    if not loop:
        # Route to confirm_intent with the detected intent
        return {"route": "prebooking_validation", "input": state["input"]}
    else:
        # not confident, ask for more input
        return {"route": "PaitentProfile_missing", "input": state["input"]}

















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




# Node to confirm detected intent
def PaitentProfile_missing_preBooking(state: dict):
    # In a real app, you would collect new input from the user here.
    # For demo, just print and return the same state.
    print("Now in PaitentProfile_missing_preBooking")
    new_input = input()
    return {"input": new_input, "route": "prebooking_validation"}







def EligibilityandPatientProfile_preBooking(state: dict):
    """
    Router node: look at conversation output, decide intent.
    If not sure, return {"route": "router"} to loop again.
    """

    result = PreBooking_validation(state["input"])  # your LLM call
    loop=is_form_complete_PreBooking(result)

    if not loop:
        # Route to confirm_intent with the detected intent
        return {"route": "booking_calender", "input": state["input"]}
    else:
        # not confident, ask for more input
        return {"route": "PaitentProfile_missing_preBooking", "input": state["input"]}



