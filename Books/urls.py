from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, RegisterAPIView, LoginAPIView, index, register_page, login_page, LogoutAPIView, user_data
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register('books', BookViewSet, basename='books')

urlpatterns = [
    # API Endpoints
    path('api/register/', RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', LoginAPIView.as_view(), name='api_login'),
    path('api/', include(router.urls)),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('api/user/', user_data, name='user_data'),

    # Book CRUD Endpoints
    path('books/', views.book_list, name='book-list'),
    path('books/<int:pk>/', views.book_detail, name='book-detail'),
    path('books/new/', views.book_create, name='book-create'),
    path('books/<int:pk>/edit/', views.book_update, name='book-update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book-delete'),

    # Frontend Pages
    path('index/', index, name='index'),
    path('register/', register_page, name='register'),
    path('', login_page, name='login'),
]

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
