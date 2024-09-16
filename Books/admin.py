from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'author', 'published_date', 'price', 'created_at', 'updated_at')
    search_fields = ('title', 'author')
    list_filter = ('published_date',)
    ordering = ('-created_at',)
