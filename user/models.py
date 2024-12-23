from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):
    USER_TYPES = (
        ('client', 'Client'),
        ('freelancer', 'Freelancer')
    )
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='client')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class FreelancerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="freelancer_profile")
    skills = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_projects = models.IntegerField(default=0)


    def calculate_rating(self):
        from project.models import Project

        completed_projects = Project.objects.filter(
            winning_bid__freelancer=self.user,
            status='completed'
        )
        if completed_projects.exists():
            total_rating = sum(project.freelancer_rating for project in completed_projects if project.freelancer_rating)
            self.rating = total_rating / completed_projects.count()
            self.completed_projects = completed_projects.count()
            self.save()

    def __str__(self):
        return self.user.username

