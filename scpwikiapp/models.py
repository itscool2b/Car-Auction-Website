from django.db import models
from django.contrib.auth.models import User
from pdfminer.high_level import extract_text
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
import os
from .faiss_index import index, document_store, add_documents_to_faiss

#need to handle chat


class Chats(models.Model):
    url = models.URLField(length=200)
    text = models.TextField(max_length=255)
    

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