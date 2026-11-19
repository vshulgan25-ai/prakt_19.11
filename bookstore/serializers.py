from rest_framework import serializers

from .models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    # I1: на читання author — вкладений об'єкт, owner — ім'я користувача.
    author = AuthorSerializer(read_only=True)
    owner = serializers.SlugRelatedField(slug_field="username", read_only=True)
    # На запис клієнт передає author_id; неіснуючий id -> 400 з ключем "author_id".
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source="author", write_only=True
    )

    class Meta:
        model = Book
        fields = ["id", "title", "author", "author_id", "price", "cover", "owner"]
        read_only_fields = ["cover"]
