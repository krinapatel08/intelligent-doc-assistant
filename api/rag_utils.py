from pathlib import Path
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Setup database directory
DB_DIR = Path("db")
DB_DIR.mkdir(exist_ok=True)

# Load embeddings model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def get_chroma_vstore(doc_path: str):
    """Return Chroma vector store for a document"""
    return Chroma(persist_directory=doc_path, embedding_function=embeddings)


def index_document(doc, file_path: str):
    """Extract and store PDF content into Chroma vector DB"""
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


def generate_answer(question, context):
    """Generate AI response using Gemini model"""
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-lite")  # if this is available


        prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error generating answer: {str(e)}"
