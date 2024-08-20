from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course
from users.models import Subscription
from api.v1.serializers.course_serializer import CourseListSerializer, CreateCourseSerializer

class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """
    queryset = Course.objects.all()
    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseListSerializer  # Используем сериализатор для списка курсов
        return CreateCourseSerializer  # Используем сериализатор для создания курса

    @action(
        methods=['post'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def pay(self, request, pk=None):
        """Покупка доступа к курсу (подписка на курс)."""
        course = self.get_object()
        user = request.user
        balance = user.balance

        if balance.amount < course.price:
            return Response(
                {'detail': 'Недостаточно бонусов'},
                status=status.HTTP_400_BAD_REQUEST
            )

        @action(
            methods=['post'],
            detail=True,
            permission_classes=[permissions.IsAuthenticated]
        )
        def pay(self, request, pk=None):
            """Покупка доступа к курсу (подписка на курс)."""
            course = self.get_object()
            user = request.user
            balance = user.balance

            if balance.amount < course.price:
                return Response(
                    {'detail': 'Недостаточно бонусов'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            balance.amount -= course.price
            balance.save()

            Subscription.objects.create(
                user=user,
                course=course,
                start_date=timezone.now()
            )

            return Response(
                {'detail': 'Подписка успешно оформлена'},
                status=status.HTTP_201_CREATED
            )
        balance.amount -= course.price
        balance.save()

        Subscription.objects.create(
            user=user,
            course=course,
            start_date=timezone.now()
        )

        return Response(
            {'detail': 'Подписка успешно оформлена'},
            status=status.HTTP_201_CREATED
        )
