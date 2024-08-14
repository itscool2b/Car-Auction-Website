import os
import uuid
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from .models import PDFDocument
from .forms import SignUpForm, CustomLoginForm
from langchain_community.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool, initialize_agent
import openai
from .faiss_index import index, document_store
from openai import OpenAI

from .models import ChatSession
load_dotenv()

def loginpage(request):
    return render(request,'login.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.is_superuser = False
            user.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')  
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home/')
    else:
        form = CustomLoginForm()
    
    return render(request, 'login.html', {'form': form})

#handling chats
@login_required
def create(request):
    if request.method == 'POST':
        name = request.POST.GET('name', 'New Chat')
        chat_session = ChatSession.objects.create(user=request.user, name=name)
        return redirect('home/', session_id=chat_session.id)
    return render(request, 'dashboard.html')

@login_required
def chats(request, session_id):
    chat_session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            chat = form.save(commit=False)
            chat.session = chat_session
            chat.save()
        return redirect('home/', session_id=chat_session.id)
    else:
        form = ChatForm()
    chats = chat_session.chats.order_by('created_at')

    return render(request, 'chat_session.html', {'form': form, 'chats': chats, 'chat_session': chat_session})

def gpt4o(api_key, prompt, model='gpt-4o', **kwargs):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Think as if you are talking to a little kid. Be insightful while being aware they are kids. Instead of giving an actual roadmap, think of activities they could do in their childhood. Not exactly building paper airplanes, but activities that are common among kids and connected to what they want to be. Don’t be too childish, like playing with toys. Really focus on the foundation of STEAM."},
            {"role": "user", "content": prompt}
        ],
        **kwargs
    )
    
    message = response['choices'][0]['message']['content']
    return message
    

def get_relevant_documents(query):

    openai_api_key = os.getenv('OPENAI_API_KEY')
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    query_embedding = embeddings.embed_query(query)

    D, I = index.search(query_embedding, k=5)
    results = [document_store[i] for i in I[0]]
    return [result['page_content'] for result in results]


def ragapp(question):

    openai_api_key = os.getenv('OPENAI_API_KEY')
    memory = ConversationBufferMemory()
    tools = [
        Tool(
            name="InformationProvider",
            func=lambda query: get_relevant_documents(query),
            description="Use this tool to retrieve detailed information about STEAM foundation"
        ),
    ]


    def llmcall(prompt):
        api_key = os.getenv('OPENAI_API_KEY')
        return gpt4o(api_key=api_key, prompt=prompt)

    agent = initialize_agent(
        tools=tools,
        llm=llmcall,
        agent_type="zero-shot-react-description",
        memory=memory,
        handle_parsing_errors=True,
        max_iterations=50
    )

    response = agent(question)
    return response
