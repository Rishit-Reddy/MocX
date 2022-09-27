from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .forms import TimeSlotForm
from .models import InterviewerSchedule, IntervieweeSchedule
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils import timezone
import pytz
import datetime

    # TODO: security and checking
    # check if request.user is interviewee
    # check if user_requested is same as the username input in form
    # check if user_requested is interviewer as well
    # check if user_requested owns the schedule (check agaisnt time_slot.id or time_slot.user__name)
    # if all those pass, then go ahead and schedule
@login_required 
def add_schedule(request, user_requested): # adds a time slot from an interviewer (user_requested) to the interviewee's (request.user) schedule
    interviewer_id = int(request.POST['interviewer_id'])
    schedule_id = int(request.POST['schedule_id'])

    if user_requested.id == interviewer_id: # checking if same interviewer
        schedule_slot = InterviewerSchedule.objects.get(pk=schedule_id) # can use schedule_slot to do other modifications, such as change the status to pending

        # check if schedule_slot belongs to interviewer
        if user_requested.id != schedule_slot.interviewer.pk:
        # add a message, like does not exist or something
            messages.error(request, "An error occurred.")
            return False

        # if schedule slot was scheduled by another user, but no refresh has been done
        if schedule_slot.status != 'E':
            messages.error(request, "Using outdated session, so refreshed")
            return False
        
        # 1. get schedule slot start time, and end time.
        # 2. get all slots from interviewee
        # 3. see if schedule slot conflicts with any
        interviewee_slots = IntervieweeSchedule.objects.filter(interviewee_id=request.user.id)
        
        current_tz = pytz.timezone(request.user.user_timezone) # use the timzone of the interviewee
        starttime = timezone.localtime(schedule_slot.start_datetime, current_tz)
        endtime = timezone.localtime(schedule_slot.end_datetime, current_tz)


        # go through each slot and see if they conflict with the selected time slot
        for slot in interviewee_slots:
            slot_starttime = timezone.localtime(slot.interviewer_slot.start_datetime,  current_tz)
            slot_endtime = timezone.localtime(slot.interviewer_slot.end_datetime, current_tz)

            # this way, more comprehensive error signaling
            if slot_starttime < starttime and slot_endtime > starttime:
                messages.error(request, "Chosen time conflicts with already scheduled slot. Please select another time")
                return None
            elif slot_starttime < endtime and slot_endtime > endtime:
                messages.error(request, "Chosen time conflicts with already scheduled slot. Please select another time")
                return None
            elif slot_starttime > starttime and slot_endtime < endtime:
                messages.error(request, "Chosen time conflicts with already scheduled slot. Please select another time")
                return None
            elif slot_starttime == starttime and slot_endtime == endtime:
                messages.error(request, "Chosen time conflicts with already scheduled slot. Please select another time")
                return None

        # schedule if unique
        schedule_slot.change_to_tentative() # could just store a foreign instead?
        schedule_slot.interviewee_firstname = request.user.first_name
        schedule_slot.interviewee_lastname = request.user.last_name
        schedule_slot.interviewee_email = request.user.email
        schedule_slot.save()

        IntervieweeSchedule.objects.create(interviewee_id=request.user.id, interviewer_slot=schedule_slot, status=schedule_slot.status) # make this safer? check if interviewee exists?

        email_sub = f"Time slot booked by student"
        
        # change to interviewer timezone to convert times, as we send email to them        
        current_tz = current_tz = pytz.timezone(user_requested.user_timezone)
        startime = timezone.localtime(schedule_slot.start_datetime, current_tz)
        endtime = timezone.localtime(schedule_slot.end_datetime, current_tz)
    
        time_text = f"at {startime:%I:%M %p %Z } to {endtime:%I:%M %p %Z } on {startime:%d-%m-%Y}"
        email_bdy = f"Hello {schedule_slot.er__first_name}! {request.user.first_name} {request.user.last_name} has requested an interview with you {time_text}! Pending confirmation."

        # the email to be sent
        email = EmailMessage(
            email_sub,
            email_bdy,
            'noreply@mocx.in',
            [schedule_slot.er__emailid, 'headmocx09@gmail.com'] # send to their email
        )
        
        email.send(fail_silently=False)
    messages.info(request, "Successfully scheduled")
    #return redirect(f'/{user_requested}') # not ideal, but works here?


