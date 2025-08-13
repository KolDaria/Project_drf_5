from django.core.exceptions import ValidationError
from rest_framework import serializers

from habits.models import Habit


class HabitSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id', read_only=True)
    creator = serializers.CharField(default=serializers.CurrentUserDefault(), read_only=True)

    class Meta:
        model = Habit
        fields = '__all__'

    def validate(self, data):
        """Основной метод валидации, вызывающий отдельные методы валидации."""
        self._validate_reward_and_related_habit(data)
        self._validate_pleasant_habit(data)
        self._validate_associated_habit_is_pleasant(data)
        self._validate_time_complete(data)
        return data

    def validate_periodicity(self, periodicity):
        """Проверяет, что периодичность находится в диапазоне от 1 до 7 дней."""
        if periodicity < 1 or periodicity > 7:
            raise ValidationError("Периодичность должна быть от 1 до 7 дней.")
        return periodicity

    def _validate_reward_and_related_habit(self, data):
        """Проверяет, что нельзя одновременно указывать связанную привычку и вознаграждение."""
        associated_habit = data.get('associated_habit')
        reward = data.get('reward')
        if associated_habit and reward:
            raise ValidationError(
                "Нельзя одновременно указывать связанную привычку и вознаграждение. Выберите что-то одно."
            )

    def _validate_pleasant_habit(self, data):
        """Проверяет, что у приятной привычки не может быть вознаграждения или связанной привычки."""
        is_pleasant = data.get('is_pleasant')
        associated_habit = data.get('associated_habit')
        reward = data.get('reward')

        if is_pleasant and (associated_habit or reward):
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )

    def _validate_associated_habit_is_pleasant(self, data):
        """Проверяет, что в связанные привычки могут попадать только приятные привычки."""
        associated_habit = data.get('associated_habit')
        if associated_habit and not associated_habit.is_pleasant:
            raise ValidationError(
                "В связанные привычки могут попадать только приятные привычки."
            )

    def _validate_time_complete(self, data):
        """Проверяет время выполнения."""
        time_complete = data.get('time_complete')
        if time_complete and (time_complete < 1 or time_complete > 120):
            raise ValidationError(
                "Время выполнения должно быть от 1 до 120 секунд."
            )
