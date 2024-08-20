from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models import Subscription


def make_payment(request):
    """
    Реализация оплаты продукта за бонусы.
    Необходимо добавить логику для обработки запроса на оплату.
    """
    # Получаем продукт и пользователя из запроса
    product_id = request.data.get('product_id')
    if not product_id:
        return Response({'detail': 'Product ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    product = get_object_or_404(Course, id=product_id)
    user = request.user

    # Проверяем наличие подписки у пользователя
    subscription_exists = Subscription.objects.filter(user=user, course=product).exists()
    if subscription_exists:
        return Response({'detail': 'You already have a subscription to this course.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Проверяем достаточно ли бонусов у пользователя
    if user.balance < product.price:
        return Response({'detail': 'Insufficient balance.'}, status=status.HTTP_400_BAD_REQUEST)

    # Выполняем оплату
    user.balance -= product.price
    user.save()

    # Создаем подписку
    Subscription.objects.create(user=user, course=product, start_date=timezone.now())

    return Response({'detail': 'Payment successful.'}, status=status.HTTP_201_CREATED)


class IsStudentOrIsAdmin(BasePermission):
    """
    Разрешение для студентов или администраторов.
    """

    def has_permission(self, request, view):
        # Разрешить доступ администраторам
        if request.user.is_staff:
            return True

        # Разрешить доступ студентам только если они аутентифицированы
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Администраторы всегда имеют доступ к объекту
        if request.user.is_staff:
            return True

        # Студенты могут получить доступ к своим подпискам
        if isinstance(obj, Subscription):
            return obj.user == request.user

        # Разрешаем доступ студентам к объектам, если они аутентифицированы
        return request.user and request.user.is_authenticated


class ReadOnlyOrIsAdmin(BasePermission):
    """
    Разрешение для чтения или для администратора.
    """

    def has_permission(self, request, view):
        # Администраторы всегда имеют доступ
        if request.user.is_staff:
            return True

        # Разрешить доступ к просмотру для всех (GET запросы)
        return request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        # Администраторы всегда имеют доступ к объекту
        if request.user.is_staff:
            return True

        # Разрешить доступ для всех на чтение (GET запросы)
        return request.method in SAFE_METHODS
