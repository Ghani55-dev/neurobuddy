from django.urls import path
from . import views

urlpatterns = [
    path('connect-fitbit/', views.connect_fitbit, name='connect_fitbit'),
    path('fitbit/callback/', views.fitbit_callback, name='fitbit_callback'),
    path('chart-data/', views.wearable_chart_data, name='wearable_chart_data'),
    path('alerts/', views.emergency_alerts_view, name='emergency_alerts'),


]
