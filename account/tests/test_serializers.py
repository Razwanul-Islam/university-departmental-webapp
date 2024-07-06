from account.models import User
from rest_framework.test import APITestCase
from account.serializers import UserRegistrationSerializer,UserLoginSerializer,UserProfileSerializer


class TestUserRegistrationSerializer(APITestCase):


    def test_can_create_user(self):
        data={
            'email':'test@gmail.com',
            'name':'test',
            'password':'test123',
            'password2':'test123'
        }

        serializer=UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors,{})
    

    def test_user_serializer_password_mismatch(self):
        data={
            'email':'test@gmail.com',
            'name':'test',
            'password':'test1234',
            'password2':'mtest1234'
        }
        serializer=UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        #self.assertTrue(serializer.is_valid())
        #self.assertEqual(serializer.errors['non_field_errors'][0], "Password doesn't match")
        #self.assertEqual(serializer.errors,{})

    # def test_user_serializer_duplicate_email(self):
    #     User.objects.create_user(email='existinguser@example.com',password='test1234',name='test') 

    #     data={
    #         'email':'existinguser@example.com',
    #         'name':'test',
    #         'password':'test1234',
    #         'password2':'test1234',
    #         }
    #     serializer=UserRegistrationSerializer(data=data)
    #     self.assertFalse(serializer.is_valid())
    #     self.assertEqual(serializer.errors['email'][0], 'user with this email already exists.') 

    
    def test_user_serializer_create(self):
        data={
            'email':'test@gmail.com',
            'name':'test', 
            'password':'test1234',
            'password2':'test1234',     
        }
        serializer=UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user=serializer.create(serializer.validated_data)

        self.assertEqual(user.email,'test@gmail.com')
        self.assertEqual(user.name,'test')
        self.assertTrue(user.is_active)


    def test_user_serializer_update(self):
        user=User.objects.create_user(email='existinguser@gmail.com',password='test1234',name='test')

        data={
            'name':'test1',   
        }
        serializer=UserRegistrationSerializer(user,data=data,partial=True)
        self.assertTrue(serializer.is_valid())

        update_user=serializer.update(user,serializer.validated_data)
        
        self.assertEqual(update_user.name,'test1')
