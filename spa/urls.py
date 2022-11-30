from django.urls import path
from . import views

urlpatterns = [
	path('signup/', views.student_registration, name='sign_up'),
]