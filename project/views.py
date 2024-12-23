from rest_framework import generics, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q

from user.models import FreelancerProfile
from .models import Project, Bid
from .serializers import ProjectSerializer, BidSerializer, AcceptBidSerializer, CompleteProjectSerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Project.objects.all()
        # Get search parameter from query params
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        return queryset

    def perform_create(self, serializer):
        # Only clients can create projects
        if self.request.user.user_type != 'client':
            raise ValidationError("Only clients can create projects")
        serializer.save(client=self.request.user)

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.all()

    def get_queryset(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return Project.objects.filter(client=self.request.user)
        return Project.objects.all()


class BidCreateView(generics.CreateAPIView):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]
    queryset = Bid.objects.all()

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])

        if self.request.user.user_type != 'freelancer':
            raise ValidationError("Only freelancers can place bids")

        if project.status != 'open':
            raise ValidationError("This project is not open for bidding")

        if Bid.objects.filter(project=project, freelancer=self.request.user).exists():
            raise ValidationError("You have already placed a bid on this project")

        serializer.save(
            freelancer=self.request.user,
            project=project
        )

        lowest_bid = project.bids.order_by('amount').first()
        project.winning_bid = lowest_bid
        project.save()


class IsProjectOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        project_id = view.kwargs.get('project_id')
        if not project_id:
            return False

        project = get_object_or_404(Project, pk=project_id)
        return project.client == request.user

class ProjectBidsListView(generics.ListAPIView):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated, IsProjectOwner]
    queryset = Bid.objects.all()

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])

        # Double-check permission (although permission_classes should handle this)
        if project.client != self.request.user:
            raise PermissionDenied("Only the project owner can view bids")

        return Bid.objects.filter(project=project).order_by('amount')

    def handle_exception(self, exc):
        if isinstance(exc, PermissionDenied):
            return Response(
                {"error": str(exc)},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().handle_exception(exc)


class AcceptBidView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AcceptBidSerializer

    def get_queryset(self):
        return Project.objects.filter(client=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        project = self.get_object()
        context['project'] = project
        return context

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = self.get_serializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            project = serializer.save()
            return Response({
                "message": "Bid accepted successfully",
                "project": ProjectSerializer(project).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteProjectView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CompleteProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(client=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        project = self.get_object()
        context['project'] = project
        return context

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        serializer = self.get_serializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            project = serializer.save()
            return Response({
                "message": "Project completed successfully",
                "project": ProjectSerializer(project).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MyProjectsView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'client':
            return Project.objects.filter(client=user)
        else:  # freelancer
            return Project.objects.filter(winning_bid__freelancer=user)


class MyBidsView(generics.ListAPIView):
    serializer_class = BidSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type != 'freelancer':
            return Bid.objects.none()
        return Bid.objects.filter(freelancer=self.request.user)

