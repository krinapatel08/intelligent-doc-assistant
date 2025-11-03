from django.urls import path
from .views import UploadDocumentView, AskQuestionView


urlpatterns = [
    path("upload/", UploadDocumentView.as_view(), name="upload"),
    path("ask/", AskQuestionView.as_view(), name="ask"),
]
