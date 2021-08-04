from django.urls import path, include
from .views import PollAuth, PollUnAuth, CreateUser, VerifEmail

urlpatterns = [
    path('polls/<str:info>/<str:params>',PollUnAuth.as_view()),
    path('polls/<str:params>',PollAuth.as_view()),
    path('user/create',CreateUser.as_view()),
    path('user/verif',VerifEmail.as_view()),
    
]