from django import forms


class MyRegForm(forms.Form):
    password1 = forms.CharField(max_length=150, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=150, widget=forms.PasswordInput())
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=True)
