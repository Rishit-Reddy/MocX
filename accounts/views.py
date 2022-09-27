from django.http.response import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser, User, auth
from .models import IntervieweeProfile, InterviewerProfile
from django.template import *
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .forms import InterviewerForm, UserEditForm
import scheduling.views
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import activation_token_generator
from django.contrib.auth import get_user_model

User = get_user_model()# so Django won't throw "Manager isn't available; User has been swapped"

@login_required # does not redirect to this, for some reason? wonder why? path: directly /settings/edit_profile -> login -> redirects to profile.
def edit_profile(request):
    if request.method == 'POST':
        
        form_interviewer_profile = InterviewerForm(request.POST, request.FILES, instance=request.user.interviewerprofile)
        form_user_profile = UserEditForm(request.POST, request.FILES, instance=request.user)

        if form_interviewer_profile.is_valid() and form_user_profile.is_valid(): 
            form_interviewer_profile.save()
            form_user_profile.save() 
            messages.info(request, "Successfully updated profile info") # how to make these look nice?
            return redirect(f'/{ request.user.username }')
    else: 
        form_interviewer_profile = InterviewerForm(instance=request.user.interviewerprofile)
        form_user_profile = UserEditForm(instance=request.user)
    return render(request, 'edit_profile.html', {'form_er' : form_interviewer_profile, 'form_user' : form_user_profile})  

@login_required
def edit_user_profile(request):
    if request.method == 'POST':
        form_user_profile = UserEditForm(request.POST, request.FILES, instance=request.user)

        if form_user_profile.is_valid(): 
            form_user_profile.save() 
            messages.info(request, "Successfully updated profile info") # how to make these look nice?
            return redirect(f'/{ request.user.username }')
    else: 
        form_user_profile = UserEditForm(instance=request.user)
    return render(request, 'edit_user_profile.html', {'form' : form_user_profile})

from django.utils import timezone

# handles access to a user's profile
def profile_user(request, username):
    user_requested = get_object_or_404(User, username=username) # will this slow down?

    if not request.user.is_authenticated: # redirect not logged in users to login, redirect to page later?
        return redirect('/login')
    elif user_requested.username != request.user.username and not user_requested.is_interviewer:
        if request.user.is_interviewer:
            return redirect(f'/{user_requested.username}')
        return redirect('/')
    elif user_requested.is_interviewer and request.user.is_interviewee and request.user.is_authenticated and request.method == 'POST': # do scheduling
      request, scheduling.views.add_schedule(request, user_requested)
      return redirect(f'/{user_requested.username}/') # this works well for now!
    
    # content to be used in the template
    content = {
        "user_requested": user_requested,
    }

    if user_requested.is_interviewer and not user_requested.is_interviewee: # get all the time slots of the interviewer
        time_slots = InterviewerProfile.objects.get(pk=user_requested.pk).time_slot.all()
        
        
        # auto remove, 5 minutes before-hand
        empty_time_slots = time_slots.filter(status="E").order_by('start_datetime') 
        
        # change to local time, and use that, as below:
        timezone.activate(user_requested.user_timezone) # USE INTERVIEWER'S TIMEZONE

        for empty_time_slot in empty_time_slots: # auto remove all empty_slots that have "expired"
            now = timezone.localtime(timezone=timezone.get_current_timezone())
            timeslottime = timezone.localtime(empty_time_slot.start_datetime, timezone.get_current_timezone())
            
            if empty_time_slot.start_datetime < now:
                empty_time_slot.change_to_declined()
                empty_time_slot.delete()
            
        empty_time_slots = time_slots.filter(status="E").order_by('start_datetime') # dislike all this fetching, but this'll do for now
        timezone.deactivate()
        # hope this doesn't slow stuff down
        # filtering out each time_slot by status
        content['empty_slots'] = empty_time_slots # what kinda object is this? a dictonary? 
        content['tentative_slots'] = time_slots.filter(status="T").order_by('start_datetime')
        content['confirmed_slots'] = time_slots.filter(status="C").order_by('start_datetime')
        content['declined_slots'] = time_slots.filter(status="D").order_by('start_datetime')    

        for decline_time_slot in content['declined_slots']: # THIS IS BECAUSE I THOUGHT DECLINED SLOTS WOULD ACTUALLY BE USEFUL
            decline_time_slot.delete()
        
    elif user_requested.is_interviewee and not user_requested.is_interviewer: # get all the interviewee's schedules as well
        time_slots = IntervieweeProfile.objects.get(pk=user_requested.pk).interviewee_id.all()
        # hope this doesn't slow stuff down
        content['tentative_slots'] = time_slots.filter(status="T").order_by('interviewer_slot__start_datetime')
        content['confirmed_slots'] = time_slots.filter(status="C").order_by('interviewer_slot__start_datetime')
        content['declined_slots'] = time_slots.filter(status="D").order_by('interviewer_slot__start_datetime')
    
    
    return render(request, 'profile_page.html', context=content)
    

