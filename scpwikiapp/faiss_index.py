import faiss
import numpy as np
# Initialize FAISS index
index = faiss.IndexFlatL2(1536)  # 1536 is the dimension of the embeddings
document_store = []

def add_documents_to_faiss(documents,embeddings):
    for doc, embedding in zip(documents,embeddings):
        document_store.append(doc)
        index.add(np.array([embedding]))