from django.db import models

class Document(models.Model):
    file = models.FileField(upload_to="documents/", null=True, blank=True)
    title = models.CharField(max_length=512, blank=True)
    text = models.TextField(blank=True)  # extracted text
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Document {self.id}"

class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chunks")
    text = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    chroma_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatHistory(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="chats", null=True, blank=True)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
