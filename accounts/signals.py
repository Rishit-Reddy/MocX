from django.db.models.signals import post_save
from accounts.models import User, InterviewerProfile, IntervieweeProfile
from django.dispatch import receiver

# creates the correct Profile when a new User is created
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_interviewer and not instance.is_interviewee: # if the user is an interviewer
            # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#create
            InterviewerProfile.objects.create(user=instance)
        elif instance.is_interviewee and not instance.is_interviewer: # if the user is an interviewee
            IntervieweeProfile.objects.create(user=instance)

# save signal
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if instance.is_interviewer and not instance.is_interviewee:
        instance.interviewerprofile.save()
    elif instance.is_interviewee and not instance.is_interviewer:
        instance.intervieweeprofile.save()