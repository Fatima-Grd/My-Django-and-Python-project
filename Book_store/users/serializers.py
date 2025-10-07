from rest_framework import serializers
from users.models import Profile
from .models import Book


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.phone_number")

    class Meta:
        model = Profile
        fields = ["address", "national_code",  "user"]


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.user.phone_number')

    class Meta:
        model = Book
        fields = ['id', 'title', 'description', 'author_name', 'created_at']


