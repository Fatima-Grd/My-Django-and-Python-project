from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, HttpResponse, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import status
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
import json
from users.models import MainUser, Profile
from django.views.decorators.csrf import csrf_exempt
from users.forms import UserForm
from users.serializers import ProfileSerializer
from .models import Book, Profile
from .serializers import BookSerializer



def home(request):
    return HttpResponse("Hi friends from MFT")


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        phone_number = data["phone_number"]

        user = authenticate(request, phone_number=phone_number,
                            password=data["password"])
        if user:
            login(request, user)
            return redirect('home')
        return redirect('register')
    return redirect('register')


@csrf_exempt
def register(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        form = UserForm(data=data)
        if form.is_valid():
            phone_number = data['phone_number']
            password = data['password']
            user = MainUser.objects.create(phone_number=phone_number)
            user.set_password(password)
            user.save()
            Profile.objects.create(user=user)
            return HttpResponse(f"User {phone_number} has been created.")
        return HttpResponse("Data format is not correct")
    return HttpResponse("You Have to Register!")


def get_all_profile(request):

    if request.method == "GET":
        profiles_list = []
        profiles = Profile.objects.all()
        for profile in profiles:
            profiles_list.append({"user": profile.user.phone_number,
                                  "national_code": profile.national_code,
                                  "address": profile.address})

        return render(request, "profiles.html",
                      {"profiles": profiles_list})


class Profiles(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class CreateBook(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_profile = request.user.profile

        book = Book(
            title=request.data.get('title'),
            description=request.data.get('description', ''),
            author=user_profile
        )
        book.save()

        return Response({
            'message': 'Book created successfully',
            'book_id': book.id,
            'title': book.title
        })


class AllBooks(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


class MyBooks(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = request.user.profile
        my_books = Book.objects.filter(author=user_profile)
        serializer = BookSerializer(my_books, many=True)
        return Response(serializer.data)

