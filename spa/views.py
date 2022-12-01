from django.shortcuts import render, redirect
from django.views import View
from django.views import generic
from django.contrib.auth.models import User
from django.views.generic.base import TemplateResponseMixin
from django.contrib import messages
from django.contrib import auth
from allauth.account.views import SignupView
from .forms import LoginForm

from .forms import UserRegistrationForm, StudentForm, UserForm
from .mixins import RedirectLoggedInUser

# Create your views here.

class StudentRegistrationView(RedirectLoggedInUser, generic.TemplateView):
	template_name = 'account/signup.html'
	def get(self, request, *args, **kwargs):
		u_form = UserRegistrationForm()
		s_form = StudentForm()
		context = {
			'u_form': u_form,
			's_form': s_form,
		}
		return self.render_to_response(context)

	def post(self, request, *args, **kwargs):
		u_form = UserRegistrationForm(request.POST)
		s_form = StudentForm(request.POST)
		if u_form.is_valid() and s_form.is_valid():
			u_form.save(request)
			u_email = u_form.cleaned_data['email']
			user = User.objects.get(email=u_email)
			s_form = s_form.save(commit=False)
			s_form.user = user 
			s_form.save()
			messages.success(request, "Your Account Has Been Created. You Can Now Login")
			return redirect('account_login')
		context = {
			'u_form': u_form,
			's_form': s_form,
		}
		return self.render_to_response(context)

student_registration = StudentRegistrationView.as_view()

class LoginView(generic.TemplateView):
	template_name = 'account/login.html'
	def get(self, request, *args, **kwargs):
		form = LoginForm()
		return self.render_to_response({'form': form})

	def post(self, request, *args, **kwargs):
		form = LoginForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			email = data['email']
			if User.objects.filter(email=email).exists():
				username = User.objects.get(email=email).username
			else:
				messages.error(request, 'Email doesn\'t exist')
				return self.render_to_response({'form': form})
			password = data['password']
			user = auth.authenticate(username=username, password=password)
			if user is not None:
				auth.login(request, user)
				return redirect('dashboard')
		messages.error(request, "Incorrect password")
		print('hello')
		return self.render_to_response({'form': form})

login = LoginView.as_view()


class DashboardView(generic.TemplateView):
	template_name = 'spa/dashboard.html'

	def post(self, request, *args, **kwargs):
		u_form = UserForm(request.POST, instance=request.user)
		print(u_form)
		# s_form = StudentForm(request.POST, initial=request.user)
		if u_form.is_valid():
			u_form.save()
			# s_form.save()
			return redirect('dashboard')
		return self.render_to_response({"u_form": u_form,})


	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		print(self.request.user)
		context['u_form'] = UserForm()
		context['s_form'] = StudentForm()
		return context

dashboard = DashboardView.as_view()



