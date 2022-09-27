from django.forms import ModelForm, DateTimeInput, DateTimeField
from django.core.exceptions import ValidationError
from .models import InterviewerSchedule
from django.utils import timezone
import datetime

class TimeSlotForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.interviewer_id = kwargs.pop('interviewer_id')
        self.timeslot_id = kwargs.pop('timeslot_id', -1) # a -1 should be impossible
        super(TimeSlotForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean() 
        now = timezone.localtime(timezone.now(), timezone.get_current_timezone()) # user self.user_timezone instead
        
        starttime = cleaned_data['start_datetime']
        endtime = starttime + datetime.timedelta(minutes=30)
        
        if starttime < now: # trying to start an interview before now, no
            raise ValidationError("Please select a future date to add slot...")
        
        # 1. get startime, endtime for new slot
        # 2. get all the interviewer time slots
        # how do to #2? It seems more involved, as if it takes more steps
        # 3. run the comparison and throw proper validation errors. 
        # TODO: Figure out a better primary key method, or see how to optimize db for searching. think about this when builldng new mocx
        # Possible to refactor? Directly set the interviewer profile via argument?
        interviewer_slots = InterviewerSchedule.objects.filter(interviewer_id=self.interviewer_id)

        # go through each slot and see if they conflict with the selected time slot
        for slot in interviewer_slots:
            # convert slots into local timezone
            slot_starttime = timezone.localtime(slot.start_datetime, timezone.get_current_timezone())
            slot_endtime = timezone.localtime(slot.end_datetime, timezone.get_current_timezone())
            
            if self.timeslot_id == slot.id:
                continue # skips checking with same timeslot

            # this way, more comprehensive error signaling
            if slot_starttime < starttime and slot_endtime > starttime:
                raise ValidationError(f"Chosen time conflicts with {slot_starttime:%I:%M %p %Z} to {slot_endtime:%I:%M %p %Z}. i.e. will start in the middle.")
            elif slot_starttime < endtime and slot_endtime > endtime:
                raise ValidationError(f"Chosen time conflicts with {slot_starttime:%I:%M %p %Z} to {slot_endtime:%I:%M %p %Z}.  i.e. will end in the middle.")
            elif slot_starttime > starttime and slot_endtime < endtime:
                raise ValidationError(f"Chosen time conflicts with {slot_starttime:%I:%M %p %Z} to {slot_endtime:%I:%M %p %Z}") # I wonder if this will ever happen?
            elif slot_starttime == starttime and slot_endtime == endtime:
                raise ValidationError(f"There is already a time slot with same time on the same date: {slot_starttime:%I:%M %p %Z} to {slot_endtime:%I:%M %p %Z}")

    class Meta:
        model = InterviewerSchedule
        exclude = ['interviewer', 'status', 'interviewee_firstname', 'interviewee_lastname', 'interviewee_email', 'end_datetime' ]
        widgets = {
            'start_datetime' : DateTimeInput(attrs={'class' : 'form-control','type':'datetime-local'}),
        }