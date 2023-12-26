from rest_framework import generics, permissions
from .models import notice, subject,exam,result
from .serializers import NoticeSerializer,SubjectSerializer,ExamSerializer,ResultSerializer
from .permissions import IsHeadUser,IsHeadAndTeacherUser


# notice part
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
   
 
##subjects part
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
    
    
## exam part

class ExamCreateView(generics.CreateAPIView):
    queryset = exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsHeadUser]

class ExamUpdateView(generics.UpdateAPIView):
    queryset = exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsHeadUser]

class ExamDeleteView(generics.DestroyAPIView):
    queryset = exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsHeadUser]
    
    
    
##Result part


    

class ResultCreateView(generics.CreateAPIView):
    queryset = result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsHeadAndTeacherUser]
    

class ResultUpdateView(generics.UpdateAPIView):
    queryset = result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsHeadAndTeacherUser]
    

class ResultDeleteView(generics.DestroyAPIView):
    queryset = result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsHeadAndTeacherUser]
    

class ResultRetrieveView(generics.RetrieveAPIView):
    queryset = result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsHeadAndTeacherUser]
    





