import os
import fitz
import pdfplumber
import pytesseract
from PIL import Image
from dotenv import load_dotenv

from langchain_core.documents import Document as LDocument
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma  # ✅ new import

load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")


def extract_text_from_pdf(path):
    """Extract text from PDF (pdfplumber → fallback PyMuPDF)."""
    texts = []
    try:
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                txt = p.extract_text()
                if txt:
                    texts.append(txt)
    except Exception:
        doc = fitz.open(path)
        for page in doc:
            txt = page.get_text()
            if txt:
                texts.append(txt)
    return "\n".join(texts)


def extract_text_from_image(path):
    """OCR text from image."""
    try:
        img = Image.open(path)
        return pytesseract.image_to_string(img)
    except Exception:
        return ""


def chunk_text(text, size=1000, overlap=200):
    """Chunk long text for embedding."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        start += size - overlap
    return chunks


from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def get_chroma_vstore():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vstore = Chroma(
        collection_name="documents",
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
    )
    return vstore




def index_document(document_obj, file_path):
    """Extract text and store embeddings in Chroma."""
    lower = file_path.lower()

    # Detect file type
    if lower.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif lower.endswith((".png", ".jpg", ".jpeg", ".tiff")):
        text = extract_text_from_image(file_path)
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            text = ""

    chunks = chunk_text(text)

    try:
        vstore = get_chroma_vstore()
        docs = [LDocument(page_content=c, metadata={"source": str(document_obj.id)}) for c in chunks]
        vstore.add_documents(docs)
        vstore.persist()
        print(f"✅ Indexed {len(chunks)} chunks into Chroma")
    except Exception as e:
        print(f"⚠️ Chunk/indexing error: {e}")

    return text
