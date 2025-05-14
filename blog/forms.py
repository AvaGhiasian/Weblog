from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from blog.models import *


class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ('پیشنهاد', 'پیشنهاد'),
        ('انتقاد', 'انتقاد'),
        ('گزارش', 'گزارش'),
    )
    message = forms.CharField(widget=forms.Textarea, required=True)
    name = forms.CharField(max_length=250, required=True)
    email = forms.EmailField()
    phone = forms.CharField(max_length=11, required=True)
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES)

    def clean_phone(self):
        """ validate phone number """
        phone = self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError('شماره تماس عددی نیست!')
            else:
                return phone


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'body']
        widgets = {
            'body': forms.TextInput(attrs={
                'placeholder': 'متن',
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'نام',
                'class': 'form-control'
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if name:
            if len(name) > 250 or len(name) < 2:
                raise forms.ValidationError('نام معتبر نیست!')
            else:
                return name


class SearchForm(forms.Form):
    query = forms.CharField()


class CreatePostForm(forms.ModelForm):
    image1 = forms.ImageField(label="تصویر اول")
    image2 = forms.ImageField(label="تصویر دوم")

    class Meta:
        model = Post
        fields = ['title', 'description', 'reading_time']


# class LoginForm(forms.Form):
#     username = forms.CharField(max_length=250, required=True)
#     password = forms.CharField(max_length=250, required=True, widget=forms.PasswordInput)


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(max_length=20, widget=forms.PasswordInput, label='password')
    password_2 = forms.CharField(max_length=20, widget=forms.PasswordInput, label='repeat password')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password_2(self):
        if self.cleaned_data['password'] != self.cleaned_data['password_2']:
            raise forms.ValidationError('پسوردها مطابقت ندارند!')
        return self.cleaned_data['password_2']


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class AccountEditForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['date_of_birth', 'bio', 'job', 'photo']