# urls.py
from django.urls import path
from .views import NoticeListCreateView, NoticeRetrieveUpdateDeleteView,SubjectCreateView, SubjectUpdateView, SubjectDeleteView

urlpatterns = [
    #any one will perform to see notice
    path('notices/', NoticeListCreateView.as_view(), name='notice-list-create'),
    #only head are able to perform notice create,update and delete
    path('notices/<int:pk>/', NoticeRetrieveUpdateDeleteView.as_view(), name='notice-retrieve-update-delete'),
    
    #Onnly head will be able to perform subject create,update and delete
    path('subjects/create/', SubjectCreateView.as_view(), name='subject-create'),
    path('subjects/update/<int:subject_id>/', SubjectUpdateView.as_view(), name='subject-update'),
    path('subjects/delete/<int:subject_id>/', SubjectDeleteView.as_view(), name='subject-delete'),
]
