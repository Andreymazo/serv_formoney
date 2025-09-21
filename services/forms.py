from django import forms

from services.models import Query

class QueryForm(forms.Form):
    category = forms.CharField(max_length=200)
    max_number_for_analitic = forms.IntegerField(help_text="Enter number for analitic")

