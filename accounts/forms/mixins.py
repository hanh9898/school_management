from django import forms

class DateOfBirthFormMixin:
    """
    Mixin để thêm widget date cho trường date_of_birth.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'date_of_birth' in self.fields:
            self.fields['date_of_birth'].widget = forms.DateInput(attrs={'type': 'date'})
