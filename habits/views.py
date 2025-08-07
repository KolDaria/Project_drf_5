from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import exceptions, generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from habits.models import Habit
from habits.pagination import HabitListPagination
from habits.serializers import HabitSerializer


class HabitCreateAPIView(generics.CreateAPIView):
    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class HabitListAPIView(generics.ListAPIView):
    serializer_class = HabitSerializer
    pagination_class = HabitListPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['action', 'place']
    ordering_fields = ['time', 'periodicity']
    filter_fields = ['time', 'periodicity', 'action', 'place']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Habit.objects.filter(owner=self.request.user)
        else:
            return Habit.objects.none()


class PublicHabitListAPIView(generics.ListAPIView):
    serializer_class = HabitSerializer
    pagination_class = HabitListPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['action', 'place']
    ordering_fields = ['time', 'periodicity']
    filter_fields = ['time', 'periodicity', 'action', 'place']

    def get_queryset(self):
        return Habit.objects.filter(sign_publicity=True)


class HabitRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)


class HabitUpdateAPIView(generics.UpdateAPIView):
    serializer_class = HabitSerializer
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        habit = self.get_object()

        if request.data.get('complete', False):
            habit.last_execution_date = timezone.now().date()
            habit.save()

        if habit.sign_publicity and habit.owner != request.user:
            raise exceptions.PermissionDenied("Вы не можете редактировать чужие публичные привычки.")
        return super().update(request, *args, **kwargs)


class HabitDestroyAPIView(generics.DestroyAPIView):
    queryset = Habit.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)
