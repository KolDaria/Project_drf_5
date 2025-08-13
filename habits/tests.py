import datetime

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitTestCase(APITestCase):
    def setUp(self):
        # Создаем пользователя
        self.owner_user = User.objects.create_user(
            email='owner@example.com', password='password123')
        self.regular_user = User.objects.create_user(
            email='regular@example.com', password='password123')

        # Создаем тестовые привычки
        self.habit1 = Habit.objects.create(
            owner=self.owner_user,
            creator='owner11',
            place='Парк',
            time=timezone.now().time(),
            action="Пробежка",
            is_pleasant=True,
            periodicity=1,
            time_complete=120
        )
        self.habit2 = Habit.objects.create(
            owner=self.regular_user,
            creator='regular11',
            place='Дом',
            time=timezone.now().time(),
            action="Уборка",
            is_pleasant=False,
            periodicity=1,
            time_complete=60
        )

        # URLs
        self.habit_list_url = reverse('habits:habit-list')
        self.habit_public_url = reverse('habits:habit-public-list')
        self.habit_retrieve_habit2_url = reverse('habits:habit-retrieve', kwargs={'pk': self.habit2.pk})
        self.habit_retrieve_url = reverse('habits:habit-retrieve', kwargs={'pk': self.habit1.pk})
        self.habit_create_url = reverse('habits:habit-create')
        self.habit_update_url = reverse('habits:habit-update', kwargs={'pk': self.habit1.pk})
        self.habit_delete_url = reverse('habits:habit-delete', kwargs={'pk': self.habit1.pk})

    def test_habit_list_authenticated(self):
        """Аутентифицированный пользователь должен видеть список публичных привычек."""
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.habit_public_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_habit_list_owner(self):
        """Владелец должен видеть только свои привычки."""
        self.client.force_authenticate(user=self.owner_user)
        response = self.client.get(self.habit_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['creator'], 'owner11')

    def test_habit_retrieve_owner(self):
        """Владелец должен иметь возможность просматривать детали своих привычек."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.habit_retrieve_habit2_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['creator'], 'regular11')

    def test_habit_retrieve_other_user(self):
        """Пользователь не должен иметь возможность просматривать детали чужих привычек."""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.habit_retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_habit_owner(self):
        """Аутентифицированный пользователь может создать привычку."""
        self.client.force_authenticate(user=self.owner_user)
        current_time = datetime.datetime.now().time()

        data = {
            'place': 'Дом',
            'time': current_time.strftime('%H:%M:%S'),
            'action': 'Зарядка',
            'is_pleasant': False,
            'periodicity': 1,
            'time_complete': 60,
        }

        response = self.client.post(self.habit_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 3)
        habit = Habit.objects.last()
        self.assertEqual(habit.owner, self.owner_user)
        self.assertEqual(habit.place, 'Дом')
        self.assertEqual(habit.action, 'Зарядка')
        self.assertFalse(habit.is_pleasant)
        self.assertEqual(habit.periodicity, 1)
        self.assertEqual(habit.time_complete, 60)
        self.assertFalse(habit.sign_publicity)

    def test_update_habit_owner(self):
        """Владелец может обновить свою привычку."""
        self.client.force_authenticate(user=self.owner_user)
        data = {
            'time': '09:00:00',
        }
        url = self.habit_update_url
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_habit = Habit.objects.get(pk=self.habit1.pk)
        self.assertEqual(updated_habit.time.strftime('%H:%M:%S'), '09:00:00')

    def test_update_course_not_owner(self):
        """Не владелец не может обновить чужую привычку."""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'time': '19:00:00',
        }
        url = self.habit_update_url
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_habit_owner(self):
        """Владелец может удалить свои привычки."""
        self.client.force_authenticate(user=self.owner_user)
        url = self.habit_delete_url
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(pk=self.habit1.pk).count(),
                         0)

    def test_delete_habit_not_owner(self):
        """Не владелец не может удалить чужой курс."""
        self.client.force_authenticate(user=self.regular_user)
        url = self.habit_delete_url
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authentication_required_for_list(self):
        """Тест, что для просмотра списка привычек требуется аутентификация."""
        self.client.logout()
        response = self.client.get(self.habit_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_public_habit_not_owner(self):
        """Не владелец не может обновить чужую публичную привычку."""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'time': '19:00:00',
        }
        url = self.habit_update_url
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
