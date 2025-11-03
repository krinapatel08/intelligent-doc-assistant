import os
import fitz 
import pdfplumber
import pytesseract
from PIL import Image
from .vector_store import get_collection
from langchain_core.documents import Document as LDocument

from langchain_community.vectorstores import Chroma

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from dotenv import load_dotenv
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")  # optional
CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

def extract_text_from_pdf(path):
    texts = []
    try:
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                txt = p.extract_text()
                if txt:
                    texts.append(txt)
    except Exception:
        # fallback to PyMuPDF
        doc = fitz.open(path)
        for page in doc:
            txt = page.get_text()
            if txt:
                texts.append(txt)
    return "\n".join(texts)

def extract_text_from_image(path):
    try:
        img = Image.open(path)
        return pytesseract.image_to_string(img)
    except Exception:
        return ""

def chunk_text(text, size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        start += size - overlap
    return chunks

def get_chroma_vstore():
    # Use LangChain's Chroma wrapper with OpenAIEmbeddings if available
    if OPENAI_KEY:
        embedding = OpenAIEmbeddings()
        return Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding)
    # fallback: use plain chroma collection
    coll = get_collection()
    return coll

def index_document(document_obj, file_path):
    # detect by extension
    lower = file_path.lower()
    if lower.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif lower.endswith((".png", ".jpg", ".jpeg", ".tiff")):
        text = extract_text_from_image(file_path)
    else:
        # for txt or other: read raw text
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except:
            text = ""

    # save extracted text into document model (caller should pass model)
    chunks = chunk_text(text)
    # Add to Chroma via LangChain wrapper if available
    try:
        vstore = get_chroma_vstore()
        docs = [LDocument(page_content=c, metadata={"source": str(document_obj.id)}) for c in chunks]
        vstore.add_documents(docs)
        vstore.persist()
    except Exception as e:
        # fallback: add to collection directly
        coll = get_collection()
        ids = [f"{document_obj.id}_{i}" for i in range(len(chunks))]
        coll.add(documents=chunks, ids=ids)
    return text
