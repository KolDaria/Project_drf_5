from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from config.settings import EMAIL_HOST_USER
from habits.models import Habit
from habits.services import send_telegram_message
from users.models import User


@shared_task
def send_reminder_habit_time(email):
    now = timezone.now()
    now_time = now.time()
    today = now.date()

    habits = Habit.objects.all()

    for habit in habits:
        last_execution_date = habit.last_execution_date

        if last_execution_date is None:
            last_execution_date = habit.created_at.date()

        next_execution_date = last_execution_date + timedelta(days=habit.periodicity)

        if next_execution_date <= today:
            habit_time = habit.time
            if habit_time.hour == now_time.hour and habit_time.minute == now_time.minute:
                message = f"Напоминание: Пора выполнить привычку '{habit.action}' в {habit.place}!"
                send_mail("Напоминание", message, EMAIL_HOST_USER, [email])
                user = User.objects.get(email=email)
                if user.tg_chat_id:
                    send_telegram_message(user.tg_chat_id, message)
