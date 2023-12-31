import pinecone
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import langchain.chat_models as lc
from langchain.chains import RetrievalQA
from langchain.chains import RetrievalQA
from langchain.agents import ZeroShotAgent, Tool, AgentExecutor
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from langchain import OpenAI, LLMChain
import openai
from dotenv import load_dotenv
import os

load_dotenv()
pinecone.init(api_key=os.getenv("pinecone_api"), environment=os.getenv("pinecone_env"))
openai.api_key=os.getenv("OPENAI_API_KEY")

index_name = 'accel-local'
index = pinecone.Index(index_name)

model_name = 'text-embedding-ada-002'
embed = OpenAIEmbeddings(model=model_name)

def Ask_bot(query,session_no):

    vectorstore = Pinecone(
        index, embed.embed_query,"text",namespace='retool-shreya'
    )

    llm = lc.ChatOpenAI(temperature=0,model_name="gpt-3.5-turbo-16k")

    ruff = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=vectorstore.as_retriever())
            
    tools = [
    Tool(
    name="PDF System",
    func=ruff.run,
    description="Always Use this first. Useful for when you need to answer questions. Input should be a fully formed question.",
    ),]

    prefix = """You are a technical conversation bot. You have access to the following tools:"""
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
    url=os.getenv("redis_url"), ttl=600, session_id=session_no
    )
    # message_history.add_user_message(query)
    # message_history.clear()
    if len(message_history.messages)>9:
        message_history.clear()

    memory = ConversationBufferWindowMemory(k=10,
        memory_key="chat_history", chat_memory=message_history
    )

    llm_chain = LLMChain(llm=OpenAI(temperature=0), prompt=prompt)
    agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=False)
    agent_chain = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=False, memory=memory
    )

    res=agent_chain.run(input=query)
    return res
