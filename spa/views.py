from django.shortcuts import render, redirect
from django.views import View
from django.views import generic
from django.views.generic.base import TemplateResponseMixin

from .forms import UserForm, StudentForm

# Create your views here.

class StudentRegistrationView(generic.TemplateView):
	template_name = 'registration/account_signup.html'
	def get(self, request, *args, **kwargs):
		u_form = UserForm()
		s_form = StudentForm()
		context = {
			'u_form': u_form,
			's_form': s_form,
		}
		return self.render_to_response(context)

	def post(self, request, *args, **kwargs):
		u_form = UserForm(request.POST)
		if u_form.is_valid():
			u_form.save(request)
			return redirect('sign_up')
		s_form = StudentForm()
		context = {
			'u_form': u_form,
			's_form': s_form,
		}
		return self.render_to_response(context)

student_registration = StudentRegistrationView.as_view()



