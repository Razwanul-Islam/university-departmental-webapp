import pytest
from rest_framework.exceptions import ValidationError
from account.models import User
from account.serializers import UserRegistrationSerializer, UserLoginSerializer

@pytest.mark.django_db
class TestUserRegistrationSerializer:
    
    def test_password_match(self):
        # Test case where passwords match
        data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testpassword',
            'password2': 'testpassword'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['password'] == 'testpassword'
        assert serializer.validated_data['password2'] == 'testpassword'
        
        # Test case where passwords don't match
        data['password2'] = 'differentpassword'
        serializer = UserRegistrationSerializer(data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_create_user(self):
        data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'password': 'testpassword',
            'password2': 'testpassword'
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()
        
        # Call create method
        user = serializer.save()
        
        assert user.email == 'test@example.com'
        assert user.name == 'Test User'
        assert user.check_password('testpassword')

@pytest.mark.django_db
class TestUserLoginSerializer:
    
    def test_valid_serialization(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        serializer = UserLoginSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['email'] == 'test@example.com'
        assert serializer.validated_data['password'] == 'testpassword'

    def test_valid_deserialization(self):
        user = User.objects.create_user(email='test@example.com', name='Test User', password='testpassword')
        serializer = UserLoginSerializer(instance=user)
        
        # The password field in the serialized data is hashed
        expected_data = {
            'email': 'test@example.com',
            'password': user.password  # Compare against the hashed password stored in the database
        }
        assert serializer.data['email'] == expected_data['email']
        assert serializer.data['password'] == expected_data['password']