from django.shortcuts import render
from django.utils import timezone
from accounts.models import InterviewerProfile
from scheduling.models import InterviewerSchedule
from django.http import HttpResponse
from django.template.loader import render_to_string

def throw404(request, exception):
    return render(request, '404.html')

def index(request):
    if request.user.is_authenticated:
        interviewer_with_schedules = [] # a list containing a two item tuple, first one being an interviwerprofile, the second being a QuerySet of the interviewer's schedule slots
        interviewers = InterviewerProfile.objects.all() # This will really be bad without pagination
        
        # doing it here is the same as doing it individuallly to each profile, this way can put the code here, and 
        # not do anythign else to the code each time profile loads
        # can put a case in profile: Only recheck if it's the interviewer her/himself loading into it
        for interviewer in interviewers:
            # takes the first 4 of the most recent happening schedule_slots of the interviewer, and appends it to interviewer_with_schedules
            schedule_slots = InterviewerSchedule.objects.filter(interviewer_id=interviewer.pk)
            schedule_slots = schedule_slots.filter(status="E") # get empty slots
            schedule_slots = schedule_slots.order_by("start_datetime")[:4] # get the first 4

            if len(schedule_slots) > 0: # skips any interviewers who haven't added any slots yet.
                interviewer_with_schedules.append((interviewer, schedule_slots))

        
        content = { 
            'interviewers' : interviewer_with_schedules, # a list containing a tuples (interviewer object, querySet of his/her schedule_slots)
        }

        return render(request,'home.html', context=content)    
    elif not request.user.is_authenticated:
        return render(request,'landing.html')
    