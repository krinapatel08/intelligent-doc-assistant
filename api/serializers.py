from rest_framework import serializers
from .models import Document, Chunk, ChatHistory

class ChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chunk
        fields = "__all__"

class DocumentSerializer(serializers.ModelSerializer):
    chunks = ChunkSerializer(many=True, read_only=True)
    class Meta:
        model = Document
        fields = ["id", "title", "file", "text", "created_at", "chunks"]

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = "__all__"
