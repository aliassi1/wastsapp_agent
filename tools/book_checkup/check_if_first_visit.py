from typing import Optional, Literal, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from tools.Utils.utils import model
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import os

questions = [
    "Is this your first visit to our clinic, or have you been here before?"  # new_patient
]

class IntakeForm(BaseModel):
    new_patient: Optional[bool] = Field(None, description="True if first visit, ask if this is the first visit to this clinic")
    response: str = Field(description="response to get the needed info if missing")

parser = PydanticOutputParser(pydantic_object=IntakeForm)


prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a friendly dental intake assistant.\n"
     "Goal: Determine if this is the user's first visit to the clinic.\n"
     "Ask ONE concise question if the answer is missing or ambiguous.\n"
     "Return ONLY JSON with keys: new_patient, response.\n"
     "If unsure, ask: 'Is this your first visit to our clinic, or have you been here before?'\n"
     "If the answer is illogical, ask again.\n"
    ),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
    ("system", 
     "Return JSON only.\n"
     "{format_instructions}")
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

async def get_checkingin_first_step_BOOK_CHECKUP(session_id: str, user_msg: str) -> IntakeForm:
    out = await router_chain.ainvoke(
        {"input": user_msg, "format_instructions": parser.get_format_instructions(), 'questions': questions},
        config={"configurable": {"session_id": session_id}}
    )
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

# Example loop:
# form = converse("I want to book a checkup")
# print(form.model_dump())
# if form.next_question: ask it to the user, then call converse() again with their reply.


if __name__=='__main__':
    async def main():
        session_id = input("Enter session id: ")
        while True:
            query = input("You: ")
            result = await check_if_first_visit(session_id, query)
            print(result)
    asyncio.run(main())