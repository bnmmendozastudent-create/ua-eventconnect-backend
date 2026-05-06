from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.RegisterView.as_view()),
    path('auth/login/', TokenObtainPairView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),

    # Class-based (JWT protected)
    path('events/', views.EventListView.as_view()),
    path('admin/events/', views.EventCreateView.as_view()),
    path('admin/events/<int:pk>/', views.EventDetailView.as_view()),
    path('admin/events/<int:event_id>/report/', views.AttendanceReportView.as_view()),
    path('registrations/', views.RegisterForEventView.as_view()),
    path('registrations/my/', views.MyRegistrationsView.as_view()),
    path('registrations/<int:pk>/cancel/', views.CancelRegistrationView.as_view()),

    # Function-based (No auth - for Postman testing / Lab Activity 07)
    path('lab/events/', views.get_events),
    path('lab/registrations/', views.register_event),
    path('lab/admin/events/', views.create_event),
]