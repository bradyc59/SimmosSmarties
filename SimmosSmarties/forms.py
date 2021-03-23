from django.forms import ModelForm, ModelChoiceField
from .models import Product, CaUser, ProductCategory, Order
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction
from django import forms


class CategoryChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class ProductForm(ModelForm):
    category = CategoryChoiceField(queryset=ProductCategory.objects.all())

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'picture', 'category', 'featured', 'on_sale', 'sale_price']


class CheckoutForm(ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'address1', 'address2', 'city', 'county', 'country', 'postcode']


class CaSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CaUser

        @transaction.atomic
        def save(self):
            user = super().save(commit=False)
            user.is_admin = False
            user.save()
            return user


class AdminSignupForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CaUser

        @transaction.atomic
        def save(self):
            user = super().save(commit=False)
            user.is_admin = True
            user.save()
            return user


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.TextInput(attrs={'class': 'form_control', 'placeholder': '', 'id': 'hello'})
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '', 'id': 'hello'}))
