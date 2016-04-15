from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.db import IntegrityError,connection
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from .models import User_profile,Police,Address,Civilian,Criminal_Record
from .forms import User_profile_form,Police_form,Address_form,Civilian_form,Criminal_Record_form
from django.contrib import messages
from django.contrib.messages import get_messages

def index(request):
	return redirect('police.views.loginpage')

def signuppage(request):
	if request.user.is_authenticated():
		return redirect('/u/fill_details')

	if request.method == 'POST':
		try:
			username=password=lastname=firstname=''	
			email     = request.POST.get('email')
			firstname = request.POST.get('firstname')
			lastname  = request.POST.get('lastname')
			username  = request.POST.get('username')
			password  = request.POST.get('password')
			user=User.objects.create_user(username,email,password)
			user.first_name=firstname
			user.last_name=lastname
			user.save()
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request,user)
			status='done'
		except IntegrityError:
			status = 'user already exists'
			return render(request,'police/signup.html',{'status':status})
		else:
			status = 'new user was created'
		return redirect('/u/fill_details')
	else:
		return render(request,'police/signup.html')

def signup_detail(request):
	if request.user.is_authenticated():
		if User_profile.objects.filter(user=request.user).exists():
			if User_profile.objects.get(user=request.user).isPolice==1:
				return redirect('/u/police/'+request.user.username)
			else:
				return redirect('/u/civilian/'+request.user.username)
		if request.method == 'POST':
			if request.POST.get('police')=="police":
				form=User_profile_form(request.POST)
				if form.is_valid():
					temp=form.save(commit=False)
					temp.user=request.user
					temp.gender=request.POST.get('gender')
					temp.isPolice=1
					temp.save()
					return redirect('/u/police/'+request.user.username)
				else:
					error="fill in the details properly"
					return redirect('/u/fill_details',{'error':error})
			else:
				form=User_profile_form(request.POST)
				if form.is_valid():
					temp=form.save(commit=False)
					temp.user=request.user
					temp.isPolice=0
					temp.gender=request.POST.get('gender')
					temp.save()
					return redirect('/u/civilian/'+request.user.username)
				else:
					error="fill in the details properly"
					return redirect('/u/fill_details',{'error':error})
		else:
			form=User_profile_form()
			return render(request,'police/signup_detail.html',{'form':form})
	else:
		return redirect('/u/login')

def welcomepolice(request,username):
	if not request.user.is_authenticated():
		messages.error(request, 'you need to login '+username)
		return redirect('/u/login')
	if username != request.user.username:
		logout(request)
		messages.error(request, 'login with username '+username)
		return redirect('/u/login')
	if User_profile.objects.get(user=request.user).isPolice==0:
		logout(request)
		messages.error(request, 'you are a civilian and you cannot view a policeman\'s account')
		return redirect('/u/login')
	if request.method=='POST' and request.POST.get('civilian')=="civilian":
		get_user_name=request.POST.get('username')
		requested_user=User.objects.filter(username=get_user_name)
		if requested_user.exists():
			query=User_profile.objects.filter(user=requested_user[0])
			if query.exists() and query[0].isPolice==0:
				return redirect('/u/detail/civilian/'+get_user_name)
		messages.error(request, 'no user with the '+get_user_name+' was found')
		return redirect('/u/police/'+username)

	if request.method=='POST' and request.POST.get('police')=="police":
		get_user_name=request.POST.get('username')
		requested_user=User.objects.filter(username=get_user_name)
		if requested_user.exists():
			query=User_profile.objects.filter(user=requested_user[0])
			if query.exists() and query[0].isPolice==1:
				policeman=Police.objects.filter(user=requested_user[0])
				if not policeman.exists():
					messages.error(request,'the user\'s details are not yet filled up')
					return redirect('/u/police/'+username)
				curr_police=Police.objects.filter(user=request.user)
				if curr_police.exists():
					if policeman[0].rank >= curr_police[0].rank:
						return redirect('/u/detail/police/'+get_user_name)
					else:
						messages.error(request,'you cannot view your senior\'s account')
						return redirect('/u/police/'+username)
				else:
					messages.error(request,'fill up your details first')
					return redirect('/u/police/'+username)
		messages.error(request, 'no police with the username '+get_user_name+' was found')
		return redirect('/u/police/'+username)
	else:
		curr_user=User_profile.objects.get(user=request.user)
		return render(request,'police/welcome_police.html',{'user':request.user,'curr_user':curr_user})

