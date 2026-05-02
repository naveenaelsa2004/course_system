from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Course, CourseVideo, CourseNote

class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Add form-control class to all widgets except checkbox
            if not isinstance(field.widget, forms.CheckboxInput):
                existing_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f"{existing_class} form-control".strip()
            
            # Set empty_label to "Select" for ModelChoiceFields
            if isinstance(field, forms.ModelChoiceField):
                field.empty_label = "Select"

class UserRegistrationForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=[('', 'Select')] + [c for c in User.ROLE_CHOICES if c[0] != 'Admin'],
        required=True
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'role',)

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.role == 'Instructor':
            user.is_approved = False
        if commit:
            user.save()
        return user

class UserLoginForm(StyledFormMixin, AuthenticationForm):
    pass

class CourseForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category']

class CourseVideoForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CourseVideo
        fields = ['title', 'video_url']

class CourseNoteForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = CourseNote
        fields = ['title', 'pdf_file']

from django.forms import inlineformset_factory

VideoFormSet = inlineformset_factory(
    Course, CourseVideo, form=CourseVideoForm,
    extra=1, can_delete=True
)

NoteFormSet = inlineformset_factory(
    Course, CourseNote, form=CourseNoteForm,
    extra=1, can_delete=True
)
