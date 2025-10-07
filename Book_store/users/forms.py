from django import forms
from users.models import MainUser


class UserForm(forms.ModelForm):

    class Meta:
        model = MainUser
        fields = ['first_name', "last_name", "phone_number", "email"]
