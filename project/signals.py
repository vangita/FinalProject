from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Bid, Project

@receiver(post_save, sender=Bid)
@receiver(post_delete, sender=Bid)
def update_winning_bid(sender, instance, **kwargs):
    project = instance.project
    lowest_bid = project.bids.order_by('amount').first()

    project.winning_bid = lowest_bid
    project.save()
