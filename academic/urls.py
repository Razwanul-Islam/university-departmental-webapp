# urls.py
from django.urls import path
from .views import NoticeListCreateView, NoticeRetrieveUpdateDeleteView

urlpatterns = [
    #any one will perform to see notice
    path('notices/', NoticeListCreateView.as_view(), name='notice-list-create'),
    #only head are able to perform notice create,update and delete
    path('notices/<int:pk>/', NoticeRetrieveUpdateDeleteView.as_view(), name='notice-retrieve-update-delete'),
]
