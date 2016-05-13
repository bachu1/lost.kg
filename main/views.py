#importings
from django.shortcuts import render_to_response, redirect, get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Cardstick, Mail, Item, Category
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import re
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse , reverse_lazy
#impoer of models 

def main(request):
	#initialize variables
	args={}
	args.update(csrf(request))
	return render(request, 'main/main.html',args)
	
@login_required(login_url=reverse_lazy('main:signin'))
def report(request):
	#initialize variables
	args={}
	args.update(csrf(request))
	if request.POST:
		title = request.POST.get('title', '')
		description = request.POST.get('description', '')
		contacts = request.POST.get('contacts', '')
		award = request.POST.get('award', '')
		category_id = request.POST.get('category', '')
		operation = request.POST.get('operation')
		category = Category.objects.get(id=category_id)
		item = Item.objects.create(user=request.user, title=title, description=description, contacts=contacts, category=category)
		if operation == 'lost':
			item.award = award
		else:
			item.is_lost = False
		item.save()
		return redirect(reverse('main:profile'))

	else:
		args['categories'] = Category.objects.all()
		args['operation'] = request.GET.get('operation','')

		return render(request, 'main/report.html', args)


def message(request):
	#initialize variables
	args={}
	args.update(csrf(request))
	if request.POST:
		name = request.POST['name']
		email = request.POST['email']
		subject = request.POST['subject']
		message = request.POST['message']
		mail = Mail.objects.create(name=name,email=email,title=subject,body=message)
		mail.save()
	return redirect(reverse('main:main'))

def signin(request):
	# redirect to main page authorized users
	if request.user.is_authenticated():
		return redirect(reverse("main:main"))
	# initialize variables
	args={}
	args.update(csrf(request))

	if request.POST:
		username = request.POST['username']
		password = request.POST['password']

		user = authenticate(username=username, password=password)

		if user is not None:
			if user.is_active:
				login(request, user)
				return redirect(reverse('main:main'))
		else:
			args['error_message'] = "Имя пользователя и пароль не совпадают, попробуйте еще раз. "
			return render(request, 'main/signin.html', args)
	else:
		next_lingk = request.GET.get('next','')
		if next_lingk != '':
			args['message'] = 'Для того что бы совершить данное действие вам нужно войти в систему.'

		return render(request, 'main/signin.html', args)

@login_required(login_url=reverse_lazy('main:main'))
def signout(request):

	logout(request)
	return redirect(request.META.get('HTTP_REFERER'))

def signup(request):
	# redirect not authenticated users to main page
	if request.user.is_authenticated():
		return redirect(reverse("main:main"))
	# initialize variables
	args={}
	args.update(csrf(request))
	validation = True
	# Query objects from model
	all_users = User.objects.all()

	if request.POST:
		first_name = request.POST.get('first_name', '')
		email = request.POST.get('e_mail', '')
		password = request.POST.get('password', '')
		username = email

		# email validation
		users_using_email = all_users.filter(email=email)

		if not re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", email):
			validation = False
			args['email_error'] = 'Неправильно введен email'
		else:
		    if users_using_email.count() > 0:
			    validation = False
			    args['email_error'] = 'Этот email уже зарегистрирован'
			    args['email'] = email
			    args['first_name'] = first_name
		if validation == False:
			return render(request, 'main/signup.html', args)
		else:
			user = User.objects.create_user(username=username, email=email, password=password)
			user.first_name = first_name
			user.save()
			user = authenticate(username=username, password=password)
			login(request, user)
			return redirect(reverse('main:main'))
	else:
		return render(request, 'main/signup.html', args)

@login_required(login_url=reverse_lazy('main:signin'))
def profile(request):
	args={}
	args.update(csrf(request))
	args['items'] = Item.objects.filter(user=request.user)
	return render(request, 'main/profile.html', args)

def item(request, item_id):
	args = {}
	args['item'] = get_object_or_404(Item, id=item_id)
	return render(request, 'main/item.html', args)

def delete_item(request, item_id):
	item = get_object_or_404(Item, id=item_id)
	if item.user.username == request.user.username:
		item.delete()
	return redirect(reverse('main:profile'))

def item_list(request):
	args = {}
	items = Item.objects.all()
	this_category = request.GET.get('category', '')
	if this_category != '':
		category = Category.objects.filter(title=this_category)
		if category.count() > 0:
			items = items.filter(category=category[0])
	items_lost = items.filter(is_lost=True)
	items_found = items.filter(is_lost=False)
	args['categories'] = Category.objects.all()
	args['this_category'] = this_category
	args['items_lost'] = items_lost
	args['items_found'] = items_found
	return render(request, 'main/item_list.html', args)