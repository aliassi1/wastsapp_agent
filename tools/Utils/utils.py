
from dotenv import load_dotenv
import os 
from langchain.memory import ConversationSummaryBufferMemory
from langchain_openai import ChatOpenAI


load_dotenv()
api_key_value = os.getenv('OPEN_AI_KEY')

model = ChatOpenAI(api_key=api_key_value, model="gpt-4o-mini")

ALLOWED_INTENTS = {
    "book_checkup": "book_checkup_agent",
    "tooth_pain_appointment": "tooth_pain_agent",
    "cosmetic_whitening": "whitening_agent",
    "braces_consultation": "braces_agent",
    "emergency_visit": "emergency_agent",
    "child_appointment": "child_agent",
}

memory = ConversationSummaryBufferMemory(
    llm=model,
    max_token_limit=1000,
    return_messages=True,
    input_key="input"
             # important for chat-style memory
)







# context_builder.py
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

SYSTEM_PROMPT = "You are a concise WhatsApp assistant. Keep replies short and clear."

def seed_messages(summary: str, turns: list[dict], user_text: str):
    msgs = []
    if summary:
        msgs.append(SystemMessage(content=f"Session summary:\n{summary}"))
    for t in turns:                   # turns = [{"u": "...", "a": "..."}]
        if "u" in t: msgs.append(HumanMessage(content=t["u"]))
        if "a" in t: msgs.append(AIMessage(content=t["a"]))
    msgs.append(HumanMessage(content=user_text))  # current user message
    return msgs
