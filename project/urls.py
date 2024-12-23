from django.urls import path
from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    BidCreateView,
    ProjectBidsListView,
    AcceptBidView,
    CompleteProjectView,
    MyProjectsView,
    MyBidsView,
)

urlpatterns = [
    path('projects/', ProjectListCreateView.as_view(), name='project-list-create'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('projects/<int:project_id>/bid/', BidCreateView.as_view(), name='bid-create'),
    path('projects/<int:project_id>/bids/', ProjectBidsListView.as_view(), name='project-bids-list'),
    path('projects/<int:pk>/accept-bid/', AcceptBidView.as_view(), name='accept-bid'),
    path('projects/<int:pk>/complete/', CompleteProjectView.as_view(), name='complete-project'),
    path('my-projects/', MyProjectsView.as_view(), name='my-projects'),
    path('my-bids/', MyBidsView.as_view(), name='my-bids'),

]