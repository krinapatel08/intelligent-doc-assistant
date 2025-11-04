from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader

DB_DIR = Path("db")
DB_DIR.mkdir(exist_ok=True)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_chroma_vstore(doc_path: str):
    return Chroma(persist_directory=doc_path, embedding_function=embeddings)

def index_document(doc, file_path: str):
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        text += page.extract_text() or ""

    if not text.strip():
        return ""

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)
    doc_dir = DB_DIR / f"doc_{doc.id}"
    doc_dir.mkdir(parents=True, exist_ok=True)

    Chroma.from_texts(chunks, embeddings, persist_directory=str(doc_dir))
    return text

import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()


genai.configure(api_key="YOUR_GEMINI_API_KEY")

def generate_answer(question, context):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    response = model.generate_content(prompt)
    return response.text.strip()