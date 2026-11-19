from rest_framework import filters, permissions, viewsets

from .models import Author, Book
from .permissions import IsOwnerOrModeratorOrReadOnly
from .serializers import AuthorSerializer, BookSerializer


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """Публічний довідник авторів: читати може будь-хто. Не змінюйте права тут."""

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.AllowAny]


class BookViewSet(viewsets.ModelViewSet):
    # select_related: author і owner підтягуються одним JOIN-ом -> немає N+1 (I1)
    queryset = Book.objects.select_related("author", "owner")
    serializer_class = BookSerializer
    permission_classes = [IsOwnerOrModeratorOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "author__name"]
    ordering_fields = ["price", "title"]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
