import os
import uuid
from dotenv import load_dotenv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.decorators import login_required
from .models import ChatSession, ChatMessage, PDFDocument
from .forms import SignUpForm, CustomLoginForm
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.agents import Tool, initialize_agent
import openai
from .faiss_index import index, document_store

load_dotenv()



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')  # Redirect to a home page or dashboard
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')  # Redirect to a home page or dashboard
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def start_chat_session(request):
    session_id = str(uuid.uuid4())
    ChatSession.objects.create(session_id=session_id, user=request.user)
    return redirect('chat', session_id=session_id)

@login_required
def handle_chat(request, session_id):
    chat_session = get_object_or_404(ChatSession, session_id=session_id)

    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        if user_message:
            ChatMessage.objects.create(session=chat_session, sender='user', message=user_message)
            response = ragapp(user_message)
            ChatMessage.objects.create(session=chat_session, sender='bot', message=response)
            return redirect('chat', session_id=session_id)
    return render(request, 'chat.html', {'session_id': session_id, 'messages': chat_session.messages.all()})

class OpenAIChatLLM:
    def __init__(self, api_key, model="gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key

    def call(self, prompt, **kwargs):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert on the game SCP: Secret Laboratory."},
                {"role": "user", "content": prompt}
            ],
            **kwargs
        )
        return response['choices'][0]['message']['content']
    

def get_relevant_documents(query):

    openai_api_key = os.getenv('OPENAI_API_KEY')
    embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    query_embedding = embeddings.embed_query(query).reshape(1, -1)

    D, I = index.search(query_embedding, k=5)
    results = [document_store[i] for i in I[0]]
    return [result['content'] for result in results]


def ragapp(question):
    info_prompt_template = PromptTemplate.from_template("""
    You are an expert on the game SCP: Secret Laboratory. Answer the following question based on the game:

    Question: {question}
    Answer:
    """)

    openai_api_key = os.getenv('OPENAI_API_KEY')
    llm = OpenAIChatLLM(api_key=openai_api_key)
    memory = ConversationBufferMemory()
    tools = [
        Tool(
            name="InformationProvider",
            func=lambda query: get_relevant_documents(query),
            description="Use this tool to retrieve detailed information about SCP: Secret Laboratory."
        ),
    ]

    agent = initialize_agent(
        tools=tools,
        llm=llm.call,
        agent_type="zero-shot-react-description",
        memory=memory,
        handle_parsing_errors=True,
        max_iterations=50
    )

    response = agent(question)
    return response
