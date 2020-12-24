from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ContactForm(forms.Form):
    """
    Contact Form allowing a user to send a message
    """

    name = forms.CharField(required=True)
    contact_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(
        widget=forms.Textarea(), required=True, max_length=2048,
    )

    def json(self):
        """
        Returns class attributes as a dictionary.
        """
        return {
            "name": self.name,
            "contact_email": self.contact_email,
            "subject": self.subject,
            "message": self.message,
        }


class NewUserForm(UserCreationForm):
    """
    Extends the UserCreationForm class to add an Email field
    for user registration form
    """

    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        """
        Removes ugly fields hints (help_text) for username, and password fields
        """
        super(NewUserForm, self).__init__(*args, **kwargs)

        for fieldname in ["username", "password1", "password2"]:
            self.fields[fieldname].help_text = None

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
