from django import forms
from .models import Feedback, GuitarOrder


class FeedbackForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "autocomplete": "off",
            "tabindex": "-1",
            "aria-hidden": "true",
        })
    )
    class Meta:
        model = Feedback
        fields = ("name", "email", "message")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ваше ім’я", "maxlength": "80"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@example.com"}),
            "message": forms.Textarea(attrs={"placeholder": "Розкажіть, яку гітару шукаєте", "rows": 5, "maxlength": "1200"}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if len(name) < 2:
            raise forms.ValidationError("Ім’я має містити щонайменше 2 символи.")
        return name

    def clean_message(self):
        message = self.cleaned_data.get("message", "").strip()
        if len(message) < 10:
            raise forms.ValidationError("Повідомлення має містити щонайменше 10 символів.")
        return message

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("website"):
            raise forms.ValidationError("Помилка відправки форми (виявлено підозрілу активність).")
        return cleaned_data


class GuitarConfigForm(forms.ModelForm):
    QUANTITY_CHOICES = [(n, str(n)) for n in range(1, 11)]
    quantity = forms.TypedChoiceField(label="Кількість", choices=QUANTITY_CHOICES, coerce=int, initial=1)

    class Meta:
        model = GuitarOrder
        fields = (
            "instrument_type",
            "body_shape",
            "wood",
            "color",
            "frets_count",
            "strings_count",
            "pickups_set",
            "quantity",
        )


class CartQuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=20)