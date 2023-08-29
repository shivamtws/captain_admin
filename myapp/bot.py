import logging,requests,json,telegram,pinecone
from time import sleep
from telegram import Update
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings as mainEmbed
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters)
import tracemalloc
from langchain.vectorstores import Pinecone
from django.conf import settings
import os,time

tracemalloc.start()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
pinecone_key = "dc0204fc-778a-4fd1-9eb6-c80cd98da213"
pinecone_env = "gcp-starter"
embeddings_model = mainEmbed(model='text-embedding-ada-002',openai_api_key="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")
index_name = "document"
pinecone.init(api_key = pinecone_key, environment = pinecone_env)
vector_store = Pinecone.from_existing_index(index_name,embeddings_model)

# file_path = os.path.join(settings.BASE_DIR, 'myapp/data/prompt.txt')
file_path = './data/prompt.txt'

with open(file_path, 'r') as file:
    context = file.read()
print("$#$"*10)
print(context)

prompt_template = context

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

chain_type_kwargs = {"prompt": PROMPT}

# query = "Do you know about DJED ?"
# res = vector_store.similarity_search(query)
# for i in res:
#     print(i.page_content)
    
def answer(vector_store,query): 
    llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.2,openai_api_key="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")
    retreiver = vector_store.as_retriever(search_type='similarity',search_kwargs={'k':3})
    # chain = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff',retriever=retreiver)
    
    chain = RetrievalQA.from_chain_type(llm=llm, 
                                 chain_type="stuff", 
                                 retriever=retreiver, 
                                 chain_type_kwargs=chain_type_kwargs)
    
    
    ans = chain.run(query)


    return ans
Bot_Token = '6117306760:AAGCOI-D6Rh_WNR9RPSNNEQuXYc7n5udy1I'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_name = user.username if user.username else ""
    print(user_name)
    await context.bot.sendChatAction(chat_id=chat_id, action="typing")
    sleep(1.5)
    # Send the conversation history back to the user
    await context.bot.send_message(chat_id=chat_id,text=f"Hello @{user_name}, Welcome to Foreon AI powered assistant, Feel free to ask me anything about Foreon network\n")


def make_post_request(url, data):
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error occurred during the request: {e}")
        return None


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text
        
    # Check if the bot's username is mentioned in the message text
    if f"@{context.bot.username}" == 'group':
        print("%%%"*30, user_message)
        
        await context.bot.sendChatAction(chat_id=chat_id, action="typing")
        sleep(2)
        
        response = answer(vector_store, user_message)

        await context.bot.send_message(chat_id=chat_id, text=response)

    # For direct messages, respond without needing to be mentioned
    elif update.message.chat.type == 'private':
        print("### Direct Message:", user_message)
        await context.bot.sendChatAction(chat_id=chat_id, action="typing")
        sleep(1.5)
        pinecone.init(api_key = pinecone_key, environment = pinecone_env)
        vector_store = Pinecone.from_existing_index(index_name,embeddings_model)
        response = answer(vector_store, user_message)

        print(response)

        await context.bot.send_message(chat_id=chat_id, text=response)


if __name__ == '__main__':
    application = ApplicationBuilder().token(Bot_Token).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(start_handler)
    application.add_handler(echo_handler)


    application.run_polling()