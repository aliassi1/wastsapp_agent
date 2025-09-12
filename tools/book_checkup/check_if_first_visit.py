from typing import Optional, Literal, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import LLMChain
from tools.Utils.utils import model,memory

questions = [
    "Can I have your full name to add to the appointment booking?"  # full_name,
    "Is this your first visit to our clinic, or have you been here before?",  # new_patient
    "May I ask your age, please? This helps us schedule you with the right doctor.",  # age
    "Do you have any special needs we should be aware of (for example, mobility assistance, anxiety, or a request for sedation)?",  # special_needs
]

class IntakeForm(BaseModel):
    new_patient: Optional[bool] = Field(None, description="True if first visit ask if this is the first visit to this clinic")
    age: Optional[int] = None
    special_needs: Optional[List[str]] = Field(
        None, description="Leave null until explicitly asked. If user says none, set to []."
    )    
    response:str = Field(description="response to get all the needed info if some are missing")
    full_name:Optional[str]= Field(None,description='Name of the person')
    # has_insurance: Optional[bool] = None
    # insurance_provider: Optional[str] = None
    # insurance_member_id: Optional[str] = None
    # sedation_preference: Optional[bool] = None
    # mobility_assistance: Optional[bool] = None
    # What to ask next (one clear question), or empty if all slots are filled
    # next_question: Optional[str] = None

parser = PydanticOutputParser(pydantic_object=IntakeForm)


prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a friendly dental intake assistant. "
     "Goal: fill all IntakeForm fields. "
     "Ask ONE concise question at a time for missing/ambiguous info. "
     "You MUST explicitly ask about special needs before finishing. "
     "If the user has none, set special_needs to []. "
     "Return ONLY JSON with keys: new_patient, age, special_needs, response, full_name."
     '- Do NOT default special_needs to [].'
    '- Leave special_needs = null until you have explicitly asked about it.'
    '''be sure to ask all questions {questions}'''
    '''if anything is none keep asking the question until it is filled'''
    '''infer answers not always is it eplxicitly stated'''
    'if illogical answer ask question again'
    ),

    MessagesPlaceholder("history"),
    ("human", "{input}"),
    ("system", 
     "Return JSON only.\n"
     "{format_instructions}")
])


chain = LLMChain(llm=model, prompt=prompt, memory=memory)

def get_checkingin_first_step_BOOK_CHECKUP(user_msg: str) -> IntakeForm:
    out = chain.invoke({"input": user_msg, "format_instructions": parser.get_format_instructions(),'questions':questions})
    print(parser.parse(out["text"]))
    return parser.parse(out["text"])

# Example loop:
# form = converse("I want to book a checkup")
# print(form.model_dump())
# if form.next_question: ask it to the user, then call converse() again with their reply.

if __name__=='__main__':

    while(True):
        query=input()
        out = chain.invoke({"input": query, "format_instructions": parser.get_format_instructions(),'questions':questions})
        print(parser.parse(out["text"]))