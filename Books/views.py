from django.contrib.auth.models import User
from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .tokens import get_tokens_for_user
from .models import Book
from .serializers import BookSerializer, UserSerializer
from .permissions import IsBookOwner
from django.shortcuts import render, get_object_or_404, redirect
from .forms import BookForm, CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.core.exceptions import PermissionDenied




class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsBookOwner]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Book.objects.all()
        return Book.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "message": "Books retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "message": "Book created successfully.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            book = self.get_object()
            serializer = self.get_serializer(book)
            return Response({
                "message": "Book retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({
                "error": "Book not found."
            }, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, *args, **kwargs):
        try:
            book = self.get_object()
            serializer = self.get_serializer(book, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Book updated successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({
                "error": "Book not found."
            }, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None, *args, **kwargs):
        try:
            book = self.get_object()
            serializer = self.get_serializer(book, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Book updated partially successfully.",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({
                "error": "Book not found."
            }, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            book = self.get_object()
            book.delete()
            return Response({
                "message": "Book deleted successfully."
            }, status=status.HTTP_204_NO_CONTENT)
        except Book.DoesNotExist:
            return Response({
                "error": "Book not found."
            }, status=status.HTTP_404_NOT_FOUND)


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({
                'user_details': serializer.data,
                'token': token
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({"msg": "Username and Password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)

        if user:
            token = get_tokens_for_user(user)
            return Response({
                'token': token,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_data(request):
    return Response({'username': request.user.username})


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Refresh token not provided.'}, status=400)
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({'detail': str(e)}, status=400)
        
        return Response({'detail': 'Successfully logged out.'})



####### TEMPLATE ########




@login_required
def book_list(request):
    if request.user.is_superuser:
        books = Book.objects.all()
    else:
        books = Book.objects.filter(user=request.user)
    return render(request, 'book_list.html', {'books': books})

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not request.user.is_superuser and book.user != request.user:
        raise PermissionDenied("You do not have permission to view this book.")
    return render(request, 'book_detail.html', {'book': book})

@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)
            book.user = request.user
            book.save()
            return redirect('book-list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})

@login_required
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not request.user.is_superuser and book.user != request.user:
        raise PermissionDenied("You do not have permission to edit this book.")
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book-list')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form})

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if not request.user.is_superuser and book.user != request.user:
        raise PermissionDenied("You do not have permission to delete this book.")
    if request.method == 'POST':
        book.delete()
        return redirect('book-list')
    return render(request, 'book_confirm_delete.html', {'book': book})


def register_page(request):
    return render(request, 'register.html')

def login_page(request):
    return render(request, 'login.html')

def index(request):
    return render(request, 'index.html')



