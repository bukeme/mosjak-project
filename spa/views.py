from django.shortcuts import render, redirect
from django.views import View
from django.views import generic
from django.contrib.auth.models import User
from django.views.generic.base import TemplateResponseMixin
from django.contrib import messages
from django.contrib import auth
from allauth.account.views import SignupView
from .forms import LoginForm

from .forms import UserRegistrationForm, StudentForm, UserForm, ProjectForm
from .mixins import RedirectLoggedInUser
from .models import Student, Project

# Create your views here.

class StudentRegistrationView(RedirectLoggedInUser, generic.TemplateView):
	template_name = 'account/signup.html'
	def get(self, request, *args, **kwargs):
		# Pass User Registration Form and Student Form
		u_form = UserRegistrationForm()
		s_form = StudentForm()
		context = {
			'u_form': u_form,
			's_form': s_form,
		}
		return self.render_to_response(context)

	def post(self, request, *args, **kwargs):
		# Get User Data From The Form
		u_form = UserRegistrationForm(request.POST)
		s_form = StudentForm(request.POST)
		if u_form.is_valid() and s_form.is_valid(): # If The Two Form Input Are Valid
			# Save The Two Forms And Redirect User To Login
			u_form.save(request)
			u_email = u_form.cleaned_data['email']
			user = User.objects.get(email=u_email)
			s_form = s_form.save(commit=False)
			s_form.user = user 
			s_form.save()
			messages.success(request, "Your Account Has Been Created. You Can Now Login")
			return redirect('account_login')
		# If Not Valid Render Sign Up Page With Form And Error
		context = {
			'u_form': u_form,
			's_form': s_form,
		}
		return self.render_to_response(context)

student_registration = StudentRegistrationView.as_view()

class LoginView(RedirectLoggedInUser, generic.TemplateView):
	template_name = 'account/login.html'
	def get(self, request, *args, **kwargs):
		# Pass Login Form
		form = LoginForm()
		return self.render_to_response({'form': form})

	def post(self, request, *args, **kwargs):
		# Get User Data From The Form
		form = LoginForm(request.POST)
		if form.is_valid(): # Form is valid
			data = form.cleaned_data
			email = data['email']
			if User.objects.filter(email=email).exists(): # Check if user with email exists
				username = User.objects.get(email=email).username
			else:
				messages.error(request, 'Email doesn\'t exist')
				return self.render_to_response({'form': form})
			password = data['password']
			# Authenticate user
			user = auth.authenticate(username=username, password=password)
			if user is not None: # Checks if user exist
				auth.login(request, user)
				if user.is_staff:
					return redirect('admin_dashboard')
				return redirect('student_dashboard')
		messages.error(request, "Incorrect password")
		return self.render_to_response({'form': form})

login = LoginView.as_view()


class StudentDashboardView(generic.TemplateView):
	template_name = 'spa/student-dashboard.html'

	def post(self, request, *args, **kwargs):
		# Save Updates
		u_form = UserForm(request.POST, instance=request.user)
		s_form = StudentForm(request.POST, instance=request.user.student)
		if u_form.is_valid():
			u_form.save()
			s_form.save()
			return redirect('student_dashboard')
		return self.render_to_response({"u_form": u_form, 's_form': s_form})


	def get_context_data(self, *args, **kwargs):
		# Pass Forms 
		context = super().get_context_data(*args, **kwargs)
		context['u_form'] = UserForm()
		context['s_form'] = StudentForm()
		context['p_form'] = ProjectForm()
		return context

student_dashboard = StudentDashboardView.as_view()

class AdminDashboardView(generic.TemplateView):
	template_name = 'spa/admin-dashboard.html'

	def post(self, request, *args, **kwargs):
		# Save Updates
		u_form = UserForm(request.POST, instance=request.user)
		if u_form.is_valid():
			u_form.save()
			return redirect('admin_dashboard')
		return self.render_to_response({'u_form': u_form})

	def get_context_data(self, *args, **kwargs):
		# Pass Forms
		context = super().get_context_data(*args, **kwargs)
		context['u_form'] = UserForm()
		return context

admin_dashboard = AdminDashboardView.as_view()

def project_post_action(self, request):
	# Get Data
		form = ProjectForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			title = data['title']
			case_study = data['case_study']
			
			title_exist = Project.objects.filter(title=title).exists()
			case_study_exist = Project.objects.filter(case_study=case_study).exists()
			# If project exists, flag user
			if title_exist or case_study_exist:
				messages.error(request, 'This Project Has Been Allocated')
				return self.render_to_response({'form': form})
			# If group members are added
			try:
				students = request.POST.get('students')
				for student_id in students:
					student = Student.objects.get(pk=int(student_id))
					if student.project is not None:
						# If one of the group members is in a project
						messages.error(request, 'Project Has Already Been Allocated To One Of The Group Members')
						return self.render_to_response({'form': form})
			except:
				pass
			# Save project and associate it with user
			form.save()
			project = Project.objects.get(title=title)
			request.user.student.project = project
			request.user.student.save()
			try:
				for student_id in students:
					# Associate group members to project
					student = Student.objects.get(pk=int(student_id))
					student.project = project
					student.save()
			except:
				pass
			return redirect('student_dashboard')
		return self.render_to_response({'form': form})

class RegisterProjectView(generic.TemplateView):
	template_name = 'spa/register-project.html'

	def post(self, request, *args, **kwargs):
		return project_post_action(self, request)
			

	def get_context_data(self, *args, **kwargs):
		# Pass Forms
		context = super().get_context_data(*args, **kwargs)
		context['form'] = ProjectForm()
		context['students'] = Student.objects.exclude(user=self.request.user)
		return context 

register_project = RegisterProjectView.as_view()

class ProjectDetailView(generic.TemplateView):
	template_name = 'spa/project-detail.html'

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		project = Project.objects.get(pk=kwargs['pk'])
		context['project'] = project
		context['form'] = ProjectForm(instance=project)
		context['students'] = Student.objects.all()
		return context

project_detail = ProjectDetailView.as_view()

class ProjectUpdateview(generic.TemplateView):
	template_name = 'spa/project-update.html'

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		project = Project.objects.get(pk=kwargs['pk'])
		context['project'] = project
		context['form'] = ProjectForm()
		context['students'] = Student.objects.all()
		return context

project_update = ProjectUpdateview.as_view()

