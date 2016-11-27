from django import forms

from django.contrib.auth.models import User
from mocking.models import *

from django.forms.widgets import HiddenInput
from django.contrib.auth.forms import PasswordResetForm


class RegistrationForm(forms.Form):
    username = forms.CharField(error_messages={'required': 'Username is required'},
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    first_name = forms.CharField(error_messages={'required': 'First name is required'},
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(error_messages={'required': 'Last name is required'},
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(error_messages={'required': 'Email is required'},
                             widget=forms.EmailInput(
                                 attrs={'class': 'form-control', 'placeholder': 'Email'}))
    pwd = forms.CharField(error_messages={'required': 'Password is required'},
                          widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    pwd2 = forms.CharField(error_messages={'required': 'Confirm password is required'},
                           widget=forms.PasswordInput(
                               attrs={'class': 'form-control', 'placeholder': 'Re-enter Password'}))

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        pwd = cleaned_data.get('pwd')
        pwd2 = cleaned_data.get('pwd2')
        if pwd and pwd2 and pwd != pwd2:
            raise forms.ValidationError("Passwords did not match.")

        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        # Generally return the cleaned data we got from the cleaned_data
        # dictionary
        return username

    def clean_email(self):
        # Confirms that the email is not already present in the
        # User model database.
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__exact=email):
            raise forms.ValidationError("Email is already taken.")

        # Generally return the cleaned data we got from the cleaned_data
        # dictionary
        return email


class LoginForm(forms.Form):
    username = forms.CharField(error_messages={'required': 'Username is required'},
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    pwd = forms.CharField(error_messages={'required': 'Password is required'},
                          widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class AddProblemForm(forms.Form):
    name = forms.CharField(error_messages={'required': 'problem name is required'},
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'problem name'}))
    description = forms.CharField(error_messages={'required': 'descrption is required'},
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'descrption'}))
    solution = forms.CharField(error_messages={'required': 'solution is required'},
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'solution'}))
    difficulty = forms.IntegerField(error_messages={'required': 'difficulty is required'},
                                    widget=forms.TextInput(
                                        attrs={'class': 'form-control', 'placeholder': 'difficulty'}))
    category = forms.ModelChoiceField(queryset=ProblemCategory.objects.all())


class AddProblemCategoryForm(forms.Form):
    name = forms.CharField(error_messages={'required': 'new problem category is required'},
                           widget=forms.TextInput(
                               attrs={'class': 'form-control', 'placeholder': 'new problem category'}))


class AddLanguageForm(forms.Form):
    name = forms.CharField(error_messages={'required': 'new language is required'},
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'new language'}))


class ChooseRoleForm(forms.Form):
    role = forms.ChoiceField(choices={
        ('1', 'Interviewee'),
        ('0', 'Interviewer'),
    })  # , widget=forms.TextInput(attrs={'id': 'role'}))

    problem = forms.ModelChoiceField(queryset=Problem.objects.all())


class RateForm(forms.Form):
    rate = forms.IntegerField()
    rated_on = forms.IntegerField()
    rated_by = forms.IntegerField()
    interview = forms.IntegerField()

    def clean_rated_on(self):
        rated_on = self.cleaned_data.get('rated_on')
        if not User.objects.filter(pk=rated_on):
            raise forms.ValidationError("Unknown user to rate")
        return rated_on

    def clean_rated_by(self):
        rated_by = self.cleaned_data.get('rated_by')
        if not User.objects.filter(pk=rated_by):
            raise forms.ValidationError("Rated by Unknown user")
        return rated_by

    def clean_interview(self):
        interview = self.cleaned_data.get('interview')
        if not Interview.objects.filter(pk=interview):
            raise forms.ValidationError("Interview does not exist")
        return interview

    def clean_rate(self):
        rate = self.cleaned_data.get('rate')
        if rate < 0 or rate > 5:
            raise forms.ValidationError("Rate out of range")
        return rate

    def clean(self):
        cleaned_data = super(RateForm, self).clean()

        rated_on = cleaned_data.get('rated_on')
        rated_by = cleaned_data.get('rated_by')
        interview = Interview.objects.get(pk=cleaned_data.get('interview'))
        if (interview.interviewer_id == rated_on and interview.interviewee_id == rated_by) or (
                interview.interviewer_id == rated_by and interview.interviewee_id == rated_on):
            # check if already rated
            if not RateRecord.objects.filter(interview=interview, rated_on=rated_on):
                return cleaned_data
            raise forms.ValidationError("Already rated")

        raise forms.ValidationError("Parameters do not match")
