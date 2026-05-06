from django.shortcuts import render

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, Event, Registration
from .serializers import RegisterSerializer, UserSerializer, EventSerializer, RegistrationSerializer


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


# AUTH
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


# EVENTS
class EventListView(generics.ListAPIView):
    queryset = Event.objects.filter(status='upcoming').order_by('date')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]


class EventCreateView(generics.CreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAdminRole]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminRole]


# REGISTRATIONS
class RegisterForEventView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        event_id = request.data.get('event_id')

        if Registration.objects.filter(student=request.user, event_id=event_id).exists():
            return Response({'detail': 'You are already registered for this event.'}, status=400)

        event = Event.objects.get(pk=event_id)
        if event.slots_remaining <= 0:
            return Response({'detail': 'This event is already full.'}, status=400)

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class MyRegistrationsView(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(student=self.request.user)


class CancelRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            registration = Registration.objects.get(pk=pk, student=request.user)
            registration.status = 'cancelled'
            registration.save()
            return Response({'detail': 'Registration cancelled.'})
        except Registration.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=404)


# ADMIN REPORT
class AttendanceReportView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
        except Event.DoesNotExist:
            return Response({'detail': 'Event not found.'}, status=404)

        registrations = Registration.objects.filter(event=event, status='confirmed')
        serializer = RegistrationSerializer(registrations, many=True)
        return Response({
            'event': event.title,
            'date': str(event.date),
            'total_registered': registrations.count(),
            'capacity': event.capacity,
            'slots_remaining': event.slots_remaining,
            'attendees': serializer.data,
        })


# ─────────────────────────────────────────────
# LAB ACTIVITY 07 - SIMPLE VIEWS FOR POSTMAN TESTING
# No authentication required
# ─────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([AllowAny])
def get_events(request):
    # DFD: Fetch Events
    events = Event.objects.filter(status='upcoming')
    data = [
        {
            "id": e.id,
            "title": e.title,
            "description": e.description,
            "date": str(e.date),
            "time": str(e.time),
            "location": e.location,
            "capacity": e.capacity
        }
        for e in events
    ]
    return Response({"status": "success", "data": data})


@api_view(['POST'])
@permission_classes([AllowAny])
def register_event(request):
    user_id = request.data.get('user_id')
    event_id = request.data.get('event_id')

    # DFD: Validate
    if not user_id or not event_id:
        return Response({"status": "error", "message": "Missing data"})

    # DFD: Process
    try:
        user = User.objects.get(id=user_id)
        event = Event.objects.get(id=event_id)
    except:
        return Response({"status": "error", "message": "Invalid user/event"})

    # DFD: Save
    Registration.objects.create(user=user, event=event)

    return Response({
        "status": "success",
        "message": "Registered successfully"
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def create_event(request):
    title = request.data.get('title')
    description = request.data.get('description')
    location = request.data.get('location')
    date = request.data.get('date')
    time = request.data.get('time')
    capacity = request.data.get('capacity')

    # DFD: Validate
    if not title:
        return Response({"status": "error", "message": "Title is required"})

    # DFD: Save
    event = Event.objects.create(
        title=title,
        description=description,
        location=location,
        date=date,
        time=time,
        capacity=capacity
    )

    return Response({
        "status": "success",
        "message": "Event created successfully",
        "event_id": event.id
    })