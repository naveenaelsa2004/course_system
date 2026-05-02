from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment, Category, User, SiteSetting, CourseVideo, CourseNote
from .forms import UserRegistrationForm, CourseForm, UserLoginForm, VideoFormSet, NoteFormSet

def home(request):
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'courses/home.html', {'courses': courses})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'courses/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'courses/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    if not request.user.is_approved:
        return redirect('pending_approval')
        
    if request.user.role == 'Admin':
        courses = Course.objects.all().order_by('-created_at')
        instructors = User.objects.filter(role='Instructor')
        students = User.objects.filter(role='Student')
        enrollments_count = Enrollment.objects.count()
        return render(request, 'courses/admin_dashboard.html', {
            'courses': courses,
            'instructors': instructors,
            'students': students,
            'enrollments_count': enrollments_count
        })
    elif request.user.role == 'Instructor':
        courses = request.user.courses_taught.all()
        return render(request, 'courses/instructor_dashboard.html', {'courses': courses})
    else:
        enrollments = request.user.enrollments.all()
        enrolled_course_ids = enrollments.values_list('course_id', flat=True)
        available_courses = Course.objects.exclude(id__in=enrolled_course_ids).order_by('-created_at')
        return render(request, 'courses/student_dashboard.html', {
            'enrollments': enrollments,
            'available_courses': available_courses
        })

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    is_enrolled = False
    if request.user.is_authenticated and request.user.role == 'Student':
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    return render(request, 'courses/course_detail.html', {'course': course, 'is_enrolled': is_enrolled})

@login_required
def enroll_course(request, pk):
    if request.user.role != 'Student':
        return redirect('course_detail', pk=pk)
        
    course = get_object_or_404(Course, pk=pk)
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        Enrollment.objects.create(student=request.user, course=course, status='Active')
    return redirect('dashboard')

@login_required
def unenroll_course(request, pk):
    if request.user.role != 'Student':
        return redirect('dashboard')
        
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        Enrollment.objects.filter(student=request.user, course=course).delete()
    return redirect('dashboard')

@login_required
def course_create(request):
    if request.user.role not in ['Instructor', 'Admin'] or not request.user.is_approved:
        return redirect('home')
        
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            
            video_formset = VideoFormSet(request.POST, instance=course)
            note_formset = NoteFormSet(request.POST, request.FILES, instance=course)
            
            if video_formset.is_valid() and note_formset.is_valid():
                video_formset.save()
                note_formset.save()
                return redirect('dashboard')
    else:
        form = CourseForm()
        video_formset = VideoFormSet()
        note_formset = NoteFormSet()
    return render(request, 'courses/course_form.html', {
        'form': form, 
        'video_formset': video_formset,
        'note_formset': note_formset,
        'action': 'Create'
    })

@login_required
def course_edit(request, pk):
    if request.user.role == 'Admin':
        course = get_object_or_404(Course, pk=pk)
    else:
        course = get_object_or_404(Course, pk=pk, instructor=request.user)
        
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        video_formset = VideoFormSet(request.POST, instance=course)
        note_formset = NoteFormSet(request.POST, request.FILES, instance=course)
        
        if form.is_valid() and video_formset.is_valid() and note_formset.is_valid():
            form.save()
            video_formset.save()
            note_formset.save()
            return redirect('dashboard')
    else:
        form = CourseForm(instance=course)
        video_formset = VideoFormSet(instance=course)
        note_formset = NoteFormSet(instance=course)
    return render(request, 'courses/course_form.html', {
        'form': form, 
        'video_formset': video_formset,
        'note_formset': note_formset,
        'action': 'Edit'
    })

@login_required
def course_delete(request, pk):
    if request.user.role == 'Admin':
        course = get_object_or_404(Course, pk=pk)
    else:
        course = get_object_or_404(Course, pk=pk, instructor=request.user)
        
    if request.method == 'POST':
        course.delete()
        return redirect('dashboard')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})

@login_required
def course_students(request, pk):
    if request.user.role != 'Instructor':
        return redirect('dashboard')
    course = get_object_or_404(Course, pk=pk, instructor=request.user)
    enrollments = course.enrollments.all()
    return render(request, 'courses/instructor_students.html', {'course': course, 'enrollments': enrollments})

@login_required
def manage_users(request):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    users = User.objects.exclude(pk=request.user.pk)
    return render(request, 'courses/manage_users.html', {'users': users})

@login_required
def approve_user(request, pk):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    user.is_approved = not user.is_approved
    user.save()
    return redirect('manage_users')

@login_required
def delete_user(request, pk):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        return redirect('manage_users')
    return render(request, 'courses/user_confirm_delete.html', {'user_to_delete': user})

@login_required
def site_settings(request):
    if request.user.role != 'Admin':
        return redirect('dashboard')
    setting = SiteSetting.load()
    if request.method == 'POST':
        setting.site_name = request.POST.get('site_name', setting.site_name)
        setting.contact_email = request.POST.get('contact_email', setting.contact_email)
        setting.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
        setting.save()
        return redirect('dashboard')
    return render(request, 'courses/site_settings.html', {'setting': setting})

@login_required
def pending_approval(request):
    if request.user.is_approved:
        return redirect('dashboard')
    return render(request, 'courses/pending_approval.html')

@login_required
def focus_studio(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    # Check if student is enrolled or if the user is the instructor/admin
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    can_access = is_enrolled or request.user.role == 'Admin' or (request.user.role == 'Instructor' and course.instructor == request.user)
    
    if not can_access:
        return redirect('course_detail', pk=pk)
        
    return render(request, 'courses/focus_studio.html', {'course': course})
@login_required
def create_instructor(request):
    if request.user.role != 'Admin':
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'Instructor'
            user.is_approved = True
            user.save()
            return redirect('manage_users')
    else:
        form = UserRegistrationForm()
        
    return render(request, 'courses/create_instructor.html', {'form': form})
