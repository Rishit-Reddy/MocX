from django.forms import ModelForm, Textarea, CheckboxInput, NumberInput, Select, URLInput, ClearableFileInput, DecimalField
from .models import InterviewerProfile,User

class UserEditForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'user_timezone']
        
        widgets = {
            'user_timezone' : Select(attrs={'class': 'form-control'})
        }

# attrs={'class' : 'form-control' }
class InterviewerForm(ModelForm):
    best_ielts_score = DecimalField(max_value=9.0, min_value=0.0) # setting the range of values accepted as a score
    class Meta:
        model = InterviewerProfile
        exclude = ['user','twitter_profile','facebook_profile','twitter_profile','website_profile','insta_profile','education_details','employment_details']
        
        widgets = { # is there a way to for loop over these and set attrs that way?
            'about_me' : Textarea(attrs={'placeholder': 'Tell us about yourself...', 'class': 'form-control','rows': '3'}),
            'education_details' : Textarea(attrs={'placeholder': 'Tell us about your education...', 'class': 'form-control'}),
            'employment_details' : Textarea(attrs={'placeholder': 'Tell us about your employment...', 'class' : 'form-control'}),
            'taken_ielts' : CheckboxInput(attrs={'class' : 'form-check-input'}),
            'best_ielts_score' : NumberInput(attrs={'class' : 'form-control'}),
            'training_exp' : Select(attrs={'class' : 'form-control'}),
            'mother_tongue': Textarea(attrs={'class' : 'form-control','rows':'1'}),
            'linkedin_profile' : URLInput(attrs={'class' : 'form-control'}),
            'twitter_profile' : URLInput(attrs={'class' : 'form-control'}),
            'facebook_profile' : URLInput(attrs={'class' : 'form-control'}),
            'website_profile' : URLInput(attrs={'class' : 'form-control'}),
            'insta_profile' : URLInput(attrs={'class' : 'form-control'}),
            'price' : NumberInput(attrs={'class' : 'form-control'}),
            'profile_image' : ClearableFileInput(attrs={'class' : 'form-control'})
        }


