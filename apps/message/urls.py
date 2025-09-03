# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'conversations/(?P<conversation_id>[^/.]+)/messages', views.MessageViewSet, basename='message')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/users/', views.UserListView.as_view(), name='user-list'),
    path('api/unread-count/', views.UnreadMessagesCountView.as_view(), name='unread-count'),
]