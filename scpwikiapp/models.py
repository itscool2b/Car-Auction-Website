from django.db import models
from django.contrib.auth.models import User
from pdfminer.high_level import extract_text
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
import os
from .faiss_index import index, document_store, add_documents_to_faiss

class ChatSession(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.session_id}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:50]}"
    

class PDFDocument(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='pdfs/')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
       
        super().save(*args, **kwargs)
        
    
        file_path = self.file.path
        text = extract_text(file_path)
        
      
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(text)
        
        
        documents = [{"page_content": chunk} for chunk in chunks]

        
        openai_api_key = os.getenv('OPENAI_API_KEY')
        embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        doc_embeddings = [embeddings.embed_query(doc["page_content"]) for doc in documents]

        
        add_documents_to_faiss(documents, doc_embeddings)