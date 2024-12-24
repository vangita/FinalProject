from django.db import models
from django.conf import settings
from project.models import Project

class Payment(models.Model):
    PAYMENT_STATUSES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUSES, default='pending')
    transaction_reference = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.transaction_reference} for {self.project.title} by {self.user.username}"

    class Meta:
        ordering = ['-created_at']
