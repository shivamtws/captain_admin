from django.shortcuts import render,redirect
from django.conf import settings
import os,time
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings as mainEmbed
from langchain.vectorstores import Pinecone
import pinecone

# Create your views here
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
import os

pinecone_key = os.getenv("pinecone_key")
openai_api_key = os.getenv("openai_api_key")
pinecone_env = os.getenv("pinecone_env")
pinecone_key_discord = os.getenv("pinecone_key_discord")

embeddings_model = mainEmbed(model='text-embedding-ada-002',openai_api_key=openai_api_key)
index_name = "document"
def not_logged_in(user):
    return not user.is_authenticated

@login_required(login_url='login')
def index(request):
    return render(request, 'index.html')

# @user_passes_test          
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)                   
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid email or password.')
    # return redirect('login') 
    return render(request, 'login.html')

@login_required(login_url='login')  
def prompt(request):
    # file_path = 'myapp/data/prompt.txt'
    file_path = os.path.join(settings.BASE_DIR, 'myapp/data/prompt.txt')
    if request.method == 'POST':
        new_content = request.POST.get('prompt')

        with open(file_path, 'w') as file:
            file.write(new_content)
        messages.success(request, 'Prompt updated successfully.')  # Add this line
        return redirect('prompt')
    
    with open(file_path, 'r') as file:
        text_content = file.read()

    context = {
        'text_content': text_content,
    }
    return render(request, 'prompt.html', context)

@login_required(login_url='login')
def data(request):
    file_path = os.path.join(settings.BASE_DIR, 'myapp/data/mainData.txt')
    if request.method == 'POST':
        delete_index(pinecone_key)
        new_content = request.POST.get('data')
        with open(file_path, 'w') as file:
            file.write(new_content)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 256,
            chunk_overlap  = 0,
            length_function = len,
            add_start_index = True,
        )
        chunks = text_splitter.create_documents([new_content])
        create_index(index_name,chunks)


        messages.success(request, 'Data Trained successfully.')
        return redirect('data')
    
    with open(file_path, 'r') as file:
        text_content = file.read()

    context = {
        'text_content': text_content,
    }
    return render(request, 'data.html', context)

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def promptDiscord(request):
    file_path = os.path.join(settings.BASE_DIR, 'myapp/data/promptDiscord.txt')
    if request.method == 'POST':
        new_content = request.POST.get('prompt')

        with open(file_path, 'w') as file:
            file.write(new_content)
        messages.success(request, 'Prompt updated successfully.')  # Add this line
        return redirect('promptDiscord')
    
    with open(file_path, 'r') as file:
        text_content = file.read()

    context = {
        'text_content': text_content,
    }
    return render(request, 'promptDiscord.html',context)


@login_required(login_url='login')
def dataDiscord(request):
    
    file_path = os.path.join(settings.BASE_DIR, 'myapp/data/dataDiscord.txt')
    if request.method == 'POST':
        new_content = request.POST.get('data')

        with open(file_path, 'w') as file:
            file.write(new_content)

        delete_index(pinecone_key_discord)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 256,
            chunk_overlap  = 0,
            length_function = len,
            add_start_index = True,
        )
        chunks = text_splitter.create_documents([new_content])
        create_index(index_name,chunks,pinecone_key_discord)    
        messages.success(request, 'Data updated successfully.')
        return redirect('dataDiscord')
    
    with open(file_path, 'r') as file:
        text_content = file.read()

    context = {
        'text_content': text_content,
    }

    return render(request, 'dataDiscord.html',context)

def create_index(index_name,chunks,key):
    from langchain.vectorstores import Pinecone
    from langchain.embeddings.openai import OpenAIEmbeddings
    pinecone.init(api_key = key, environment=pinecone_env)

    if index_name in pinecone.list_indexes():
        # print('this is already exit')
        vector_store = Pinecone.from_existing_index(index_name,embeddings_model)
        # print("ok")
    else:
        print("create index")
        pinecone.create_index(index_name,dimension=1536, metric='cosine')
        vector_store = Pinecone.from_documents(chunks,embeddings_model,index_name=index_name)

    return vector_store


def delete_index(key,index_name = "all"):
    import pinecone
    pinecone.init(api_key = key, environment=pinecone_env)

    if index_name =="all":
        indexes = pinecone.list_indexes()
        print("Deleting All indexes...")
        for index in indexes:
            pinecone.delete_index(key,index)        
        print("delete all")    
    else:
        pinecone.delete_index(key,index_name)
        print("ok delete")