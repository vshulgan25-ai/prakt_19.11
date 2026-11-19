from rest_framework.permissions import SAFE_METHODS, BasePermission

MODERATORS_GROUP = "Moderators"


class IsOwnerOrModeratorOrReadOnly(BasePermission):
    """P3.

    - читання (GET/HEAD/OPTIONS) — усім;
    - створення — будь-якому автентифікованому;
    - зміна й видалення — лише власнику книги або члену групи Moderators.
    """

    def has_permission(self, request, view):
        # Рівень «усього списку»: запис дозволений тільки після входу.
        # Анонім тут отримує відмову -> DRF віддає 401 (бо є WWW-Authenticate).
        return request.method in SAFE_METHODS or bool(
            request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        # Рівень «однієї книги»: викликається з get_object() для PUT/PATCH/DELETE.
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user.is_authenticated:
            return False
        return obj.owner_id == user.id or user.groups.filter(name=MODERATORS_GROUP).exists()
