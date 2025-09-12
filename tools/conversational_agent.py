from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import ConversationChain
from tools.Utils.utils import memory,model

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a friendly, helpful assistant. 
     Do not answer questions about yourself. 
     Your job is to detect the user's goal and route them to the appropriate workflow.\n\nConverse naturally, but only return an intent when you are certain.
      The output must be exactly one of:\n[\n\"book_checkup\",\n\"tooth_pain_appointment\",\n\"cosmetic_whitening\",\n\"braces_consultation\",\n\"emergency_visit\",\n\"child_appointment\"\n]\n\nWhen you are sure of the user's intent, respond with only the intent word (e.g., book_checkup) and nothing else.\n"""),
    MessagesPlaceholder("history"),   # <-- make sure memory works
    ("human", "{input}")
])


conversation = ConversationChain(
    llm=model,
    memory=memory,
    prompt=prompt,
    verbose=True
)


def conversational_agent(query:str):
        results = conversation.invoke({"input":query})
        print(results)
        return results


if __name__ == '__main__':
    
    results = conversation.invoke({"input": "what is your job"})
    results = conversation.invoke({"input": "my name is ali"})
    results = conversation.invoke({"input": "what is my name"})
    results = conversation.invoke({"input": "i want to book an apointment to check my teeth"})
    print(results["response"])  # <-- use correct key depending on version