def login_register(request):
    if request.user.is_authenticated: # you're already logged in. logout before signing in --> message
        return redirect(f'/{request.user.username}')
    return render(request,'login.html')

def user_login(request):
    if request.user.is_authenticated: # you're already logged in --> message
        return redirect(f'/{request.user.username}')
    
    if request.method == 'POST':
        email_id = request.POST.get('email_id')
        password = request.POST.get('password')
        user = auth.authenticate(username=email_id,password=password)

        if user is None:
            messages.info(request,'Invalid Credentials')
            # print('invalid')
            if 'next' in request.POST:
                if request.POST.get('next') == "/settings/edit_profile":
                    return redirect(request.POST.get('next'))
                    
            return render(request,'login.html')
        else:
            auth.login(request,user)
            
            if 'next' in request.POST:
                if request.POST.get('next') == "/settings/edit_profile":
                    return redirect(request.POST.get('next'))
            
            if user.is_interviewer and not user.is_interviewee:
                return redirect(f'/{user.username}')
            return redirect('/')


    else: return render(request,'login.html')

def interviewer_register(request): 
    if request.user.is_authenticated: # You're already logged in --> message
        return redirect(f'/{request.user.username}')
  
    if request.method == 'POST':
        email_id = request.POST.get('email_id')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        country_code = request.POST.get('country_code')
        mother_tongue = request.POST.get('language')
        ielts_band = request.POST.get('ielts_score')
        taken_ielts = request.POST.get('flexRadioDefault') # yes so pythonic
        experience = request.POST.get('experience')
        about_me = request.POST.get('about_me') #About ME???
        price = request.POST.get('price')        
        linkedin = request.POST.get('linkedin')
        

        if User.objects.filter(email=email_id).exists():
            messages.info(request,'Email already exists')
            return render(request,'examiner_registration.html')

        else:
            if password1 == password2:
                    user = User.objects.create_user(
                        username=email_id,
                        email=email_id,
                        password=password1,
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone_number,
                        country_code = country_code,
                        #Profile Picture??? # see that's why we use forms they provide us with allllll
                        is_registered = True,
                        is_interviewer = True)
                    
                    # why not use a form?
                    interviewer = InterviewerProfile.objects.get(pk=user.pk) # get the related user


                    if taken_ielts == 'on':
                        interviewer.taken_ielts = True
                        interviewer.best_ielts_score = ielts_band
                    elif taken_ielts == 'no': 
                        interviewer.taken_ielts = False
                        interviewer.best_ielts_score = 0
                    
                    interviewer.training_exp = experience
                    interviewer.about_me = about_me #About ME???
                    interviewer.price = price
                    interviewer.linkedin_profile = linkedin
                    interviewer.mother_tongue = mother_tongue
                    interviewer.save() 

                    # login the user and redirect to home
                    user = auth.authenticate(username=email_id, password=password1)
                    auth.login(request, user)
                    return redirect(f'/{email_id}')
            else:
                #print("1")
                messages.error(request,'Passwords did not match')
                return render(request,'examiner_registration.html')        
    else: return render(request,'examiner_registration.html')


