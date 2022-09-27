from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('login_register',views.login_register,name='login_register'),
    path('login/',views.user_login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('register',views.interviewee_register,name='register'),
    path('examiner_register',views.interviewer_register,name='examiner_register'),
    path('activation/<uidb64>/<token>', views.activation_user, name='activation_user'),
    path('password-reset/',auth_views.PasswordResetView.as_view(template_name='password_reset.html'),name='password_reset'),
    path('password-reset/done',auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),name='password_reset_done'),
    path('password-reset/complete/',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),name='password_reset_complete'),
    path('password-reset/confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),name='password_reset_confirm'),
    path('<username>/',views.profile_user,name='profile'),
    path('<username>/dashboard',views.dashboard,name='dashboard'),
    path('<username>/report',views.report,name='report'),
    path('settings/edit-profile',views.edit_profile,name='edit_profile'),
    path('settings/edit-my-profile',views.edit_user_profile,name='edit_user_profile'),
    path('<username>/Change_Password',views.changePassword,name='Change_Password'),
    path('<username>/delete_user',views.delete_user,name='delete_user'),
    
]