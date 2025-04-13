from django import forms
from .models import InstructorProfile, Instrument, User

class InstructorProfileForm(forms.ModelForm):
    instruments = forms.ModelMultipleChoiceField(
        queryset=Instrument.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    # field that’s not part of the model by default
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = InstructorProfile
        fields = ['bio', 'city', 'level', 'instruments', 'profile_picture']

    # Get really help here!!!
    def __init__(self, *args, **kwargs):
        # Accept the current user via kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Set an initial value for the extra field if already available
        if self.instance.pk and self.instance.instructor.profile_picture:
            self.fields['profile_picture'].initial = self.instance.instructor.profile_picture

    def save(self, commit=True):
        instructor_profile = super().save(commit=False)
        # Get the uploaded file from cleaned_data
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture and self.user:
            # Save the new profile picture to the User instance
            self.user.profile_picture = profile_picture
            if commit:
                self.user.save()
        if commit:
            instructor_profile.save()
            self.save_m2m()
        return instructor_profile


class ApprenticeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'profile_picture']
