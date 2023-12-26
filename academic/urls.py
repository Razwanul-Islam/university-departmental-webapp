# urls.py
from django.urls import path
from .views import NoticeListCreateView, NoticeRetrieveUpdateDeleteView,SubjectCreateView, SubjectUpdateView, SubjectDeleteView,ExamCreateView, ExamUpdateView, ExamDeleteView,ResultRetrieveView, ResultCreateView, ResultUpdateView, ResultDeleteView


urlpatterns = [
    #any one will perform to see notice
    path('notices/', NoticeListCreateView.as_view(), name='notice-list-create'),
    #only head are able to perform notice create,update and delete
    path('notices/<int:pk>/', NoticeRetrieveUpdateDeleteView.as_view(), name='notice-retrieve-update-delete'),
    
    #Only head will be able to perform subject create,update and delete
    path('subjects/create/', SubjectCreateView.as_view(), name='subject-create'),
    path('subjects/update/<int:subject_id>/', SubjectUpdateView.as_view(), name='subject-update'),
    path('subjects/delete/<int:subject_id>/', SubjectDeleteView.as_view(), name='subject-delete'),
    
    #Only head will be able to perform exam create,update and delete
    path('exam/create/', ExamCreateView.as_view(), name='exam-create'),
    path('exam/update/<int:pk>/', ExamUpdateView.as_view(), name='exam-update'),
    path('exam/delete/<int:pk>/', ExamDeleteView.as_view(), name='exam-delete'),
    
    
    ###Only Head and Teacher are able to perform result create update and delete 
    
    path('result/create/', ResultCreateView.as_view(), name='result-create'),
    path('result/update/<int:pk>/', ResultUpdateView.as_view(), name='result-update'),
    path('result/delete/<int:pk>/', ResultDeleteView.as_view(), name='result-delete'),
    
    
    ## ###Any one can be view or retrieve result
    path('result/<int:pk>/', ResultRetrieveView.as_view(), name='result-retrieve'),
]
