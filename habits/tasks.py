from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from habits.models import Habit
from habits.services import send_telegram_message


@shared_task
def send_reminder_habit_time():
    now = timezone.now()
    now_time = now.time()
    today = now.date()

    habits = Habit.objects.filter(owner__tg_chat_id__isnull=False)

    for habit in habits:
        last_execution_date = habit.last_execution_date

        if last_execution_date is None:
            last_execution_date = habit.created_at.date()

        next_execution_date = last_execution_date + timedelta(days=habit.periodicity)

        if next_execution_date <= today:
            habit_time = habit.time
            if habit_time.hour == now_time.hour and habit_time.minute == now_time.minute:
                message = f"Напоминание: Пора выполнить привычку '{habit.action}' в {habit.place}!"
                user = habit.owner
                send_telegram_message(user.tg_chat_id, message)
