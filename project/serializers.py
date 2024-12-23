from rest_framework import serializers
from .models import Project, Bid
from user.models import FreelancerProfile, User

from rest_framework import serializers
from .models import Project, Bid

class ProjectSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.username', read_only=True)
    bid_count = serializers.SerializerMethodField()
    winning_bid_details = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'description',
            'client_username',
            'budget_range_max',
            'status',
            'created_at',
            'deadline',
            'bid_count',
            'freelancer_rating',
            'winning_bid',
            'winning_bid_details'
        ]
        read_only_fields = ['client', 'status', 'winning_bid', 'freelancer_rating']

    def get_bid_count(self, obj):
        return obj.bids.count()

    def get_winning_bid_details(self, obj):
        if obj.winning_bid:
            return {
                'freelancer': obj.winning_bid.freelancer.username,
                'amount': obj.winning_bid.amount,
                'proposed_deadline': obj.winning_bid.proposed_deadline,
                'proposal_text': obj.winning_bid.proposal_text,
            }
        return None



class BidSerializer(serializers.ModelSerializer):
    freelancer_username = serializers.CharField(source='freelancer.username', read_only=True)
    freelancer_rating = serializers.DecimalField(
        source='freelancer.freelancer_profile.rating',
        max_digits=3,
        decimal_places=2,
        read_only=True
    )
    project_title = serializers.CharField(source='project.title', read_only=True)
    project_status = serializers.CharField(source='project.status', read_only=True)

    class Meta:
        model = Bid
        fields = [
            'id',
            'project',
            'project_title',
            'project_status',
            'freelancer_username',
            'freelancer_rating',
            'amount',
            'proposed_deadline',
            'proposal_text',
            'created_at'
        ]
        read_only_fields = ['freelancer']

    def validate(self, data):
        project = data['project']

        if project.status != 'open':
            raise serializers.ValidationError(
                "Cannot bid on a project that is not open"
            )

        if data['amount'] > project.budget_range_max:
            raise serializers.ValidationError(
                f"Bid amount cannot exceed project budget of {project.budget_range_max}"
            )

        if data['proposed_deadline'] > project.deadline:
            raise serializers.ValidationError(
                "Proposed deadline cannot be later than project deadline"
            )

        if not self.instance:
            user = self.context['request'].user
            if project.bids.filter(freelancer=user).exists():
                raise serializers.ValidationError(
                    "You have already placed a bid on this project"
                )

        return data


from rest_framework import serializers
from .models import Project, Bid


class AcceptBidSerializer(serializers.Serializer):
    bid_id = serializers.IntegerField()

    def validate_bid_id(self, value):
        project = self.context['project']
        try:
            bid = project.bids.get(id=value)
        except Bid.DoesNotExist:
            raise serializers.ValidationError("Invalid bid ID")
        return value

    def update(self, instance, validated_data):
        bid_id = validated_data.get('bid_id')
        project = self.context['project']

        try:
            bid = project.bids.get(id=bid_id)
        except Bid.DoesNotExist:
            raise serializers.ValidationError("Bid not found")

        if project.status != 'open':
            raise serializers.ValidationError("This project is not open for bidding")

        project.winning_bid = bid
        project.status = 'closed'
        project.save()
        return project
    
class CompleteProjectSerializer(serializers.Serializer):
    rating = serializers.IntegerField()

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def update(self, instance, validated_data):
        rating = validated_data.get('rating')
        project = self.context['project']

        if project.status != 'closed':
            raise serializers.ValidationError("Only closed projects can be completed")

        project.status = 'completed'
        project.freelancer_rating = rating
        project.save()

        freelancer = project.winning_bid.freelancer
        if hasattr(freelancer, 'freelancer_profile'):
            freelancer.freelancer_profile.calculate_rating()

        return project


