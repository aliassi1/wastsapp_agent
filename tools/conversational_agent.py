from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import ConversationChain
from tools.Utils.utils import memory,model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
import asyncio

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a friendly, helpful assistant.\n"
     "Do not answer questions about yourself.\n"
     "You are a dental clinic receptionist. Your job is to detect the user's intent and route them to the correct workflow.\n"
     "The output should be ONLY one of these EXACT strings when you are certain:\n"
     '["faq", "book_*", "reschedule", "cancel"]\n'
     "If unsure, ask a brief clarifying question.\n"
     "When you are sure, only respond with the intent string itself, nothing more.\n"
     "Examples:\n"
     "AI: So you want to book an appointment?\n"
     "Human: Yes\n"
     "AI: book_*\n"
     "AI: You want to cancel your appointment?\n"
     "Human: Yes\n"
     "AI: cancel\n"
     "AI: You want to reschedule?\n"
     "Human: Yes\n"
     "AI: reschedule\n"
     "AI: Are you asking a general question?\n"
     "Human: What are your opening hours?\n"
     "AI: faq\n"
    ),
    MessagesPlaceholder("history"),
    ("human", "{input}")
])

chain = prompt | model | StrOutputParser()

conversation = ConversationChain(
    llm=model,
    memory=memory,
    prompt=prompt,
    verbose=True
)
REDIS_URL = "redis://:supersecret123@localhost:6379/0"

def get_session_history(session_id: str):
    return RedisChatMessageHistory(
        url=REDIS_URL,
        session_id=session_id,  # e.g., your wa_id
        ttl=7*24*3600           # 7 days in seconds
    )


router_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",     # maps your input dict key
    history_messages_key="history", # fills MessagesPlaceholder
)




async def conversational_agent(session_id: str, user_text: str) -> str:
    raw = await router_chain.ainvoke(
        {"input": user_text},
        config={"configurable": {"session_id": session_id}}
    )
    # Enforce your allow-list strictly
    out = raw.strip().lower()
    return out 

async def main():
    results = await conversational_agent('qwe1',"my name is ali")
    print(results)
    results = await conversational_agent('qwe1',  "what is my name")
    print(results)
    results = await conversational_agent('qwe1', "i want to book an apointment to check my teeth")
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
