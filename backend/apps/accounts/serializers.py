from __future__ import annotations

from typing import Any

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import User


class LoginSerializer(serializers.Serializer[Any]):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        user = authenticate(
            request=self.context.get("request"),
            username=data["username"],
            password=data["password"],
        )
        if user is None:
            # authenticate() returns None for bad credentials AND inactive users
            raise serializers.ValidationError("Invalid credentials.")
        data["user"] = user
        return data


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_staff"]
        read_only_fields = ["id", "username", "email", "is_staff"]
