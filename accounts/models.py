from django.db import models
from django.contrib.auth.models import AbstractUser
from django_resized import ResizedImageField
import pytz

class User(AbstractUser):
    TIMEZONE_CHOICES = [
        ('Asia/Kolkata', 'Asia/Kolkata [IST] [GMT + 05:30]' ),
        ('UTC', 'UTC, [GMT + 00:00]'),
    ]
    
    is_interviewee = models.BooleanField(default=False)
    is_interviewer = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=False)
    phone = models.CharField(max_length=10)
    country_code = models.PositiveSmallIntegerField(default=91)
    user_timezone = models.CharField(max_length=32, choices=TIMEZONE_CHOICES, default='Asia/Kolkata')

# when creating a new User with an Interviewer/Interviewee profile, use this: User.objects.create_user(username="er6@a.com", password="abc", is_interviewer/is_interviewee=True)
class InterviewerProfile(models.Model):
    EXP_CHOICES = [
        ("< 1yr", "Less than 1 Year"),
        ("1 - 2yr", "1 to 2 Years"),
        ("2 - 3yr", "2 to 3 Years"),
        ("3 - 4yr", "3 to 4 Years"),
        ("4 - 5yr", "4 to 5 Years"),
        ("5+ yr", "More than 5 Years")
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    # personal details
    about_me = models.TextField(max_length=200, default="Empty") # bio of sorts, shown on button thing and on profile
    education_details = models.TextField(max_length=100, default="Empty") 
    employment_details = models.TextField(max_length=100, default="Empty") # any English language related jobs, stuff like that
    mother_tongue = models.CharField(max_length=20, blank=True)
    # ielts details
    # certificate_details = models.CharField(max_length=100, default="Empty") # any certificate details. Won't be shown if empty
    taken_ielts = models.BooleanField(blank=False, default=False) 
    best_ielts_score = models.DecimalField(max_digits=2,decimal_places=1,default=0.0) # only shown if taken_ielts is True
    training_exp = models.CharField(max_length=15, choices=EXP_CHOICES, default="< 1yr") # multiple choice with year experiences? 0-1, 2-5, 5+? Need more info
    # social details
    # <a href="https://www.vecteezy.com/free-vector/social-icons">Social Icons Vectors by Vecteezy</a>
    linkedin_profile = models.URLField(max_length=60, blank=True) 
    twitter_profile = models.URLField(max_length=60, blank=True) 
    facebook_profile = models.URLField(max_length=60, blank=True)
    website_profile = models.URLField(max_length=60, blank=True) 
    insta_profile = models.URLField(max_length=60, blank=True) 

    # ratings = some sort of list? Or will this be a running average?
    # ratings_rated = no. of ratings?
    price = models.PositiveSmallIntegerField(default=0) # in Rupees, but how to change? Must add commision on top of this
    profile_image = ResizedImageField(default='default-avatar.jpg', size=[200,200], quality=100, crop=['middle', 'center'], upload_to='profile_pics')

    # useful properties for the model. use as if they were fields, i.e. interviewerprofile.country__code
    @property
    def user__timezone(self):
        return self.user.user_timezone

    @property # returns the phone no
    def phone__no(self):
        return self.user.phone

    @property # returns the country code
    def country__code(self):
        return self.user.country_code
    
    @property # returns the frist name
    def first__name(self):
        return self.user.first_name

    @property # returns the last name
    def last__name(self):
        return self.user.last_name

    @property
    def email__id(self):
        return self.user.email

    @property # returns the user name
    def user__name(self):
        return self.user.username
    
class IntervieweeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    tentative_field = models.CharField(max_length=50)
    
    # useful properties for the model, use as if they were a field i.e. intervieweeprofile.first__name, etc.
    @property
    def user__timezone(self):
        return self.user.user_timezone
    
    @property # get phone no from user
    def phone__no(self):
        return self.user.phone
    
    @property
    def email__id(self):
        return self.user.email

    @property # return country code 
    def country__code(self):
        return self.user.country_code

    @property # return first name
    def first__name(self):
        return self.user.first_name

    @property # retrun last name
    def last__name(self):
        return self.user.last_name

    @property # return username
    def user__name(self):
        return self.user.username