def interviewee_register(request):
    if request.user.is_authenticated: # You're already logged in --> message
      return redirect(f'/{request.user.username}')
  
    if request.method == 'POST':
        email_id = request.POST.get('email_id')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        #print(email_id,password1)

        if User.objects.filter(email=email_id).exists():
            messages.error(request,'Email Already Exists')
            return render(request,'Registration.html')

        else:
            if password1 == password2:
                    user = User.objects.create_user(username=email_id,email=email_id,password=password1,first_name=first_name,last_name=last_name,phone=phone_number,is_interviewee=True, is_registered = True)

              #       # send account registration email 
              #       uidb64 = urlsafe_base64_encode(force_bytes(user.pk)) # encode the user primary key

              #       domain = get_current_site(request).domain # gets the domain
              #       link = reverse('activation_user', kwargs={'uidb64' : uidb64, 'token' : activation_token_generator.make_token(user) }) 
              #       activate_url='https://'+domain+link # change to https, when done

              #       # can be a better message
              #       email_sub = "Account Activation for " + user.first_name
              #       email_bdy = f"Hello {user.username}! Thank you for registering. To use Mocx to its full potential, please use this link below for activating your new account:" + activate_url + "\n\nNot you? Please contact us."

              #       # the email to be sent
              #       email = EmailMessage(
              #           email_sub,
              #           email_bdy,
              #           'noreply@mocx.in',
              #           [email_id] # to email_id send to email after testing.
              #       )
                    
                    
              #       email1 = EmailMessage( # send one to ourselves as well when a new user registers
              #           email_sub,
              #           "has registered for an account, see subject",
              #           'noreply@mocx.in',
              #           ['headmocx09@gmail.com'] 
              #       )
                   
              #       email1.send(fail_silently=False)
              #       email.send(fail_silently=False)



                    # login the user and redirect to home   
                    user = auth.authenticate(username=email_id,password=password1)
                    auth.login(request, user)
                    return redirect('/')
            else:
                #print("1")
                messages.error(request,'Passwords did not match')
                return render(request,'Registration.html')        
    else: return render(request,'Registration.html')

# Universal Dashboard
def dashboard(request,username):
    return render(request, 'dashboard.html')

# activation of a new user account
def activation_user(request, uidb64, token):
    if request.method == 'GET':
        
        try:
            id = force_text(urlsafe_base64_decode(uidb64)) # decode this
            user = User.objects.get(pk=id)

            if user.is_registered: # show a message, already registered or smthn
                return redirect('/')
            
            user.is_registered = True
            user.save()
            
            # show a message or a "toast?" of sorts?
            return redirect(f'/{user.username}')

        except Exception as e:
            pass # what to do here?

    return redirect('/')

@login_required
def changePassword(request, username):
    if request.method == 'POST':
        if request.user.is_authenticated == AnonymousUser:
            pass
        else:
            user = request.user
            old_password = request.POST.get('old_password')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if user.check_password(old_password):
                if password1 == password2:
                    user.set_password(password1)
                    user.save()  
                    messages.success(request,'Password Changed Successfully')
                    
                    # relogin user, and redirect to profile
                    #auth.login(request, user)
                    #return redirect('/accounts/profile') 
                    return redirect('/')
                else:
                    messages.error(request,'Password did not match')
                    return render(request,'change_password.html')
            else:
                messages.error(request,"Old Password Didn't match")
                return render(request,'change_password.html')
    else: return render(request,'change_password.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

@login_required
def delete_user(request, username):
    user = request.user
    user.delete()
    
    return redirect('/')

@login_required
def report(request,username):
    return render(request,'report.html')

