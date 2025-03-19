from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'days', 'specific_days', 'group_size', 'location_type', 'description', 'experience', 'price_per_hour']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'days': forms.Select(),
            'group_size': forms.Select(),
            'location_type': forms.Select(),
        }

    def clean(self):
        cleaned_data = super().clean()
        days = cleaned_data.get('days')
        specific_days = cleaned_data.get('specific_days')
        if days == 'specific' and not specific_days:
            raise forms.ValidationError("Укажите конкретные дни, если выбрано 'Конкретные дни'.")
        elif days != 'specific':
            cleaned_data['specific_days'] = None  # Очищаем поле, если не выбрано "Конкретные дни"
        return cleaned_data