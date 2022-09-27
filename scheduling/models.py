from django.db import models
from accounts.models import InterviewerProfile, IntervieweeProfile

class InterviewerSchedule(models.Model): # more accurate name, Interviwer Time Slot
    STATUSES = [
        ("E", "Empty"),
        ("T", "Tentative"),
        ("C", "Confirmed"),
        ("D", "Declined"),
    ]

    interviewer = models.ForeignKey(InterviewerProfile, on_delete=models.CASCADE, related_name='time_slot') #fk to interviewer who created this slot
    #interviewee info, why not use a foreign key?
    interviewee_firstname = models.CharField(max_length=50, default="") # TODO Make max name possible only 50 chars
    interviewee_lastname = models.CharField(max_length=50, default="" ) # here as well
    interviewee_email = models.CharField(max_length=50, default="") # TODO Same for usrname

    # for the time range, and for easier displaying. end_datetie can be calculated in view, with a interviewer_duration variable? The computation is done with a hard coded value
    start_datetime = models.DateTimeField(blank=False) 
    end_datetime = models.DateTimeField(blank=True)

    # interview_duration
    status = models.CharField(max_length=1, choices=STATUSES, default="E")    

    @property
    def er__username(self):
        return self.interviewer.user__name
    
    @property 
    def er__first_name(self):
        return self.interviewer.first__name

    @property
    def er__last_name(self):
        return self.interviewer.last__name
    
    @property
    def er__emailid(self):
        return self.interviewer.email__id


    # status changing methods
    # Change to Empty again 
    def change_to_empty(self):
        self.status = "E"
        self.interviewee_firstname = ""
        self.interviewee_lastname = ""
        self.interviewee_email = ""
        self.save()
    
    # Change to Tentative
    def change_to_tentative(self):
        self.status = "T"
        self.save()
    
    # Change to Confirmed
    def change_to_confirmed(self):
        self.status = "C"
        self.save()

    # Change to Declined
    def change_to_declined(self):
        self.status = "D"
        self.save()

class IntervieweeSchedule(models.Model):
    STATUSES = {
        ("T","Tentative"),
        ("C", "Confirmed"),
        ("D", "Declined"),
    }

    interviewee = models.ForeignKey(IntervieweeProfile, on_delete=models.CASCADE, related_name='interviewee_id')
    interviewer_slot = models.OneToOneField(InterviewerSchedule, on_delete=models.CASCADE) # MAKING THIS THE PRIMARY KEY COULD REALLY SPEED THINGS UP
    
    status = models.CharField(max_length=1, choices=STATUSES, default="T") # local status, uses interviewer's schedule status to update. why not just use that via fk?

    @property
    def interviewer__username(self):
        return self.interviewer_slot.er__username
    
    @property
    def interviewer__firstname(self):
        return self.interviewer_slot.er__first_name

    @property
    def interviewer__lastname(self):
        return self.interviewer_slot.er__last_name


    @property
    def start__time(self):
        return self.interviewer_slot.start_datetime

    # Change to Confirmed
    def change_to_confirmed(self):
        self.status = "C"
        self.save()

    # Change to Declined
    def change_to_declined(self):
        self.status = "D"
        self.save()