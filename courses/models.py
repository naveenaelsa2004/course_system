from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Instructor', 'Instructor'),
        ('Student', 'Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Student')
    is_approved = models.BooleanField(default=True)

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Instructor'}, related_name='courses_taught')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    video_url = models.URLField(max_length=500, blank=True, null=True, help_text="Link to course video (e.g. YouTube, Vimeo)")
    notes = models.TextField(blank=True, null=True, help_text="Additional course notes or resources (text)")
    notes_pdf = models.FileField(upload_to='course_notes/', blank=True, null=True, help_text="Upload notes as PDF")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class CourseVideo(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    video_url = models.URLField(max_length=500, help_text="Link to video (e.g. YouTube, Vimeo)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course.title}"

class CourseNote(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes_list')
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='course_notes/', help_text="Upload notes as PDF")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.course.title}"

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Active', 'Active'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'}, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Future payment integration placeholder
    payment_id = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class SiteSetting(models.Model):
    site_name = models.CharField(max_length=255, default='E-Learning Hub')
    contact_email = models.EmailField(default='support@example.com')
    maintenance_mode = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super(SiteSetting, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Site Settings"