def editpolice(request,username):
	if not request.user.is_authenticated():
		messages.error(request, 'you need to login '+username)
		return redirect('/u/login')
	if username != request.user.username:
		logout(request)
		messages.error(request, 'login with username '+username)
		return redirect('/u/login')
	if User_profile.objects.get(user=request.user).isPolice==0:
		logout(request)
		messages.error(request, 'you are a civilian and you cannot edit a policeman\'s account')
		return redirect('/u/login')
	if request.method == 'POST':
		form1=Police_form(request.POST)
		form2=Address_form(request.POST)
		if form1.is_valid() and form2.is_valid():
			post1=form1.save(commit=False)
			post1.user=request.user
			temp=request.POST.get('post_police')
			post1.post=temp

			rank=0
			if temp=="Commissioner":
				rank=1
			elif temp=="Joint Commissioner":
				rank=2
			elif temp=="Deputy Commissioner":
				rank=3
			elif temp=="Assistant Superintendent":
				rank=4
			elif temp=="Inspector":
				rank=5
			elif temp=="Assistant Inspector":
				rank=6
			elif temp=="Sub-Inspector":
				rank=7
			else:
				rank=8

			post1.rank=rank
			post1.save()
			post2=form2.save(commit=False)
			post2.user=request.user
			post2.save()
			messages.error(request, "changes have been saved sucessfully")
			return redirect('/u/police/'+request.user.username)
		else:
			error='fill in the details properly'
			return render('police/editpolice.html',{'error':error})
	else:
		if Police.objects.filter(user=request.user).exists() and Address.objects.filter(user=request.user).exists():
			address=Address.objects.get(user=request.user)
			details=Police.objects.get(user=request.user)
			post=details.post
			return render(request,'police/editpolice.html',{'post':post,'details':details,'address':address,'user':request.user})
		else:
			form1=Police_form()
			form2=Address_form()
			return render(request,'police/editpolice.html',{'user':request.user})


def editcivilian(request,username):
	isCriminal=0
	if not request.user.is_authenticated():
		messages.error(request, 'you need to login '+username)
		return redirect('/u/login')
	if username != request.user.username:
		logout(request)
		messages.error(request, 'login with username '+username)
		return redirect('/u/login')
	if User_profile.objects.get(user=request.user).isPolice==1:
		logout(request)
		messages.error(request, 'you are a police and you cannot edit a civilian\'s account')
		return redirect('/u/login')
	if request.method == 'POST':
		form1=Civilian_form(request.POST)
		form2=Address_form(request.POST)
		if form1.is_valid() and form2.is_valid():
			post1=form1.save(commit=False)
			post1.user=request.user
			post1.isCriminal=isCriminal
			post1.save()
			post2=form2.save(commit=False)
			post2.user=request.user
			post2.save()
			messages.error(request, "changes have been saved sucessfully")
			return redirect('/u/civilian/'+request.user.username)
		else:
			error='fill in the details properly'
			return render('police/editcivilian.html',{'error':error})
	else:
		if Civilian.objects.filter(user=request.user).exists() and Address.objects.filter(user=request.user).exists():
			address=Address.objects.get(user=request.user)
			details=Civilian.objects.get(user=request.user)
			isCriminal=Civilian.objects.get(user=request.user).isCriminal
			return render(request,'police/editcivilian.html',{'isCriminal':isCriminal,'details':details,'address':address})
		else:
			form1=Civilian_form()
			form2=Address_form()
			return render(request,'police/editcivilian.html',{'isCriminal':isCriminal,'user':request.user})

