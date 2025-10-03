from typing import Optional, Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from tools.Utils.utils import model
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import os

questions = [
    "Do you have a preferred dentist, or would you like the first available?",
    "Would you prefer a male or female dentist, or does it not matter?",
    "Are you booking a routine dental checkup, or do you have a specific concern (like pain or sensitivity)?"
]

# ---- Strict schema (lets the parser reject off-spec outputs) ----
class PreBookingInfo(BaseModel):
    dentist_gender: Optional[Literal["male", "female", "no_problem"]] = Field(
        None, description="Gender preference; 'no_problem' means no preference."
    )
    preferred_dentist: Optional[str] = Field(
        None, description="Either a dentist name like 'Dr. Sara' or 'first_available'."
    )
    type: Optional[Literal["routine_checkup", "specific_concern"]] = Field(
        None, description="Visit type."
    )
    response: str = Field(
        description="If any field is None/ambiguous, ask ONE concise question. If all are filled, give a short confirmation."
    )

parser = PydanticOutputParser(pydantic_object=PreBookingInfo)

prompt = ChatPromptTemplate.from_messages([
    ("system",
     """You are a friendly dental intake assistant.
Your ONLY job is to collect three fields: dentist_gender, preferred_dentist, type, and to write a single follow-up question in 'response'.

Hard rules:
- Never assume answers. At the start of a conversation, ALL fields MUST be None.
- Fill a field ONLY if the user's MOST RECENT message (or explicit prior answer) clearly provides it.
- Normalizations (from user phrasing):
  - "anyone / any doctor / no preference / first available" → preferred_dentist="first_available"
  - If they also imply no gender preference ("any gender / doesn’t matter / either"), set dentist_gender="no_problem"
- 'response' MUST be a QUESTION ending with "?" unless ALL three fields are already filled from user input.
- not always the answer is explicit sometimes it is implicitly implied
- Do NOT mention scheduling, confirmations, or notifications. You are ONLY collecting info.
- Return JSON ONLY matching the schema.

Questions to use (in order when needed):
{questions}
"""),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
    ("system", "Return JSON only.\n{format_instructions}")
])



# Redis setup for session-based memory
REDIS_URL = "redis://:supersecret123@localhost:6379/0"

def get_session_history(session_id: str):
    return RedisChatMessageHistory(
        url=REDIS_URL,
        session_id=session_id,
        ttl=7*24*3600
    )

chain = prompt | model

# Wrap chain with Redis-backed message history
router_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


import asyncio

async def PreBooking_validation(session_id: str, user_msg: str) -> PreBookingInfo:
    out = await router_chain.ainvoke({
        "input": user_msg,
        "format_instructions": parser.get_format_instructions(),
        "questions": questions
    }, config={"configurable": {"session_id": session_id}})
    # Extract content if output is an AIMessage or dict with 'content'
    content = None
    if hasattr(out, 'content'):
        content = out.content
    elif isinstance(out, dict) and 'content' in out:
        content = out['content']
    else:
        content = out
    parsed = parser.parse(content)
    print(parsed)
    return parsed


if __name__ == "__main__":
    async def main():
        session_id = input("Enter session id: ")
        while True:
            q = input("You: ")
            result = await PreBooking_validation(session_id, q)
            print(result)
    asyncio.run(main())
