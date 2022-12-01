from django.urls import path, include
import allauth.account
from . import views

urlpatterns = [
	path('accounts/signup/', views.student_registration, name='account_signup'),
	path('accounts/login/', views.login, name='account_login'),
	# path('accounts/login/', allauth.account.views.LoginView.as_view(), name='account_login'),
	path('accounts/', include('allauth.account.urls')),
	path('', views.dashboard, name='dashboard'),
]