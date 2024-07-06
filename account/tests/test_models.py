from django.test import TestCase
from django.contrib.auth import get_user_model

class UserModelTest(TestCase):

    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            email='user@example.com',
            name='Regular User',
            password='testpass123'
        )
        self.superuser = self.user_model.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='adminpass123'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, 'user@example.com')
        self.assertEqual(self.user.name, 'Regular User')
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_admin)
        self.assertTrue(self.user.check_password('testpass123'))

    def test_superuser_creation(self):
        self.assertEqual(self.superuser.email, 'admin@example.com')
        self.assertEqual(self.superuser.name, 'Admin User')
        self.assertTrue(self.superuser.is_active)
        self.assertTrue(self.superuser.is_admin)
        self.assertTrue(self.superuser.check_password('adminpass123'))

    def test_user_str(self):
        self.assertEqual(str(self.user), 'user@example.com')
        self.assertEqual(str(self.superuser), 'admin@example.com')

    def test_user_has_perm(self):
        self.assertTrue(self.superuser.has_perm(None))
        self.assertTrue(self.superuser.has_module_perms(None))
        self.assertFalse(self.user.has_perm(None))
        self.assertFalse(self.user.has_module_perms(None))

    def test_user_is_staff(self):
        self.assertTrue(self.superuser.is_staff)
        self.assertFalse(self.user.is_staff)

    def test_user_type_default(self):
        self.assertEqual(self.user.user_type, 'S')

    def test_user_creation_without_email(self):
        with self.assertRaises(ValueError):
            self.user_model.objects.create_user(
                email='',
                name='No Email User',
                password='nopass123'
            )
