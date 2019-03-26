"""
Referendum's app: Test registration views
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, LiveServerTestCase
from django.urls import reverse

from referendum.views.account import AccountView


class AccountViewTestCase(LiveServerTestCase):
    """
    Test Account view.
    """

    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create(username='test', email='test@test.fr', is_active=True)
        self.password = "test"
        self.user.set_password(self.password)
        self.user.save()

    def test_page_access_when_logged_in(self):
        """
        Test access to account page when logged in.
        """
        print(self.client.login(username=self.user.email, password=self.password))
        response = self.client.get(reverse('account', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)

    def test_page_access_when_not_logged_in(self):
        """
        Test access to account page when not logged in. Should be redirect.
        """
        response = self.client.get(reverse('account', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
                         "%s?next=%s" % (settings.LOGIN_URL, reverse('account', kwargs={'pk': self.user.pk})))

    def test_update_account(self):
        self.client.login(username=self.user.email, password=self.password)
        user_initial_first_name = self.user.first_name
        self.assertEqual(user_initial_first_name, '')
        print(self.user.pk)
        new_user_values = {
            'username': self.user.username,
            'email': self.user.email,
            'first_name': 'leo',
            'last_name': ''
        }
        response = self.client.post(
            reverse('account', kwargs={'pk': self.user.pk}), new_user_values, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.resolver_match.func.__name__, AccountView.as_view().__name__)
        self.user.refresh_from_db()
        self.assertNotEqual(user_initial_first_name, self.user.first_name)
