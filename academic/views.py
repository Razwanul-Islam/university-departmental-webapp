from rest_framework import generics, permissions
from .models import notice, subject
from .serializers import NoticeSerializer,SubjectSerializer
from .permissions import IsHeadUser

class NoticeListCreateView(generics.ListCreateAPIView):
    queryset = notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [IsHeadUser]

    def perform_create(self, serializer):
        # Set the user_id to the current authenticated user
        serializer.save(user_id=self.request.user)

class NoticeRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [IsHeadUser]
    

class SubjectCreateView(generics.CreateAPIView):
    queryset = subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsHeadUser]

class SubjectUpdateView(generics.UpdateAPIView):
    queryset = subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsHeadUser]
    lookup_field = 'subject_id'

class SubjectDeleteView(generics.DestroyAPIView):
    queryset = subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsHeadUser]
    lookup_field = 'subject_id'

