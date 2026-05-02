import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning.settings')
django.setup()

from courses.models import User, Category, Course

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass', role='Admin')
    print("Superuser created")

if not User.objects.filter(username='instructor1').exists():
    instructor = User.objects.create_user('instructor1', 'i@e.com', 'pass123', role='Instructor')
    instructor.is_approved = True
    instructor.save()
    print("Instructor created")
else:
    instructor = User.objects.get(username='instructor1')
    if not instructor.is_approved:
        instructor.is_approved = True
        instructor.save()

# Add 4 new instructors
for i in range(2, 6):
    username = f'instructor{i}'
    if not User.objects.filter(username=username).exists():
        new_instructor = User.objects.create_user(username, f'i{i}@e.com', 'pass123', role='Instructor')
        new_instructor.is_approved = True
        new_instructor.save()
        print(f"{username} created")

if not User.objects.filter(username='student1').exists():
    User.objects.create_user('student1', 's@e.com', 'pass123', role='Student')
    print("Student created")

cat_programming, _ = Category.objects.get_or_create(name='Programming', defaults={'description':'Learn to code'})
cat_design, _ = Category.objects.get_or_create(name='Design', defaults={'description':'Learn design'})
print("Categories ensured")

courses_data = [
    {"title": "Advanced Python Development", "description": "Master deep python concepts including async, OOP and decorators.", "price": 49.99, "category": cat_programming},
    {"title": "Introduction to UI/UX", "description": "A beginner guide to modern user interface design using Figma.", "price": 29.99, "category": cat_design},
    {"title": "Django for Beginners", "description": "Build modern backend systems quickly with Django and Python.", "price": 59.99, "category": cat_programming},
    {"title": "Mastering CSS & Tailwind", "description": "Learn rapid styling with modern CSS practices and Tailwind.", "price": 19.99, "category": cat_design},
    {"title": "Full-Stack Web Engineering", "description": "Combine the front-end and back-end into cohesive systems.", "price": 99.99, "category": cat_programming},
]

added = 0
for data in courses_data:
    if not Course.objects.filter(title=data['title']).exists():
        Course.objects.create(
            title=data['title'],
            description=data['description'],
            price=data['price'],
            category=data['category'],
            instructor=instructor
        )
        added += 1

print(f"{added} courses added successfully.")
