"""
URL configuration for book_store project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from users.views import register, home, Profiles
from rest_framework_simplejwt.views import TokenObtainPairView
from django.urls import path
from users.views import register, home, Profiles, CreateBook, AllBooks, MyBooks



urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('register/', register, name='register'),
    path('profiles/', Profiles.as_view(), name='profiles'),
    path('books-create/', CreateBook.as_view(), name='create-book'),
    path('books-all/', AllBooks.as_view(), name='all-books'),
    path('books-my-books/', MyBooks.as_view(), name='my-books'),
    path('', home, name='home'),
]
