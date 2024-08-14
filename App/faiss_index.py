import faiss
import numpy as np

index = faiss.IndexFlatL2(1536)  
document_store = []

def add_documents_to_faiss(documents,embeddings):
    for doc, embedding in zip(documents,embeddings):
        document_store.append(doc)
        index.add(np.array([embedding]))