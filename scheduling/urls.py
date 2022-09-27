from django import urls
from django.urls import path
from . import views

urlpatterns = [
    path('schedule/delete/<int:pk>/', views.delete_timeslot, name="delete_timeslot"),
    path('schedule/edit/<int:pk>/', views.edit_timeslot, name="edit_timeslot"),
    path('schedule/confirm/<int:pk>/', views.confirm_timeslot, name="confirm_timeslot"),
    path('schedule/decline/<int:pk>/', views.decline_timeslot, name="decline_timeslot"),
    path('schedule/cancel/<int:pk>/', views.cancel_timeslot, name="cancel_timeslot"),
    path('schedule/add/', views.add_timeslot, name="add_timeslot"),
]