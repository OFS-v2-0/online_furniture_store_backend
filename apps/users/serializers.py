from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'birthday', 'phone', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
