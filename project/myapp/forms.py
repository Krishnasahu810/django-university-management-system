from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from .models import Course, Instructor


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'description', 'credits', 'status', 'semester', 'instructor']


class AttendanceForm(forms.Form):
    student = forms.ModelChoiceField(queryset=CustomUser.objects.all())
    course = forms.ModelChoiceField(queryset=Course.objects.all())
    classes_held = forms.IntegerField(min_value=0, initial=0)
    present = forms.IntegerField(min_value=0, initial=0)
    absent = forms.IntegerField(min_value=0, initial=0)

class SignupForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
        