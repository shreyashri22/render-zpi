import pinecone
from os import *
from dotenv import load_dotenv
load_dotenv()
pinecone.init(api_key=getenv("pinecone_api"), environment=getenv("pinecone_env"))
import langchain.vectorstores as lcv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQA
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain import OpenAI, LLMChain
import openai

openai.api_key=getenv("OPENAI_API_KEY")

index_name = 'accel-local'
index = pinecone.Index(index_name)

model_name = 'text-embedding-ada-002'
embed = OpenAIEmbeddings(model=model_name)

def Ask_bot(query,session_no):

    vectorstore = lcv.Pinecone(
        index, embed.embed_query,"text",namespace='retool-shreya'
    )

    llm = ChatOpenAI(temperature=0,model_name="gpt-3.5-turbo-16k")

    ruff = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())
            
    tools = [
    Tool(
    name="PDF System",
    func=ruff.run,
    description="Always Use this first. Useful for when you need to answer questions. Input should be a fully formed question.",
    ),]

    prefix = """Have a conversation with a human, answering the following questions accurately. Answer in steps if possible. You have access to the following tools:"""
    suffix = """Begin!"

    {chat_history}
    Question: {input}
    {agent_scratchpad}"""

    prompt = ZeroShotAgent.create_prompt(
        tools,
        prefix=prefix,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"],
    )

    message_history = RedisChatMessageHistory(
    url=getenv("redis_url"), ttl=600, session_id=session_no
    )
    # message_history.add_user_message(query)
    # message_history.clear()
    if len(message_history.messages)>10:
        message_history.clear()

    memory = ConversationBufferWindowMemory(k=10,
        memory_key="chat_history", chat_memory=message_history
    )

    llm_chain = LLMChain(llm=OpenAI(temperature=0), prompt=prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, memory=memory
    )

    res=agent_chain.run(input=query)
    # message_history.clear()
    # message_history.add_ai_message(res)
    print(message_history.messages)
    return res

# ##driver code
# session_no="xyz"
# flag=1
# while flag==1:
#     query=input("Enter question: ")
#     res=Ask_bot(query,session_no)
#     print(res)
#     print("\n")
#     flag=int(input("Enter 1 to continue and 0 to say bye: "))
