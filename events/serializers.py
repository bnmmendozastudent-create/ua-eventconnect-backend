from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Event, Registration


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'student_id', 'course', 'role']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'student_id', 'course', 'role']


class EventSerializer(serializers.ModelSerializer):
    slots_remaining = serializers.ReadOnlyField()
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


class RegistrationSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(), source='event', write_only=True
    )

    class Meta:
        model = Registration
        fields = ['id', 'student', 'event', 'event_id', 'status', 'registered_at']