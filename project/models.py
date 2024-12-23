from django.db import models

from user.models import User


class Project(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open for Bids'),
        ('closed', 'Bidding Closed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_projects')
    budget_range_max = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField()
    winning_bid = models.OneToOneField('Bid', on_delete=models.SET_NULL, null=True, blank=True, related_name='won_project')
    freelancer_rating = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

class Bid(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bids')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    proposed_deadline = models.DateField()
    proposal_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['amount'] 
        unique_together = ['project', 'freelancer']