@login_required
def add_timeslot(request):
    if request.user.is_interviewee: # throw a 404 instead?
        return redirect('/')
    
    timezone.activate(request.user.user_timezone)
    
    if request.method == 'POST':       
        form = TimeSlotForm(request.POST, interviewer_id=request.user.id) # send data in here, send a certain attribute
        
        if form.is_valid():
            form_data = form.save(commit=False)
            # add a 30 minute interval onto start_datetime and save that as end_datetime
            form_data.end_datetime = form_data.start_datetime + datetime.timedelta(minutes=30)
            form_data.interviewer = request.user.interviewerprofile
            form_data.save()
            
            # messages.success(request, "Time slot added")
            timezone.deactivate()
            return redirect(f'/{request.user.username}')
    else:
        form = TimeSlotForm(interviewer_id=request.user.id)
    
    timezone.deactivate()
    return render(request, 'add_timeslot.html', { 'form' : form })


@login_required
def cancel_timeslot(request, pk): # cancel a timeslot, interviewee
    interviewee_timeslot = IntervieweeSchedule.objects.get(id=pk)
    if not request.user.is_interviewer:
        return redirect(f'/{request.user.username}')
    # check if request.user owns the timeslot
    if interviewee_timeslot.interviewee_id != request.user.id:
        # add a message, like does not exist or something
        return redirect(f'/{request.user.username}')
    if interviewee_timeslot.status != "T": # only tentative can be cancelled (For now)
        return redirect(f'/{request.user.username}')

    interviewer_timeslot = InterviewerSchedule.objects.get(id=interviewee_timeslot.interviewer_slot.id)
    email_id = interviewer_timeslot.interviewer.email__id
    interviewer_timeslot.change_to_empty()
    interviewee_timeslot.change_to_declined()
    interviewee_timeslot.delete() # send an email as well
    # get timeslot (interviewee schedule) from pk
    # get the interviewer schedule timeslot
    # set the ee_timeslot status to Declined
    # set the er_timeslot to empty
    # secutiry checking: user.request.pk is the pk given for interviewe
    email_sub = f"Time slot cancellation"
    current_tz = current_tz = pytz.timezone(interviewer_timeslot.interviewer.user__timezone)
    startime = timezone.localtime(interviewer_timeslot.start_datetime, current_tz)
    endtime = timezone.localtime(interviewer_timeslot.end_datetime, current_tz)
    time_text = f"at {startime:%I:%M %p %Z } to {endtime:%I:%M %p %Z } on {startime:%d-%m-%Y}"
    email_bdy = f"Hello Interviewer! Your booked interview with {interviewer_timeslot.interviewee_firstname} at {time_text} was cancelled! It is available for rescheduling!\n\nThank you!"
    
    # the email to be sent
    email = EmailMessage(
            email_sub,
            email_bdy,
            'noreply@mocx.in',
            [email_id, 'headmocx09@gmail.com'] # send to their email
    )
        
    email.send(fail_silently=False)

    
    
    return redirect(f'/{request.user.username}')
    

# send emails to all three, us, interviewer, interviewee  for confirm.
# send email to use, intervieweee when decline

@login_required
def confirm_timeslot(request, pk):
    timeslot = InterviewerSchedule.objects.get(id=pk)
    if not request.user.is_interviewer:
        return redirect(f'/{request.user.username}')
    # check if request.user owns the timeslot
    if timeslot.interviewer.pk != request.user.id:
        # add a message, like does not exist or something
        return redirect(f'/{request.user.username}')
    if timeslot.status != "T": # only tentative time slots can be confirmed
        return redirect(f'/{request.user.username}')
    
    interviewee_timeslot = IntervieweeSchedule.objects.get(interviewer_slot=timeslot) # get the interviewee timeslot
    
    # change the status to confirmed    
    timeslot.change_to_confirmed()
    interviewee_timeslot.change_to_confirmed()

    # get emails
    er_emailid = timeslot.interviewer.email__id
    ee_emailid = interviewee_timeslot.interviewee.email__id

    ee_current_tz = pytz.timezone(interviewee_timeslot.interviewee.user__timezone)
    ee_startime = timezone.localtime(timeslot.start_datetime, ee_current_tz)
    ee_endtime = timezone.localtime(timeslot.end_datetime, ee_current_tz)
    time_text_ee = f"at {ee_startime:%I:%M %p %Z } to {ee_endtime:%I:%M %p %Z } on {ee_startime:%d-%m-%Y}"
    
    er_current_tz = pytz.timezone(timeslot.interviewer.user__timezone)
    er_startime = timezone.localtime(timeslot.start_datetime, er_current_tz)
    er_endtime = timezone.localtime(timeslot.end_datetime, er_current_tz)
    time_text_er = f"at {er_startime:%I:%M %p %Z } to {er_endtime:%I:%M %p %Z } on {er_startime:%d-%m-%Y}"

    email_sub = f"Time slot confirmed"
    email_bdy_ee = f"Hello interviewee! Your booked interview with {timeslot.interviewer.first__name} {time_text_ee} is confirmed! \n\nThank you!"
    email_bdy_er = f"Hello interviewer! Your booked interview with {timeslot.interviewee_firstname} {time_text_er} is confirmed! \n\nThank you!"


    email_ee = EmailMessage(
            email_sub,
            email_bdy_ee,
            'noreply@mocx.in',
            [ee_emailid, 'headmocx09@gmail.com'] # send to their email
    )

    email_er = EmailMessage(
            email_sub,
            email_bdy_er,
            'noreply@mocx.in',
            [er_emailid, 'headmocx09@gmail.com'] # send to their email
    )

    email_ee.send(fail_silently=False)
    email_er.send(fail_silently=False)


    return redirect(f'/{request.user.username}')

