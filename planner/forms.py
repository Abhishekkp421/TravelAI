from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Trip, Place, Review


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter username"
        })

        self.fields["email"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter email"
        })

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter password"
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm password"
        })
class TripForm(forms.ModelForm):

    interests = forms.MultipleChoiceField(
        choices=[
            ("historical", "Historical"),
            ("nature", "Nature"),
            ("adventure", "Adventure"),
            ("food", "Food"),
            ("shopping", "Shopping"),
            ("spiritual", "Spiritual"),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Trip

        fields = [
            "destination",
            "days",
            "people",
            "budget",
            "food_preference",
            "travel_type",
            "interests",
        ]

        widgets = {

            "destination": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Jaipur, Delhi, Goa",
                    "autocomplete": "off",
                }
            ),

            "days": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 30,
                    "placeholder": "e.g. 3",
                }
            ),

            "people": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 20,
                    "placeholder": "e.g. 2",
                }
            ),

            "budget": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 500,
                    "placeholder": "e.g. 15000",
                }
            ),

            "food_preference": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),

            "travel_type": forms.Select(
                attrs={
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["interests"].widget.attrs.update({
            "class": "interest-options"
        })

    def clean_interests(self):
        return ", ".join(self.cleaned_data["interests"])
class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ["rating", "review_text"]

        widgets = {
            "rating": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "max": 5,
                    "placeholder": "Rate from 1 to 5",
                }
            ),

            "review_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Write your experience...",
                }
            ),
        }