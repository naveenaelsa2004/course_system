from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Course, Enrollment

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Role Configuration', {'fields': ('role',)}),
    )

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'price', 'created_at')
    list_filter = ('category', 'instructor')
    search_fields = ('title', 'description')

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'enrollment_date')
    list_filter = ('status', 'course')
    search_fields = ('student__username', 'course__title')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
