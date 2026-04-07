from django.urls import path
from .views import *

urlpatterns=[
    path('category/',category,name='category'),
    path('chatbox/',process_of_chatbox,name='chatbox'),
    path('doctors/',get_doctors,name='doctors'),
    path('department/',get_departments,name='department')
    
]
