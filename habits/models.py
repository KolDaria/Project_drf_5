from django.db import models
from django.utils import timezone

from users.models import User


class Habit(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='habits',
        verbose_name='Владелец'
    )
    creator = models.CharField(
        max_length=200,
        verbose_name="Создатель",
        help_text="Имя пользователя создавшего привычку (для публичных привычек)",
        default="system"
    )
    place = models.CharField(
        max_length=200,
        verbose_name="Место",
        help_text="Место выполнения привычки."
    )
    time = models.TimeField(
        verbose_name='Время выполнения',
        help_text='Время, когда необходимо выполнять привычку',
    )
    action = models.TextField(
        verbose_name="Действие",
        help_text="Действие, которое представляет собой привычку.",
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name='Приятная привычка',
        help_text='Укажите, является ли привычка приятной (True) или полезной (False).'
    )
    associated_habit = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Связанная привычка',
        help_text='Связанная привычка (важно указывать для полезных привычек, но не для приятных).',
        related_name='linked_habits'
    )
    periodicity = models.IntegerField(
        default=1,
        verbose_name='Периодичность (в днях)',
        help_text='Периодичность выполнения привычки для напоминания в днях. '
                  'Например, 1 - ежедневно, 7 - раз в неделю)'
    )
    reward = models.TextField(
        verbose_name="Вознаграждение",
        help_text="Укажите вознаграждение",
        blank=True,
        null=True
    )
    time_complete = models.PositiveIntegerField(
        default=120,
        verbose_name='Время на выполнение (в секундах)',
        help_text='Время, за которое необходимо выполнить привычку (в секундах).'
    )
    sign_publicity = models.BooleanField(
        default=False,
        verbose_name='Признак публичности',
        help_text='Привычки можно публиковать в общий доступ, '
                  'чтобы другие пользователи могли брать в пример чужие привычки.'
    )
    last_execution_date = models.DateField(
        verbose_name="Дата последнего выполнения",
        help_text="Дата последнего выполнения привычки.",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        verbose_name="Дата создания",
        default=timezone.now
    )

    def __str__(self):
        return f"Привычка: {self.action} (Владелец: {self.owner.username})"

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
