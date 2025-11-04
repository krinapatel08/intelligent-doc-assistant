import os
from pathlib import Path
import pdfplumber
from pdf2image import convert_from_path
import pytesseract

from rest_framework import status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from langchain_text_splitters import RecursiveCharacterTextSplitter
from .models import Document, ChatHistory
from .serializers import (
    DocumentSerializer,
    ChatHistorySerializer,
    UserSerializer,
    RegisterSerializer,
)
from .rag_utils import get_chroma_vstore, generate_answer, index_document


# ===============================
# 🔐 AUTHENTICATION
# ===============================
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "user": UserSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=201,
            )
        return Response(serializer.errors, status=400)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            return Response({"error": "Invalid credentials"}, status=400)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


# ===============================
# 📄 UPLOAD DOCUMENT
# ===============================
class UploadDocumentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        f = request.FILES.get("file")
        if not f:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        title = request.data.get("title") or f.name
        doc = Document.objects.create(file=f, title=title, owner=request.user)
        text = ""

        try:
            text = index_document(doc, doc.file.path)
        except Exception as e:
            print("⚠️ RAG index error:", e)

        # Fallback 1️⃣: PyPDF2 extraction
        if not text:
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(doc.file.path)
                for page in reader.pages:
                    text += page.extract_text() or ""
            except Exception as e:
                print("⚠️ PDF extract error:", e)

        # Fallback 2️⃣: OCR (for scanned PDFs)
        if not text.strip():
            try:
                print("🧠 Running OCR extraction...")
                images = convert_from_path(doc.file.path)
                for image in images:
                    text += pytesseract.image_to_string(image)
            except Exception as e:
                print("⚠️ OCR extract error:", e)

        doc.text = text
        doc.save()

        serializer = DocumentSerializer(doc)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ===============================
# 📚 DOCUMENT VIEWSET
# ===============================
class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)


# ===============================
# 💬 ASK QUESTION (RAG)
# ===============================
# ===============================
# 💬 ASK QUESTION (RAG)
# ===============================
class AskQuestionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        question = request.data.get("question")
        doc_id = request.data.get("document_id")

        if not question or not doc_id:
            return Response({"error": "Missing document_id or question"}, status=400)

        try:
            document = Document.objects.get(id=doc_id, owner=request.user)
        except Document.DoesNotExist:
            return Response({"error": "Document not found or access denied"}, status=404)

        # 🧩 Prevent NoneType errors
        if not document.text:
            document.text = ""
        context = ""

        try:
            doc_vector_path = Path(f"db/doc_{document.id}")
            vstore = get_chroma_vstore(str(doc_vector_path))
            results = vstore.similarity_search(question, k=3)
            context = "\n".join([r.page_content for r in results]) if results else ""
        except Exception as e:
            print("⚠️ Vector search error:", e)
            context = (document.text or "")[:1500]

        if not context.strip():
            print("⚠️ Using fallback: document.text for context")
            context = (document.text or "")[:1500]

        if not context.strip():
            return Response(
                {"error": "Document has no readable text to answer from."},
                status=400,
            )

        prompt = f"""
You are an intelligent document assistant.
Use only the context below to answer the question.

Context:
{context}

Question:
{question}

Answer:
"""

        answer = generate_answer(prompt, context)

        ChatHistory.objects.create(document=document, question=question, answer=answer)

        return Response({"answer": answer}, status=status.HTTP_200_OK)


# ===============================
# 🕘 CHAT HISTORY
# ===============================
class ChatHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, document_id):
        chats = ChatHistory.objects.filter(
            document__id=document_id, document__owner=request.user
        ).order_by("-created_at")
        return Response(ChatHistorySerializer(chats, many=True).data)
