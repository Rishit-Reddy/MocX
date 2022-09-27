from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

class AppTokenGenerator(PasswordResetTokenGenerator): 
    
    def _make_hash_value(self, user, timestamp): # this method runs when creating a token
        return (text_type(user.is_registered)+text_type(user.pk)+text_type(timestamp))

activation_token_generator = AppTokenGenerator()