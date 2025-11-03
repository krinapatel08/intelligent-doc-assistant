import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Document, Chunk, ChatHistory
from .serializers import DocumentSerializer, ChatHistorySerializer
from .rag_pipeline import index_document, get_chroma_vstore
from .vector_store import get_collection
from .gemini_wrapper import generate_answer
from django.core.files.storage import default_storage

class UploadDocumentView(APIView):
    def post(self, request):
        f = request.FILES.get("file")
        title = request.data.get("title") or (f.name if f else "untitled")
        if not f:
            return Response({"error": "no file"}, status=status.HTTP_400_BAD_REQUEST)
        doc = Document.objects.create(file=f, title=title)
        path = doc.file.path
        # extract, index and save text
        try:
            text = index_document(doc, path)
            doc.text = text
            doc.save()
        except Exception as e:
            print("index error:", e)
        serializer = DocumentSerializer(doc)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AskQuestionView(APIView):
    def post(self, request):
        doc_id = request.data.get("document_id")
        question = request.data.get("question")
        if not question:
            return Response({"error":"no question"}, status=status.HTTP_400_BAD_REQUEST)
        doc = None
        if doc_id:
            try:
                doc = Document.objects.get(id=doc_id)
            except Document.DoesNotExist:
                doc = None

        # retrieve top chunks from Chroma
        try:
            coll = get_chroma_vstore()
            # Use LangChain Chroma object interface if present
            retriever = None
            try:
                retriever = coll.as_retriever(search_kwargs={"k":4})
                docs = retriever.get_relevant_documents(question)
                context = "\n\n".join([d.page_content for d in docs])
            except Exception:
                # fallback to chroma direct query
                col = get_collection()
                res = col.query(query_texts=[question], n_results=4)
                context = " ".join(res.get("documents", [[]])[0])
        except Exception as e:
            context = ""

        prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        answer = generate_answer(prompt)
        # save chat
        ChatHistory.objects.create(document=doc, question=question, answer=answer)
        return Response({"answer": answer})