def welcomecivilian(request,username):
	if not request.user.is_authenticated():
		messages.error(request, 'you need to login '+username)
		return redirect('/u/login')
	if username != request.user.username:
		logout(request)
		messages.error(request, 'login with username '+username)
		return redirect('/u/login')
	if User_profile.objects.get(user=request.user).isPolice==1:
		logout(request)
		messages.error(request, 'you are a policeman and you cannot view a civilian\'s details')
		return redirect('/u/login')
	curr_user=User_profile.objects.get(user=request.user)
	return render(request,'police/welcome_civilian.html',{'user':request.user,'curr_user':curr_user})

def loginpage(request):
	error="wrong credientials entered"
	if request.user.is_authenticated():
		return redirect('/u/fill_details')
	username=password=''
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user is not None and user.is_active:
			login(request,user)
			return redirect('/u/fill_details')
		else:
			return render(request,'police/login.html',{'error':error})
	else:
		return render(request,'police/login.html')

def logout_user(request):
	if request.user.is_authenticated():
		logout(request)
	return redirect('/u/login')

def civiliandatabase(request):
	if not request.user.is_authenticated():
		messages.error(request, 'you need to login first with a valid policeman account')
		return redirect('/u/login')
	if User_profile.objects.get(user=request.user).isPolice==0:
		logout(request)
		messages.error(request, 'you are a civilian and the information you requested is highly confidential which is only available to the police')
		return redirect('/u/login')
	else:
		civilianlist=User_profile.objects.filter(isPolice=0).order_by('age')
		return render(request,'police/civilianlist.html',{'result':civilianlist})

def criminaldatabase(request):
	if not request.user.is_authenticated():
		messages.error(request, 'you need to login first with a valid policeman account')
		return redirect('/u/login')
	if User_profile.objects.get(user=request.user).isPolice==0:
		logout(request)
		messages.error(request, 'you are a civilian and the information you requested is highly confidential which is only available to the police')
		return redirect('/u/login')
	else:
		criminallist=Civilian.objects.filter(isCriminal=1)
		return render(request,'police/criminallist.html',{'result':criminallist})

def civiliandetail(request,username):
	if not request.user.is_authenticated():
		messages.error(request, 'you need to login first with a valid policeman account')
		return redirect('/u/login')
	if User_profile.objects.get(user=request.user).isPolice==0:
		logout(request)
		messages.error(request, 'you are a civilian and the information you requested is highly confidential which is only available to the police')
		return redirect('/u/login')

	requested_user=User.objects.filter(username=username)
	userprofile=User_profile.objects.get(user=requested_user[0])
	query1=Civilian.objects.filter(user=requested_user[0])

	if requested_user.exists() and query1.exists() and userprofile.isPolice==0:
		address=Address.objects.get(user=requested_user[0])
		return render(request,'police/civiliandetail.html',{'civilian':query1[0],'address':address,'userprofile':userprofile,'user':requested_user[0]})
	else:
		messages.error(request, 'no such user found')
		return redirect('/u/police/'+request.user.username)

def policedetail(request,username):
	get_user_name=username
	requested_user=User.objects.filter(username=get_user_name)
	if requested_user.exists():
		query=User_profile.objects.filter(user=requested_user[0])
		if query.exists() and query[0].isPolice==1:
			police=Police.objects.filter(user=requested_user[0])
			if not police.exists():
				messages.error(request,'the user\'s details are not yet filled up')
				return redirect('/u/police/'+request.user.username)
			curr_police=Police.objects.filter(user=request.user)
			if curr_police.exists():
				if police[0].rank >= curr_police[0].rank:
					user=User.objects.filter(username=username)
					address=Address.objects.filter(user=user)
					return render(request,'police/policedetail.html',{'user':user[0],'address':address[0],'userprofile':query[0],'police':police[0]})
				else:
					messages.error(request,'you cannot view your senior\'s account')
					return redirect('/u/police/'+request.user.username)
			else:
				messages.error(request,'fill up your details first')
				return redirect('/u/police/'+request.user.username)
	messages.error(request, 'no police with the username '+get_user_name+' was found')
	return redirect('/u/police/'+request.user.username)

		