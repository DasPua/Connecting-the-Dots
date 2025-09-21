from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_community.document_loaders import PyMuPDFLoader
import os

pdfs_path = os.path.abspath('./input/1706.03762v7.pdf')

def load_pdfs(pdfs_path):
    loader = PyMuPDFLoader(pdfs_path)
    return loader.load()

def splitter(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=100,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,)
    
    chunks = splitter.split_documents(documents)
    return chunks

def vectorize_chunks(chunks) :
    embeddings = OllamaEmbeddings(model = "tinyllama:1.1b")
    texts = [chunk.page_content for chunk in chunks]
    vectors = embeddings.embed_documents(texts)
    return vectors

def preprocess_documents(documents_path):
    path = os.path.abspath(documents_path)
    docs = load_pdfs(path)
    chunks = splitter(docs)
    output = vectorize_chunks(chunks)
    return (chunks,output)

    