@login_required
def decline_timeslot(request, pk): # interviewer declining booked timeslot
    timeslot = InterviewerSchedule.objects.get(id=pk)
    # check if request.user owns the timeslot
    if timeslot.interviewer.pk != request.user.id:
        # add a message, like does not exist or something
        return redirect(f'/{request.user.username}')
    if timeslot.status != "T": # only tentative timeslots can be declined
        return redirect(f'/{request.user.username}')
    
    interviewee_timeslot = IntervieweeSchedule.objects.get(interviewer_slot=timeslot) # get the interviewee timeslot

    # change the status to confirmed    
    current_tz = pytz.timezone(interviewee_timeslot.interviewee.user__timezone)
    startime = timezone.localtime(timeslot.start_datetime, current_tz)
    endtime = timezone.localtime(timeslot.end_datetime, current_tz)
    time_text = f"at {startime:%I:%M %p %Z } to {endtime:%I:%M %p %Z } on {startime:%d-%m-%Y}"

    # get emails
    ee_emailid = timeslot.interviewee_email
    interviewer_name = timeslot.interviewer.first__name

    timeslot.change_to_declined()
    interviewee_timeslot.change_to_declined()
    interviewee_timeslot.delete() # send an email first
    
    email_sub = f"Time slot cancellation"
    email_bdy = f"Hello interviewee! Your booked interview with {interviewer_name} {time_text} was declined!\nBut, you can still schedule with another interviewer.\n\nThank you!"

    timeslot.delete() # delete the declined timslot, since we don't use it

    # the email to be sent
    email = EmailMessage(
            email_sub,
            email_bdy,
            'noreply@mocx.in',
            [ee_emailid, 'headmocx09@gmail.com'] # send to their email
    )

    email.send(fail_silently=False)

    return redirect(f'/{request.user.username}')    

@login_required
def edit_timeslot(request, pk):
    timeslot = InterviewerSchedule.objects.get(id=pk)
    
    # check if request.user owns the timeslot
    if timeslot.interviewer.pk != request.user.id:
        # add a message, like does not exist or something
        return redirect(f'/{request.user.username}')

    if timeslot.status != "E":
        # show message, that can only edit timeslots that have not been booked
        return redirect(f'/{request.user.username}')
    
    timezone.activate(request.user.user_timezone)
    
    form = TimeSlotForm(instance=timeslot, timeslot_id=timeslot.id, interviewer_id=request.user.id)
    
    if request.method == 'POST':
        form = TimeSlotForm(request.POST, instance=timeslot, timeslot_id=timeslot.id, interviewer_id=request.user.id)
        
        if form.is_valid():
            form_data = form.save(commit=False)
            # add a 30 minute interval onto start_datetime and save that as end_datetime
            form_data.end_datetime = form_data.start_datetime + datetime.timedelta(minutes=30)
            form_data.save()
            
            timezone.deactivate()
            # messages.success(request, "Updates saved")
            return redirect(f'/{request.user.username}')

    timezone.deactivate()
    return render(request, 'edit_timeslot.html', { 'form' : form })

@login_required
def delete_timeslot(request, pk): # redirests to currentp age, uses a from
    timeslot = InterviewerSchedule.objects.get(id=pk)
    if timeslot.interviewer.pk != request.user.id:
        # add a message, like does not exist or something
        return redirect(f'/{request.user.username}')
    if timeslot.status != "E":
        # show message, that can only edit timeslots that have not been booked
        return redirect(f'/{request.user.username}')

    timeslot.delete()
    # add a message, that timeslot was deleted. An alert would be fine
    return redirect(f'/{request.user.username}')