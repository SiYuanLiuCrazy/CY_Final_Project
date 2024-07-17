from django import forms

class CatalogForm(forms.Form):
    catalog = forms.CharField(max_length=64, label='Catalog Name')