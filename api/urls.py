from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView,
    UploadDocumentView, AskQuestionView, ChatHistoryView,
    DocumentViewSet
)
from django.urls import path
from .views import delete_chat

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='documents')


urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('upload/', UploadDocumentView.as_view(), name='upload'),
    path('ask/', AskQuestionView.as_view(), name='ask'),
    path('chats/<int:document_id>/', ChatHistoryView.as_view(), name='chat_history'),
       path('chats/<int:chat_id>/delete/', delete_chat, name='delete_chat'),
    path('', include(router.urls)),  # ✅ add this to include the new /api/documents/

]
